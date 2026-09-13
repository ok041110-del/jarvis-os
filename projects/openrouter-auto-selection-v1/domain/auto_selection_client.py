"""OpenRouter Free Auto Selection Client — `models`(공식 fallback 배열 파라미터, 실측 확인: `models: [...]` 필드, `docs/guides/routing/ model-fallbacks.md`)를 그대로 사용한다. `model="openrouter/auto"`는 실측(HTTP 402 "Insufficient credits")과 공식 문서("표준 요금 부과, free 전용 아님") 둘 다로 **무료 티어에서 지원되지 않음**을 확인했다 — 이 Client는 그 방식을 쓰지 않는다(§Governance Boundary 재확인, Evidence 문서 §5 참조).

API Key/Credential은 이 파일이 탐색·설정하지 않는다 — 이 세션 Egress Proxy의 자동 인증 주입에만 의존한다(Authorization 헤더 미설정).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"

FailureClass = str  # "http_429" | "http_5xx" | "timeout" | "malformed_output" | "contract_failure" | "empty_response" | "connection_error"

# 재시도 가능 여부 표(사용자 지시 §6) — Contract failure/malformed output도
# 재시도 가능하나, 재시도 시 실패 모델을 Pool에서 제외한다.
_RETRYABLE_FAILURE_CLASSES = frozenset(
    {"http_429", "http_5xx", "timeout", "malformed_output", "empty_response", "contract_failure"}
)
_NON_RETRYABLE_FAILURE_CLASSES = frozenset({"connection_error"})  # 네트워크 자체 불가 — 재시도해도 동일하게 실패할 근거


@dataclass
class AutoSelectionAttempt:
    attempt_number: int
    models_offered: tuple[str, ...]
    http_status: Optional[int]
    selected_model: Optional[str]
    raw_content: Optional[str]
    usage: Optional[dict]
    api_latency_ms: Optional[float]
    failure_class: Optional[FailureClass]
    error_detail: Optional[str]
    contract_passed: Optional[bool]
    contract_detail: Optional[dict]


@dataclass
class AutoSelectionResult:
    stage: str
    success: bool
    final_selected_model: Optional[str]
    total_latency_ms: float
    retry_count: int
    attempts: list = field(default_factory=list)
    final_contract_passed: Optional[bool] = None
    final_raw_content: Optional[str] = None


def _single_call(models_offered: tuple[str, ...], prompt: str, *, max_tokens: int, timeout: int) -> dict:
    """1회 HTTP 호출. 예외를 던지지 않고 전부 구조화된 dict로 반환한다 —
    호출자가 `classify_failure()`로 재시도 여부를 판단한다."""
    body = json.dumps(
        {"models": list(models_offered), "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.2}
    ).encode("utf-8")
    request = urllib.request.Request(
        OPENROUTER_CHAT_COMPLETIONS_URL, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler())
    start = time.perf_counter()
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "http_status": None,
            "elapsed_ms": (time.perf_counter() - start) * 1000,
            "error": f"connection failed: {exc}",
            "parsed": None,
        }
    elapsed_ms = (time.perf_counter() - start) * 1000

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        return {"http_status": status, "elapsed_ms": elapsed_ms, "error": f"non-JSON response: {exc}", "parsed": None}

    return {"http_status": status, "elapsed_ms": elapsed_ms, "error": None, "parsed": parsed}


def _record_attempt(
    attempts: list[AutoSelectionAttempt],
    *,
    attempt_number: int,
    models_offered: tuple[str, ...],
    call_result: dict,
    selected_model: Optional[str] = None,
    raw_content: Optional[str] = None,
    usage: Optional[dict] = None,
    failure_class: Optional[FailureClass] = None,
    error_detail: Optional[str] = None,
    contract_passed: Optional[bool] = None,
    contract_detail: Optional[dict] = None,
) -> None:
    """이번 시도의 결과를 `AutoSelectionAttempt`로 기록해 `attempts`에 추가한다."""
    attempts.append(
        AutoSelectionAttempt(
            attempt_number=attempt_number,
            models_offered=models_offered,
            http_status=call_result.get("http_status"),
            selected_model=selected_model,
            raw_content=raw_content,
            usage=usage,
            api_latency_ms=call_result.get("elapsed_ms"),
            failure_class=failure_class,
            error_detail=error_detail,
            contract_passed=contract_passed,
            contract_detail=contract_detail,
        )
    )


def _exclude_model_if_configured(pool: tuple[str, ...], model: Optional[str], exclude: bool) -> tuple[str, ...]:
    """실패한 `model`을 다음 재시도 Pool에서 제외한다(`exclude`가 True이고 Pool에 있을 때만)."""
    if exclude and model in pool:
        return tuple(m for m in pool if m != model)
    return pool


def classify_failure(call_result: dict) -> Optional[FailureClass]:
    """호출 1회 결과를 실패 유형으로 분류한다. 성공(재시도 불필요)이면
    `None`을 반환한다."""
    if call_result.get("error") and call_result.get("http_status") is None:
        return "connection_error"
    status = call_result.get("http_status")
    if status == 429:
        return "http_429"
    if status is not None and status >= 500:
        return "http_5xx"
    if status is not None and status >= 400:
        return "malformed_output"  # 4xx(429 제외) — OpenRouter가 모든 candidate에서 실패했다는 응답
    return None  # HTTP 200 — 내용 유효성은 별도로 판단(빈 응답/Contract는 호출부가 확인)


def call_with_auto_selection(
    stage: str,
    prompt: str,
    models_pool: tuple[str, ...],
    *,
    output_contract,
    max_tokens: int,
    timeout: int,
    max_retries: int = 1,
    exclude_failed_model_from_retry_pool: bool = True,
) -> AutoSelectionResult:
    """`models` 배열을 그대로 OpenRouter에 넘기고(자체 순위화 없음), HTTP/malformed/empty/Contract 실패를 구분해 최대 `max_retries`회만 재시도한다. Contract 판정은 호출자가 넘긴 기존 parser/validator (`output_contract`)를 그대로 쓴다 — 이 함수는 Contract 판정 로직을 갖지 않는다(새 LLM judge 없음, 사용자 지시 §5)."""
    attempts: list[AutoSelectionAttempt] = []
    current_pool = models_pool
    overall_start = time.perf_counter()

    for attempt_number in range(1, max_retries + 2):
        call_result = _single_call(current_pool, prompt, max_tokens=max_tokens, timeout=timeout)
        failure_class = classify_failure(call_result)

        if failure_class is not None:
            _record_attempt(
                attempts,
                attempt_number=attempt_number,
                models_offered=current_pool,
                call_result=call_result,
                failure_class=failure_class,
                error_detail=call_result.get("error") or json.dumps(call_result.get("parsed"))[:300],
            )
            if failure_class in _NON_RETRYABLE_FAILURE_CLASSES or attempt_number > max_retries:
                break
            continue

        parsed = call_result["parsed"]
        selected_model = parsed.get("model")
        usage = parsed.get("usage")
        try:
            content = parsed["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            content = None

        if not content:
            _record_attempt(
                attempts,
                attempt_number=attempt_number,
                models_offered=current_pool,
                call_result=call_result,
                selected_model=selected_model,
                usage=usage,
                failure_class="empty_response",
                error_detail=f"finish_reason={parsed.get('choices', [{}])[0].get('finish_reason')}",
            )
            current_pool = _exclude_model_if_configured(current_pool, selected_model, exclude_failed_model_from_retry_pool)
            if attempt_number > max_retries or not current_pool:
                break
            continue

        contract_result = output_contract(content)
        if not contract_result.passed:
            _record_attempt(
                attempts,
                attempt_number=attempt_number,
                models_offered=current_pool,
                call_result=call_result,
                selected_model=selected_model,
                raw_content=content,
                usage=usage,
                failure_class="contract_failure",
                contract_passed=False,
                contract_detail=contract_result.detail,
            )
            current_pool = _exclude_model_if_configured(current_pool, selected_model, exclude_failed_model_from_retry_pool)
            if attempt_number > max_retries or not current_pool:
                break
            continue

        # 성공
        _record_attempt(
            attempts,
            attempt_number=attempt_number,
            models_offered=current_pool,
            call_result=call_result,
            selected_model=selected_model,
            raw_content=content,
            usage=usage,
            contract_passed=True,
            contract_detail=contract_result.detail,
        )
        total_ms = (time.perf_counter() - overall_start) * 1000
        return AutoSelectionResult(
            stage=stage,
            success=True,
            final_selected_model=selected_model,
            total_latency_ms=total_ms,
            retry_count=attempt_number - 1,
            attempts=attempts,
            final_contract_passed=True,
            final_raw_content=content,
        )

    total_ms = (time.perf_counter() - overall_start) * 1000
    last = attempts[-1] if attempts else None
    return AutoSelectionResult(
        stage=stage,
        success=False,
        final_selected_model=last.selected_model if last else None,
        total_latency_ms=total_ms,
        retry_count=max(0, len(attempts) - 1),
        attempts=attempts,
        final_contract_passed=last.contract_passed if last else None,
        final_raw_content=last.raw_content if last else None,
    )

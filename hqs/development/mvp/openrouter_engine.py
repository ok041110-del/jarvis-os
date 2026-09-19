"""OpenRouter Engine 호출 — Multi-Engine Architecture의 3번째 Engine(`ADR-0027`, `RFC-0041`). `call_engine()`/`call_engine_via_chatgpt()`와 동일한 외부 계약(`str -> str`, 실패 시 `RuntimeError`)을 따르며, Free Model Pool 조회 → Deterministic Filter → 최대 3개 candidate 선정까지만 수행하고 실제 모델 선택/재시도 판정은 OpenRouter에 위임한다(`ADR-0026` §7) — 모델 품질 추정·우선순위· Stage별 모델 고정은 명시적으로 배제한다.

**선(先) 배선 상태**: `ADR-0027` §10 Deviation으로 사용자가 명시적으로 승인한 배선이며, Validation Gate 검증 완료 전까지 Production 신뢰성(quota/latency/model quality)은 검증된 것으로 간주하지 않는다(상세: `docs/research/OPENROUTER-PRODUCTION-ENGINE-MIGRATION-IMPLEMENTATION-0001.md`)."""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request

OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai"
OPENROUTER_MODELS_PATH = "/api/v1/models"
OPENROUTER_CHAT_COMPLETIONS_PATH = "/api/v1/chat/completions"
OPENROUTER_DEFAULT_TIMEOUT_SECONDS = 90

# `models[]` 배열의 실측 상한 — `OPENROUTER-MODELS-ARRAY-LIMIT-
# REVERIFICATION-0001.md` §6이 재현한 API-level limit이다(추정 아님).
MAX_CANDIDATES = 3

# 모든 Stage 공통 상한 — Stage별 값을 두지 않는다(RFC-0041 §Migration
# Boundary와의 일관성). 실제 요구 context는 매 호출마다 동적으로 추정한다.
_DEFAULT_OUTPUT_TOKEN_BUDGET = 2048
_CONTEXT_SAFETY_MARGIN = 1.2

# 실측 확인된, plain chat completion이 구조적으로 불가능한 모델(agentic
# harness 전용, OpenRouter 자체 403) — `OPENROUTER-STAGE-MODEL-SELECTION-0001.md` §2와 동일 근거.
_KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT = frozenset(
    {
        "thinkingmachines/inkling:free",
        "thinkingmachines/inkling-small:free",
    }
)


class OpenRouterEngineConfigError(RuntimeError):
    pass


def _resolve_base_url() -> str:
    return os.environ.get("OPENROUTER_BASE_URL", OPENROUTER_DEFAULT_BASE_URL).rstrip("/")


def _build_opener() -> urllib.request.OpenerDirector:
    # 매 호출마다 opener를 새로 만든다 — `chatgpt_engine.py`와 동일한 이유
    # (전역 opener의 캐싱된 proxy 설정이 이후 변경을 반영 못함).
    return urllib.request.build_opener(urllib.request.ProxyHandler())


def _auth_headers() -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def _fetch_free_model_pool(timeout: float) -> list[dict]:
    """`:free`로 끝나는 모델을 OpenRouter가 반환한 순서 그대로 가져온다 — 재정렬·순위화 없음. 이 순서 자체가 나중에 3개 초과 시 tie-break 근거가 된다."""
    url = _resolve_base_url() + OPENROUTER_MODELS_PATH
    request = urllib.request.Request(url, method="GET", headers=_auth_headers())
    try:
        with _build_opener().open(request, timeout=timeout) as response:
            raw = response.read()
    except (urllib.error.URLError, socket.timeout, OSError) as exc:
        raise OpenRouterEngineConfigError(f"OpenRouter free model pool 조회 실패: {exc}") from exc

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise OpenRouterEngineConfigError(f"OpenRouter free model pool 응답이 JSON이 아니다: {exc}") from exc

    return [m for m in parsed.get("data", []) if m.get("id", "").endswith(":free")]


def _estimate_min_context_tokens(prompt: str) -> int:
    """정확한 tokenizer 없이(모델마다 다르고 사전에 알 수 없음) 문자
    수/4를 보수적 근사치로 쓴다 — 추정치임을 숨기지 않는다."""
    input_tokens_estimate = len(prompt) // 4
    return int((input_tokens_estimate + _DEFAULT_OUTPUT_TOKEN_BUDGET) * _CONTEXT_SAFETY_MARGIN)


def _deterministic_filter(pool: list[dict], min_context_tokens: int) -> list[str]:
    """`ADR-0026` §6 Hard Filter — free 여부(Pool 자체가 이미 보장)/ 알려진 비기능 모델 제외/context 길이/modality(text 입출력)만으로 판정한다. 판정 불가능한 항목(예: Contract compatibility)은 추측 하지 않고 그냥 통과시킨다 — 제외 사유로 쓰지 않는다."""
    kept = []
    for model in pool:
        model_id = model.get("id", "")
        if model_id in _KNOWN_NONFUNCTIONAL_FOR_PLAIN_CHAT:
            continue

        context_length = model.get("context_length")
        if context_length is not None and context_length < min_context_tokens:
            continue

        architecture = model.get("architecture") or {}
        input_modalities = architecture.get("input_modalities") or []
        output_modalities = architecture.get("output_modalities") or []
        if input_modalities and "text" not in input_modalities:
            continue
        if output_modalities and "text" not in output_modalities:
            continue

        kept.append(model_id)
    return kept


def _select_candidates(kept_model_ids: list[str]) -> tuple[str, ...]:
    """3개 초과 시 순위화 없이 Pool 응답 순서 그대로 앞에서부터 자른다 (`RFC-0040`/`RFC-0041` §Candidate Selection Boundary의 deterministic tie-break)."""
    return tuple(kept_model_ids[:MAX_CANDIDATES])


def _parse_chat_response(status: int, body_bytes: bytes) -> tuple[str | None, str | None]:
    """(content, selected_model) 튜플을 반환하거나, 재시도 불가능한 오류면 `RuntimeError`를 raise한다. 429/5xx/4xx는 호출부가 재시도 분류에 쓸 수 있도록 여기서 바로 raise하지 않고 `None, None`을 반환한다 — 호출부(`call_engine_via_openrouter`)가 실패 분류와 bounded retry를 담당한다."""
    try:
        parsed = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except (ValueError, UnicodeDecodeError):
        parsed = None
    if parsed is None:
        return None, None
    if status >= 400:
        return None, None

    selected_model = parsed.get("model")
    try:
        content = parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None, selected_model
    return (content or None), selected_model


def _classify_failure(status: int | None, connection_error: bool) -> str:
    """quota(429)를 모델 품질 실패와 분리해서 분류한다 — quota 실패를 "이 모델이 나쁘다"는 신호로 취급하지 않는다(`ADR-0027` §Retry Boundary)."""
    if connection_error:
        return "connection_error"
    if status == 429:
        return "429_quota"
    if status is not None and status >= 500:
        return "5xx"
    if status is not None and status >= 400:
        return "malformed_response"
    return "empty_response"


def _single_chat_call(candidate_ids: tuple[str, ...], prompt: str, timeout: float) -> dict:
    url = _resolve_base_url() + OPENROUTER_CHAT_COMPLETIONS_PATH
    body = json.dumps(
        {
            "models": list(candidate_ids),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": _DEFAULT_OUTPUT_TOKEN_BUDGET,
        }
    ).encode("utf-8")
    headers = {"Content-Type": "application/json", **_auth_headers()}
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with _build_opener().open(request, timeout=timeout) as response:
            content, selected_model = _parse_chat_response(response.status, response.read())
            return {
                "content": content,
                "selected_model": selected_model,
                "http_status": response.status,
                "connection_error": False,
            }
    except urllib.error.HTTPError as exc:
        content, selected_model = _parse_chat_response(exc.code, exc.read())
        return {"content": content, "selected_model": selected_model, "http_status": exc.code, "connection_error": False}
    except socket.timeout:
        return {"content": None, "selected_model": None, "http_status": None, "connection_error": True}
    except urllib.error.URLError:
        return {"content": None, "selected_model": None, "http_status": None, "connection_error": True}
    except OSError:
        return {"content": None, "selected_model": None, "http_status": None, "connection_error": True}


def call_engine_via_openrouter(prompt: str) -> str:
    """단일 OpenRouter 호출 지점. 실패 시 bounded retry(최대 1회, 실패 후보 제외)를 수행한다. quota(429)는 계정 단위 제약이라 모델 교체로 회복되지 않을 수 있지만, 다른 원인의 일시적 실패 가능성을 배제하지 않기 위해 재시도 자체는 수행한다."""
    timeout = float(os.environ.get("OPENROUTER_TIMEOUT_SECONDS", OPENROUTER_DEFAULT_TIMEOUT_SECONDS))

    pool = _fetch_free_model_pool(timeout)
    min_context = _estimate_min_context_tokens(prompt)
    kept = _deterministic_filter(pool, min_context)
    candidates = _select_candidates(kept)

    if not candidates:
        raise RuntimeError(
            "OpenRouter Deterministic Filter 통과 후보가 0개다 "
            f"(Pool 크기={len(pool)}, 요구 context 추정치={min_context})"
        )

    last_failure_category = None
    attempts = []  # 내부 진단 전용(str/RuntimeError 외부 계약 무변경, 실패 시 예외 속성으로만 노출)
    for attempt in range(2):  # 최초 1회 + bounded retry 최대 1회
        result = _single_chat_call(candidates, prompt, timeout)
        if result["content"]:
            return result["content"]

        last_failure_category = _classify_failure(result["http_status"], result["connection_error"])
        attempts.append(
            {
                "attempt": attempt + 1,
                "http_status": result["http_status"],
                "requested_candidates": candidates,
                "selected_model": result.get("selected_model"),
                "category": last_failure_category,
                "connection_error": result["connection_error"],
            }
        )

        failed_model = result.get("selected_model")
        if failed_model and failed_model in candidates:
            candidates = tuple(c for c in candidates if c != failed_model)
        if not candidates:
            break

    error = RuntimeError(
        f"OpenRouter call failed after retry (category={last_failure_category}, "
        f"candidates_tried={len(candidates) or 'exhausted'})"
    )
    # 진단 정보는 예외 메시지(외부 계약)를 바꾸지 않고 속성으로만 첨부한다 —
    # response body/헤더/API Key/프롬프트는 포함하지 않는다(RFC-0041 §Security Boundary).
    error.attempts = tuple(attempts)
    raise error

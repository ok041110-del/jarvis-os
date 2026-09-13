"""Stage 05 Actual Implementation Revalidation — ADR-0026 경로(Free
Pool → Deterministic Filter → Candidate Selection(≤3) → `models[]` →
OpenRouter → 실제 selected model → Stage 05 Review)를 **실제 Stage 04
Implementation**으로 재검증한다.

범위(사용자 지시):
- Stage 01~04는 재실행하지 않는다 — `domain/stage05_actual_implementation_
  fixture.py`가 이 세션이 이전에 실제로 실행해 성공시킨 Stage 04 결과를
  동결해 재사용한다.
- Stage 05만 실행한다.
- 기존 Stage 05 Architecture/Production 코드는 변경하지 않는다.
- API Key/Authorization 값은 출력하지 않는다(Egress Proxy 자동 인증만
  사용, 이 파일 어디에도 Authorization 헤더 설정 없음).
- 실제 코드 전체를 로그로 출력하지 않는다(길이/존재 여부만).
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain._sibling_import import load_sibling_domain  # noqa: E402
from domain._sibling_import_stage05_harness import load_sibling_stage05_harness_domain  # noqa: E402
from domain.candidate_selection import select_candidates  # noqa: E402
from domain.deterministic_filter import apply_deterministic_filter  # noqa: E402
from domain.free_pool import fetch_free_pool  # noqa: E402
from domain.stage05_actual_implementation_fixture import (  # noqa: E402
    ACTUAL_STAGE04_IMPLEMENTATION,
    ACTUAL_STAGE04_IMPLEMENTATION_PROVENANCE,
    ACTUAL_STAGE04_TARGET_FUNCTION,
    ACTUAL_STAGE04_TARGET_MODULE,
)
from domain.stage05_deterministic_comparison import run_deterministic_comparison  # noqa: E402
from domain.stage_requirements import build_stage_requirements  # noqa: E402

_sibling_auto = load_sibling_domain()
call_with_auto_selection = _sibling_auto.auto_selection_client.call_with_auto_selection
stage05_review_contract = _sibling_auto.contracts.stage05_review_contract

_sibling_stage05 = load_sibling_stage05_harness_domain()
_import_lines = _sibling_stage05.validators._import_lines

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_COUNT = 3

_STAGE04_DESIGN_TEXT = (
    "Add input validation to backend_agent_code_review: if `code` is not a "
    "non-empty string (after stripping whitespace), raise `ValueError` with a "
    "clear message before calling the Engine. Keep the existing review "
    "instruction and function behavior otherwise unchanged. Update the "
    "function's docstring to mention the new validation."
)


def _build_review_prompt_with_actual_implementation(original_source: str) -> str:
    """ADR-0025/RFC-0039 §9가 확정한 Review Input 경계(Design/Contract/
    Scope/Immutable Source Snapshot + **실제 Implementation**)를 그대로
    따르되, 이전 실험의 결함(placeholder)을 제거하고 §Implementation
    자리에 `ACTUAL_STAGE04_IMPLEMENTATION`을 실제로 삽입한다."""
    instruction = (
        "You are the Review capability of a validation pipeline. Review the "
        "following code and describe issues in prose (bugs, risks, style) — "
        "do not rewrite or restate the code as your answer. A real issue is "
        "a concrete defect that would cause wrong output, a crash, or a "
        "violation of the function's own stated behavior."
    )
    contract_description = (
        "External Contract: the reviewed function must remain `str -> str`, "
        "with failures surfaced as a single exception type."
    )
    scope_description = f"Scope Context (files this change is allowed to touch): {ACTUAL_STAGE04_TARGET_MODULE}"
    return (
        f"{instruction}\n\n---STAGE 03 DESIGN---\n{_STAGE04_DESIGN_TEXT}\n\n"
        f"---CONTRACT---\n{contract_description}\n\n---SCOPE CONTEXT---\n{scope_description}\n\n"
        f"---IMMUTABLE SOURCE SNAPSHOT---\n{original_source}\n\n"
        f"---STAGE 04 IMPLEMENTATION (actual, real Stage 04 output — NOT placeholder)---\n"
        f"{ACTUAL_STAGE04_IMPLEMENTATION}"
    )


def _classify_error_detail(error_detail: str | None, http_status: int | None) -> str:
    """`auto_selection_client.classify_failure()`는 timeout/connection을
    함께 `connection_error`로 묶는다(기존 구현 무수정 원칙 — 이 함수를
    고치지 않는다). 이 실험이 요구하는 세분류(429/5xx/timeout/malformed/
    contract_failure)를 얻기 위해, 이미 반환된 `error_detail` 문자열만
    보고 사후에 한 단계 더 나눈다(재현 가능한 문자열 매칭, 추측 아님)."""
    if http_status == 429:
        return "429_quota"
    if http_status is not None and http_status >= 500:
        return "5xx"
    if error_detail and "timeout" in error_detail.lower():
        return "timeout"
    if error_detail and ("connection failed" in error_detail or "urlerror" in error_detail.lower()):
        return "connection_error"
    if http_status is not None and 400 <= http_status < 500:
        return "malformed_response"
    return "unknown"


def main() -> dict:
    print("=== Stage 05 Actual Implementation Revalidation — Pre-checks ===", file=sys.stderr)

    implementation_exists = bool(ACTUAL_STAGE04_IMPLEMENTATION and ACTUAL_STAGE04_IMPLEMENTATION.strip())
    implementation_length = len(ACTUAL_STAGE04_IMPLEMENTATION)
    print(f"Stage 04 implementation 존재 여부: {implementation_exists}", file=sys.stderr)
    print(f"implementation 길이: {implementation_length} chars", file=sys.stderr)
    print(f"대상 module: {ACTUAL_STAGE04_TARGET_MODULE}", file=sys.stderr)
    print(f"대상 function: {ACTUAL_STAGE04_TARGET_FUNCTION}", file=sys.stderr)
    print(f"출처(provenance): {ACTUAL_STAGE04_IMPLEMENTATION_PROVENANCE}", file=sys.stderr)

    original_source = (REPO_ROOT / ACTUAL_STAGE04_TARGET_MODULE).read_text(encoding="utf-8")
    prompt = _build_review_prompt_with_actual_implementation(original_source)

    # 실제 코드 전체를 로그로 출력하지 않는다 — 포함 여부만 문자열 포함 검사로 확인.
    prompt_contains_actual_implementation = ACTUAL_STAGE04_IMPLEMENTATION in prompt
    prompt_contains_placeholder_marker = "same implementation validated in the Stage 04 run" in prompt
    print(f"Review prompt에 실제 implementation 포함 여부: {prompt_contains_actual_implementation}", file=sys.stderr)
    print(f"Review prompt에 이전 placeholder 문구 포함 여부(있으면 결함 재발): {prompt_contains_placeholder_marker}", file=sys.stderr)
    print(f"prompt 총 길이: {len(prompt)} chars (실제 코드 본문은 출력하지 않음)", file=sys.stderr)

    if not prompt_contains_actual_implementation or prompt_contains_placeholder_marker:
        raise RuntimeError(
            "Review prompt에 실제 Stage04 Implementation이 없거나 placeholder가 섞여 있다 — "
            "실행을 중단한다(품질 결함을 그대로 진행시키지 않음)."
        )

    # --- 기존 deterministic validation과 비교할 기준선(AST/Dependency) ---
    original_import_lines = _import_lines(original_source)
    deterministic = run_deterministic_comparison(
        original_source_snapshot=original_source,
        implementation=ACTUAL_STAGE04_IMPLEMENTATION,
        target_function_name=ACTUAL_STAGE04_TARGET_FUNCTION,
        target_relative_path=ACTUAL_STAGE04_TARGET_MODULE,
        original_import_lines=original_import_lines,
    )
    print(
        f"Deterministic 기준선 — AST: {deterministic.ast_status} {deterministic.ast_detail}, "
        f"Dependency: {deterministic.dependency_status} {deterministic.dependency_detail}",
        file=sys.stderr,
    )

    requirement = build_stage_requirements()["stage05_review"]
    # Requirement의 prompt는 그대로 두되(다른 Stage와 동일한 min_context 추정
    # 로직 재사용), 실제 OpenRouter 호출에는 위에서 만든(placeholder 없는)
    # prompt를 쓴다 — 이 실험의 핵심 수정(§핵심 수정)이 여기서 실제로 적용된다.

    runs = []
    for rep in range(1, RUN_COUNT + 1):
        pool = fetch_free_pool()
        filter_results = apply_deterministic_filter(pool, requirement)
        selection = select_candidates("stage05_review", filter_results)

        run_record = {
            "rep": rep,
            "pool_size": len(pool.models),
            "filter_case": selection.case,
            "kept_count": selection.kept_count,
            "candidate_models": list(selection.final_candidates),
            "tie_break_applied": selection.tie_break_applied,
        }

        if not selection.final_candidates:
            run_record.update({"openrouter_call_skipped": True, "reason": "Filter 통과 후보 0개"})
            runs.append(run_record)
            continue

        call_result = call_with_auto_selection(
            "stage05_review",
            prompt,
            selection.final_candidates,
            output_contract=stage05_review_contract,
            max_tokens=requirement.token_budget,
            timeout=90,
            max_retries=1,
            exclude_failed_model_from_retry_pool=True,
        )

        attempts_detail = []
        for a in call_result.attempts:
            attempts_detail.append(
                {
                    "attempt_number": a.attempt_number,
                    "http_status": a.http_status,
                    "failure_class_from_client": a.failure_class,
                    "failure_category_refined": _classify_error_detail(a.error_detail, a.http_status),
                    "api_latency_ms": a.api_latency_ms,
                    "response_present": a.raw_content is not None,
                    "contract_passed": a.contract_passed,
                }
            )

        run_record.update(
            {
                "openrouter_call_skipped": False,
                "selected_model": call_result.final_selected_model,
                "http_status_final_attempt": attempts_detail[-1]["http_status"] if attempts_detail else None,
                "total_latency_ms": call_result.total_latency_ms,
                "response_present": call_result.final_raw_content is not None,
                "contract_validation_passed": call_result.final_contract_passed,
                "retry_performed": call_result.retry_count > 0,
                "retry_count": call_result.retry_count,
                "review_result_present": bool(call_result.final_raw_content),
                "review_result_length": len(call_result.final_raw_content) if call_result.final_raw_content else 0,
                "attempts": attempts_detail,
            }
        )
        runs.append(run_record)
        print(
            f"  rep{rep}: candidates={run_record['candidate_models']} "
            f"selected={run_record.get('selected_model')} "
            f"http={run_record.get('http_status_final_attempt')} "
            f"response_present={run_record.get('response_present')} "
            f"contract={run_record.get('contract_validation_passed')} "
            f"retry={run_record.get('retry_performed')}",
            file=sys.stderr,
        )

    return {
        "pre_checks": {
            "implementation_exists": implementation_exists,
            "implementation_length": implementation_length,
            "target_module": ACTUAL_STAGE04_TARGET_MODULE,
            "target_function": ACTUAL_STAGE04_TARGET_FUNCTION,
            "prompt_contains_actual_implementation": prompt_contains_actual_implementation,
            "prompt_contains_placeholder_marker": prompt_contains_placeholder_marker,
            "provenance": ACTUAL_STAGE04_IMPLEMENTATION_PROVENANCE,
        },
        "deterministic_baseline": {
            "ast_status": deterministic.ast_status,
            "ast_detail": deterministic.ast_detail,
            "dependency_status": deterministic.dependency_status,
            "dependency_detail": deterministic.dependency_detail,
        },
        "runs": runs,
    }


if __name__ == "__main__":
    result = main()
    out_path = "/tmp/stage05_actual_implementation_revalidation_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Full output written to {out_path}", file=sys.stderr)

"""ADR-0026 Architecture Experiment — Free Pool → Deterministic Filter →
Candidate Selection(≤3) → `models[]` → OpenRouter 실제 선택 → Contract
Validation 전체 경로를 Stage 01~05 각 3회 실측한다.

Production 코드 변경 없음. Stage 01~05 Production routing 변경 없음.
RFC/ADC/ADR 변경 없음. API Key/Authorization 값 출력 없음(Egress
Proxy 자동 인증만 사용, 이 파일 어디에도 Authorization 헤더 설정
없음)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain._sibling_import import load_sibling_domain  # noqa: E402
from domain.candidate_selection import select_candidates  # noqa: E402
from domain.deterministic_filter import apply_deterministic_filter  # noqa: E402
from domain.free_pool import fetch_free_pool  # noqa: E402
from domain.stage_requirements import build_stage_requirements  # noqa: E402

call_with_auto_selection = load_sibling_domain().auto_selection_client.call_with_auto_selection

RUN_COUNT = 3
STAGE_ORDER = ("stage01", "stage02", "stage03", "stage04", "stage05_review")


def _contract_fn_for(stage_key: str, requirement):
    if stage_key == "stage04":
        return lambda content: requirement.output_contract(content, target_function_name=requirement.target_function_name)
    return requirement.output_contract


def _filter_summary(filter_results) -> list[dict]:
    return [
        {
            "model_id": r.model_id,
            "overall": r.overall,
            "checks": [{"check": c.check_name, "verdict": c.verdict, "detail": c.detail} for c in r.checks],
        }
        for r in filter_results
    ]


def run_stage(stage_key: str, requirement) -> dict:
    runs = []
    for rep in range(1, RUN_COUNT + 1):
        # 매 반복마다 Free Pool을 다시 조회한다 — Pool 자체가 반복 사이에
        # 달라질 수 있는지(사용자 지시 §8 "가능하면 서로 다른 candidate
        # pool에서도 반복") 실측으로 확인하기 위함이다. 인위적으로 pool을
        # 바꾸지 않는다(추측/조작 없음).
        pool = fetch_free_pool()
        filter_results = apply_deterministic_filter(pool, requirement)
        selection = select_candidates(stage_key, filter_results)

        contract_fn = _contract_fn_for(stage_key, requirement)

        if not selection.final_candidates:
            runs.append(
                {
                    "rep": rep,
                    "pool_size": len(pool.models),
                    "filter_case": selection.case,
                    "kept_count": selection.kept_count,
                    "final_candidates": [],
                    "tie_break_applied": selection.tie_break_applied,
                    "openrouter_call_skipped": True,
                    "reason": "Deterministic Filter 통과 후보 0개 — OpenRouter 호출 자체를 시도하지 않음(Free Pool 시점의 실제 후보 부재를 그대로 기록, 실패로 가장하지 않음)",
                    "filter_detail": _filter_summary(filter_results),
                }
            )
            continue

        call_result = call_with_auto_selection(
            stage_key,
            requirement.prompt,
            selection.final_candidates,
            output_contract=contract_fn,
            max_tokens=requirement.token_budget,
            timeout=90,
            max_retries=1,
            exclude_failed_model_from_retry_pool=True,
        )

        runs.append(
            {
                "rep": rep,
                "pool_size": len(pool.models),
                "filter_case": selection.case,
                "kept_count": selection.kept_count,
                "final_candidates": list(selection.final_candidates),
                "tie_break_applied": selection.tie_break_applied,
                "tie_break_rule": selection.tie_break_rule,
                "openrouter_call_skipped": False,
                "success": call_result.success,
                "selected_model": call_result.final_selected_model,
                "total_latency_ms": call_result.total_latency_ms,
                "retry_count": call_result.retry_count,
                "contract_passed": call_result.final_contract_passed,
                "attempts": [
                    {
                        "attempt_number": a.attempt_number,
                        "models_offered": list(a.models_offered),
                        "http_status": a.http_status,
                        "selected_model": a.selected_model,
                        "api_latency_ms": a.api_latency_ms,
                        "failure_class": a.failure_class,
                        "error_detail": a.error_detail,
                        "contract_passed": a.contract_passed,
                        "contract_detail": a.contract_detail,
                    }
                    for a in call_result.attempts
                ],
                "filter_detail": _filter_summary(filter_results),
            }
        )
        print(
            f"  {stage_key} rep{rep}: case={selection.case} final={selection.final_candidates} "
            f"success={runs[-1].get('success')} model={runs[-1].get('selected_model')} "
            f"latency={runs[-1].get('total_latency_ms')}",
            file=sys.stderr,
        )

    return {"stage": stage_key, "min_context_tokens": requirement.min_context_tokens, "min_context_tokens_basis": requirement.min_context_tokens_basis, "runs": runs}


def main() -> dict:
    requirements = build_stage_requirements()
    output = {}
    for stage_key in STAGE_ORDER:
        print(f"=== {stage_key} ===", file=sys.stderr)
        output[stage_key] = run_stage(stage_key, requirements[stage_key])
    return output


if __name__ == "__main__":
    result = main()
    out_path = "/tmp/free_model_selection_architecture_experiment_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Full output written to {out_path}", file=sys.stderr)

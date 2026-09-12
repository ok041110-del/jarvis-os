"""Stage 01~05 x 3회 실행 — OpenRouter Free Auto Selection(`models` 배열)
실측. Production 코드/Engine Routing 변경 없음. API Key/Credential 탐색·
출력 없음."""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.auto_selection_client import call_with_auto_selection  # noqa: E402
from domain.fixtures import (  # noqa: E402
    REPO_ROOT,
    STAGE01_PROMPT,
    STAGE02_PROMPT,
    STAGE03_PROMPT,
    TARGET_FUNCTION_NAME,
    build_stage04_prompt,
    build_stage05_review_prompt,
)
from domain.model_pool import fetch_free_model_pool  # noqa: E402
from domain.stage_policy import STAGE_POLICIES  # noqa: E402

RUN_COUNT = 3


def _result_to_dict(result) -> dict:
    return {
        "stage": result.stage,
        "success": result.success,
        "final_selected_model": result.final_selected_model,
        "total_latency_ms": result.total_latency_ms,
        "retry_count": result.retry_count,
        "final_contract_passed": result.final_contract_passed,
        "attempts": [
            {
                "attempt_number": a.attempt_number,
                "models_offered_count": len(a.models_offered),
                "http_status": a.http_status,
                "selected_model": a.selected_model,
                "content_length": len(a.raw_content) if a.raw_content else 0,
                "usage": a.usage,
                "api_latency_ms": a.api_latency_ms,
                "failure_class": a.failure_class,
                "error_detail": a.error_detail,
                "contract_passed": a.contract_passed,
                "contract_detail": a.contract_detail,
            }
            for a in result.attempts
        ],
        "final_raw_content": result.final_raw_content,
    }


def run_stage(stage_key: str, prompt: str, *, target_function_name: str | None = None) -> dict:
    policy = STAGE_POLICIES[stage_key]
    pool = fetch_free_model_pool()  # 매 실행마다 새로 조회 — Pool 자체가 세션 중 바뀔 수 있음을 반영

    def contract_fn(content: str):
        if stage_key == "stage04":
            return policy.output_contract(content, target_function_name=target_function_name)
        return policy.output_contract(content)

    results = []
    for i in range(1, RUN_COUNT + 1):
        result = call_with_auto_selection(
            stage_key,
            prompt,
            pool.model_ids,
            output_contract=contract_fn,
            max_tokens=policy.token_budget,
            timeout=policy.timeout_seconds,
            max_retries=policy.retry_policy.max_retries,
            exclude_failed_model_from_retry_pool=policy.retry_policy.exclude_failed_model_from_retry_pool,
        )
        results.append(_result_to_dict(result))
        print(f"  {stage_key} run {i}: success={result.success} model={result.final_selected_model} latency={result.total_latency_ms:.0f}ms retries={result.retry_count}", file=sys.stderr)

    latencies = [r["total_latency_ms"] for r in results]
    selected_models = [r["final_selected_model"] for r in results]
    contract_pass_count = sum(1 for r in results if r["final_contract_passed"])

    return {
        "stage": stage_key,
        "pool_size": len(pool.model_ids),
        "pool_excluded_known_nonfunctional": list(pool.excluded_known_nonfunctional),
        "runs": results,
        "latency_stats": {
            "values_ms": latencies,
            "mean_ms": statistics.mean(latencies),
            "p50_ms": statistics.median(latencies),
            "stdev_ms": statistics.pstdev(latencies) if len(latencies) > 1 else 0.0,
            "min_ms": min(latencies),
            "max_ms": max(latencies),
        },
        "selected_models_per_run": selected_models,
        "contract_pass_rate": f"{contract_pass_count}/{RUN_COUNT}",
    }


def main() -> dict:
    print("=== Stage 01 ===", file=sys.stderr)
    stage01 = run_stage("stage01", STAGE01_PROMPT)

    print("=== Stage 02 ===", file=sys.stderr)
    stage02 = run_stage("stage02", STAGE02_PROMPT)

    print("=== Stage 03 ===", file=sys.stderr)
    stage03 = run_stage("stage03", STAGE03_PROMPT)

    print("=== Stage 04 ===", file=sys.stderr)
    stage04_prompt = build_stage04_prompt(REPO_ROOT)
    stage04 = run_stage("stage04", stage04_prompt, target_function_name=TARGET_FUNCTION_NAME)

    print("=== Stage 05 (Review, experimental/advisory) ===", file=sys.stderr)
    stage05_prompt = build_stage05_review_prompt(REPO_ROOT)
    stage05 = run_stage("stage05_review", stage05_prompt)

    return {
        "stage01": stage01,
        "stage02": stage02,
        "stage03": stage03,
        "stage04": stage04,
        "stage05_review": stage05,
    }


if __name__ == "__main__":
    output = main()
    with open("/tmp/auto_selection_full_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    # 요약만 stdout — 전체 raw_content는 파일에만(사람이 읽는 Evidence 작성용).
    summary = {
        stage: {
            "pool_size": data["pool_size"],
            "latency_stats": data["latency_stats"],
            "selected_models_per_run": data["selected_models_per_run"],
            "contract_pass_rate": data["contract_pass_rate"],
        }
        for stage, data in output.items()
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))

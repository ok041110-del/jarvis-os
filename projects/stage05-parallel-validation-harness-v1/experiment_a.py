"""Experiment A — Single Sequential Validation vs 6-way Parallel
Validation, 동일 Stage 04 Implementation 입력으로 N회 반복(사용자 지시
Part 2). 반복 횟수는 이 세션이 이미 확립한 관례(OpenRouter Stage
01~04 반복 재현성 Validation, `OPENROUTER-STAGE-MODEL-SELECTION-0001.md`
§8 — "최소 3회 반복", `RT-0001`의 "1회 관찰은 Evidence로 인정하지
않는다")를 그대로 따라 **3회**로 정한다 — 이 Harness가 새 기준을
만들지 않는다."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.fixtures import build_fixture, build_validation_context  # noqa: E402
from domain.review import ReviewConfig  # noqa: E402
from domain.results import VALIDATOR_ID_ORDER  # noqa: E402
from domain.runner import run_parallel, run_single  # noqa: E402
from domain.test_node import TestNodeConfig  # noqa: E402
from domain.fixtures import TESTS_RELATIVE_DIR, TARGET_RELATIVE_PATH  # noqa: E402

REPEAT_COUNT = 3


def _result_to_dict(r) -> dict:
    return {
        "validator_id": r.validator_id,
        "status": r.status,
        "latency_ms": round(r.latency_ms, 3),
        "error": r.error,
    }


def _run_result_to_dict(run_result) -> dict:
    return {
        "mode": run_result.mode,
        "total_wall_clock_ms": round(run_result.total_wall_clock_ms, 3),
        "process_count": run_result.process_count,
        "thread_count": run_result.thread_count,
        "results": [_result_to_dict(r) for r in run_result.ordered_results],
        "result_id_order": [r.validator_id for r in run_result.ordered_results],
    }


def main() -> dict:
    fixture = build_fixture(REPO_ROOT)
    ctx = build_validation_context(fixture)
    review_config = ReviewConfig(mode="disabled")  # Experiment A는 Review Mode를 고정 변수로 두지 않는다(Experiment B 전용)
    test_config = TestNodeConfig(
        source_repo_root=REPO_ROOT,
        target_relative_path=TARGET_RELATIVE_PATH,
        tests_relative_dir=TESTS_RELATIVE_DIR,
    )

    runs = {"single": [], "parallel": []}
    for i in range(REPEAT_COUNT):
        single_result = run_single(ctx, review_config, test_config)
        runs["single"].append(_run_result_to_dict(single_result))
        parallel_result = run_parallel(ctx, review_config, test_config)
        runs["parallel"].append(_run_result_to_dict(parallel_result))

    # 결과 순서(Validator ID)가 고정인지 전수 확인 — 사용자 지시("실행 순서/
    # 완료 순서가 결과 순서를 결정하지 않도록 한다")를 실제로 검증한다.
    order_consistent = all(
        run["result_id_order"] == list(VALIDATOR_ID_ORDER)
        for mode_runs in runs.values()
        for run in mode_runs
    )

    return {
        "repeat_count": REPEAT_COUNT,
        "fixed_validator_id_order": list(VALIDATOR_ID_ORDER),
        "order_consistent_across_all_runs": order_consistent,
        "runs": runs,
    }


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2, ensure_ascii=False))

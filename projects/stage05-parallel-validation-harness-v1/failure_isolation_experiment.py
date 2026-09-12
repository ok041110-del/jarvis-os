"""Part 5 — Failure Isolation 실험. 7개 시나리오(6/6 success ~ all
failure)를 전부 실행하고, 매 시나리오에서 "한 Validator의 실패가 다른
Validator 실행을 막지 않는다"는 원칙을 실제로 확인한다."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.aggregator import aggregate  # noqa: E402
from domain.fixtures import build_fixture, build_validation_context  # noqa: E402
from domain.results import ValidatorResult  # noqa: E402
from domain.review import ReviewConfig, review_validator  # noqa: E402
from domain.test_node import TestNodeConfig, run_test_validator  # noqa: E402
from domain.validators import (  # noqa: E402
    ValidationContext,
    ast_validator,
    dependency_validator,
    scope_validator,
    structure_validator,
)

_BROKEN_SYNTAX_IMPLEMENTATION = "def broken(:\n    pass\n"


def _run_deterministic_four(ctx: ValidationContext) -> list[ValidatorResult]:
    return [structure_validator(ctx), scope_validator(ctx), ast_validator(ctx), dependency_validator(ctx)]


def _all_ran(results: list[ValidatorResult], expected_ids: set) -> bool:
    return {r.validator_id for r in results} == expected_ids


def scenario_6_of_6_success(fixture) -> dict:
    ctx = build_validation_context(fixture)
    test_config = TestNodeConfig(
        source_repo_root=REPO_ROOT,
        target_relative_path=fixture.target_relative_path,
        tests_relative_dir=fixture.tests_relative_dir,
    )
    results = _run_deterministic_four(ctx)
    results.append(run_test_validator(ctx.implementation, test_config))
    results.append(review_validator(ctx, ReviewConfig(mode="deterministic")))
    agg = aggregate(results)
    return {
        "scenario": "6_of_6_success",
        "verdict": agg.verdict,
        "statuses": {r.validator_id: r.status for r in agg.ordered_results},
        "all_6_ran": _all_ran(results, {"structure", "scope", "ast", "dependency", "test", "review"}),
    }


def scenario_review_failure_5_of_6_deterministic_success(fixture) -> dict:
    """Review만 FAIL(advisory) — 5개 blocking Validator는 전부 PASS.
    Verdict가 여전히 PASS여야 한다(Review는 blocking에 영향 없음)."""
    ctx = build_validation_context(fixture)
    test_config = TestNodeConfig(
        source_repo_root=REPO_ROOT,
        target_relative_path=fixture.target_relative_path,
        tests_relative_dir=fixture.tests_relative_dir,
    )
    results = _run_deterministic_four(ctx)
    results.append(run_test_validator(ctx.implementation, test_config))
    # deterministic review가 FAIL을 내도록 TODO 마커를 넣은 implementation으로 재평가
    forced_fail_ctx = ValidationContext(
        target_relative_path=ctx.target_relative_path,
        target_function_name=ctx.target_function_name,
        implementation=ctx.implementation + "\n# TODO: forced finding for failure-isolation test\n",
        original_source_snapshot=ctx.original_source_snapshot,
        scope_candidates=ctx.scope_candidates,
        original_import_lines=ctx.original_import_lines,
    )
    review_result = review_validator(forced_fail_ctx, ReviewConfig(mode="deterministic"))
    results.append(review_result)
    agg = aggregate(results)
    return {
        "scenario": "review_failure_5_of_6_deterministic_success",
        "verdict": agg.verdict,
        "statuses": {r.validator_id: r.status for r in agg.ordered_results},
        "review_status": review_result.status,
        "all_6_ran": _all_ran(results, {"structure", "scope", "ast", "dependency", "test", "review"}),
    }


def scenario_single_validator_failure_scope(fixture) -> dict:
    """Scope 하나만 FAIL(가짜 scope_candidates) — 나머지는 정상 실행."""
    ctx = build_validation_context(fixture)
    bad_scope_ctx = ValidationContext(
        target_relative_path=ctx.target_relative_path,
        target_function_name=ctx.target_function_name,
        implementation=ctx.implementation,
        original_source_snapshot=ctx.original_source_snapshot,
        scope_candidates=("some/other/unrelated/path.py",),
        original_import_lines=ctx.original_import_lines,
    )
    results = _run_deterministic_four(bad_scope_ctx)
    results.append(review_validator(bad_scope_ctx, ReviewConfig(mode="deterministic")))
    agg = aggregate(results)
    return {
        "scenario": "single_validator_failure_scope",
        "verdict": agg.verdict,
        "statuses": {r.validator_id: r.status for r in agg.ordered_results},
        "structure_ast_dependency_still_ran": _all_ran(
            [r for r in results if r.validator_id in ("structure", "ast", "dependency")],
            {"structure", "ast", "dependency"},
        ),
    }


def scenario_test_validator_failure(fixture) -> dict:
    """Test만 실제로 FAIL하도록 깨진 구현을 준 뒤, 다른 5개는 정상적으로
    실행되는지 확인한다(진짜 pytest collection 실패 재현)."""
    ctx = build_validation_context(fixture)
    broken_ctx = ValidationContext(
        target_relative_path=ctx.target_relative_path,
        target_function_name=ctx.target_function_name,
        implementation=_BROKEN_SYNTAX_IMPLEMENTATION,
        original_source_snapshot=ctx.original_source_snapshot,
        scope_candidates=ctx.scope_candidates,
        original_import_lines=ctx.original_import_lines,
    )
    test_config = TestNodeConfig(
        source_repo_root=REPO_ROOT,
        target_relative_path=fixture.target_relative_path,
        tests_relative_dir=fixture.tests_relative_dir,
    )
    results = _run_deterministic_four(broken_ctx)
    test_result = run_test_validator(broken_ctx.implementation, test_config)
    results.append(test_result)
    results.append(review_validator(broken_ctx, ReviewConfig(mode="deterministic")))
    agg = aggregate(results)
    return {
        "scenario": "test_validator_failure",
        "verdict": agg.verdict,
        "statuses": {r.validator_id: r.status for r in agg.ordered_results},
        "test_detail_pytest_executed": test_result.detail["pytest_execution"]["executed"],
        "other_5_still_ran": _all_ran(results, {"structure", "scope", "ast", "dependency", "test", "review"}),
    }


def scenario_multiple_validator_failure(fixture) -> dict:
    """Scope + AST + Dependency 동시 FAIL(가짜 scope, 다른 함수 변경,
    새 import 추가) — 전부 독립적으로 검출되는지 확인."""
    ctx = build_validation_context(fixture)
    broken_impl = ctx.implementation.replace(
        "from ..chatgpt_engine import call_engine_via_chatgpt as call_engine_review",
        "import os\nfrom ..chatgpt_engine import call_engine_via_chatgpt as call_engine_review",
    ) + "\n\ndef _unexpected_new_function():\n    pass\n"
    bad_ctx = ValidationContext(
        target_relative_path=ctx.target_relative_path,
        target_function_name=ctx.target_function_name,
        implementation=broken_impl,
        original_source_snapshot=ctx.original_source_snapshot,
        scope_candidates=("some/other/unrelated/path.py",),
        original_import_lines=ctx.original_import_lines,
    )
    results = _run_deterministic_four(bad_ctx)
    results.append(review_validator(bad_ctx, ReviewConfig(mode="deterministic")))
    agg = aggregate(results)
    failing = [r.validator_id for r in agg.ordered_results if r.status == "FAIL"]
    return {
        "scenario": "multiple_validator_failure",
        "verdict": agg.verdict,
        "statuses": {r.validator_id: r.status for r in agg.ordered_results},
        "failing_validator_ids": failing,
        "at_least_2_failed_independently": len(failing) >= 2,
    }


def scenario_all_validator_failure(fixture) -> dict:
    """전부 FAIL — 결정적 4개 + Test까지 깨진 입력을 준다."""
    ctx = build_validation_context(fixture)
    test_config = TestNodeConfig(
        source_repo_root=REPO_ROOT,
        target_relative_path=fixture.target_relative_path,
        tests_relative_dir=fixture.tests_relative_dir,
    )
    bad_ctx = ValidationContext(
        target_relative_path=ctx.target_relative_path,
        target_function_name=ctx.target_function_name,
        implementation=_BROKEN_SYNTAX_IMPLEMENTATION,
        original_source_snapshot=ctx.original_source_snapshot,
        scope_candidates=("some/other/unrelated/path.py",),
        original_import_lines=ctx.original_import_lines,
    )
    results = _run_deterministic_four(bad_ctx)
    results.append(run_test_validator(bad_ctx.implementation, test_config))
    results.append(review_validator(bad_ctx, ReviewConfig(mode="deterministic")))
    agg = aggregate(results)
    failing = [r.validator_id for r in agg.ordered_results if r.status in ("FAIL", "ERROR")]
    return {
        "scenario": "all_validator_failure",
        "verdict": agg.verdict,
        "statuses": {r.validator_id: r.status for r in agg.ordered_results},
        "failing_validator_ids": failing,
    }


def main() -> dict:
    fixture = build_fixture(REPO_ROOT)
    scenarios = [
        scenario_6_of_6_success(fixture),
        scenario_review_failure_5_of_6_deterministic_success(fixture),
        scenario_single_validator_failure_scope(fixture),
        scenario_test_validator_failure(fixture),
        scenario_multiple_validator_failure(fixture),
        scenario_all_validator_failure(fixture),
    ]
    return {"scenarios": scenarios}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, ensure_ascii=False))

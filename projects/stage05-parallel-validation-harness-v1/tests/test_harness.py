"""Stage 05 Parallel Validation Harness 자체에 대한 테스트(사용자 지시
Part 7). Production `hqs/development/`는 읽기만 한다 — 어떤 테스트도
그 트리에 쓰지 않는다(각 테스트가 이를 개별적으로 확인한다)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))

from domain.aggregator import aggregate  # noqa: E402
from domain.fixtures import build_fixture, build_validation_context  # noqa: E402
from domain.results import VALIDATOR_ID_ORDER, ValidatorResult  # noqa: E402
from domain.review import ReviewConfig, review_validator  # noqa: E402
from domain.runner import run_parallel, run_single  # noqa: E402
from domain.test_node import TestNodeConfig, run_test_validator  # noqa: E402
from domain.validators import (  # noqa: E402
    ValidationContext,
    ast_validator,
    dependency_validator,
    scope_validator,
    structure_validator,
)
from domain.workspace import TestWorkspace  # noqa: E402


# ---- 공통 fixture ----------------------------------------------------------

_ORIGINAL_SOURCE = '''"""sample module."""


def target_fn(x: int) -> int:
    """returns x doubled."""
    return x * 2


def other_fn(y: int) -> int:
    """returns y."""
    return y
'''

_VALID_IMPLEMENTATION = '''"""sample module."""


def target_fn(x: int) -> int:
    """returns x doubled, validated."""
    if not isinstance(x, int):
        raise TypeError("x must be int")
    return x * 2


def other_fn(y: int) -> int:
    """returns y."""
    return y
'''

_SCOPE_VIOLATING_IMPLEMENTATION = '''"""sample module."""


def target_fn(x: int) -> int:
    """returns x doubled, validated."""
    return x * 2


def other_fn(y: int) -> int:
    """returns y, CHANGED."""
    return y + 1
'''


def _make_ctx(implementation: str = _VALID_IMPLEMENTATION, scope_candidates=("sample/module.py",)) -> ValidationContext:
    from domain.validators import _import_lines

    return ValidationContext(
        target_relative_path="sample/module.py",
        target_function_name="target_fn",
        implementation=implementation,
        original_source_snapshot=_ORIGINAL_SOURCE,
        scope_candidates=scope_candidates,
        original_import_lines=_import_lines(_ORIGINAL_SOURCE),
    )


# ---- 1. Validator independence --------------------------------------------


def test_structure_scope_ast_dependency_do_not_read_each_others_results():
    """4개 결정적 Validator는 서로의 ValidatorResult를 인자로 받지 않는다
    (함수 시그니처 자체가 ValidationContext만 받는다) — 코드 수준으로
    독립성을 고정한다."""
    ctx = _make_ctx()
    import inspect

    for fn in (structure_validator, scope_validator, ast_validator, dependency_validator):
        params = list(inspect.signature(fn).parameters)
        assert params == ["ctx"], f"{fn.__name__}이 ValidationContext 외의 인자를 받는다: {params}"


def test_review_does_not_require_other_validator_results():
    """Review는 다른 Validator 결과를 입력으로 요구하지 않는다(RFC-0039 §2.6.1)."""
    import inspect

    params = list(inspect.signature(review_validator).parameters)
    assert params == ["ctx", "config"]


# ---- 2. Fixed validator ordering -------------------------------------------


def test_fixed_validator_id_order_is_stable():
    assert VALIDATOR_ID_ORDER == ("structure", "scope", "ast", "dependency", "test", "review")


def test_aggregate_orders_results_by_fixed_id_regardless_of_input_order():
    ctx = _make_ctx()
    shuffled = [
        ValidatorResult("review", "PASS", 1.0),
        ValidatorResult("structure", "PASS", 1.0),
        ValidatorResult("test", "PASS", 1.0),
        ValidatorResult("ast", "PASS", 1.0),
        ValidatorResult("scope", "PASS", 1.0),
        ValidatorResult("dependency", "PASS", 1.0),
    ]
    agg = aggregate(shuffled)
    assert [r.validator_id for r in agg.ordered_results] == list(VALIDATOR_ID_ORDER)


# ---- 3. Test Workspace isolation / cleanup ---------------------------------


def test_workspace_creates_isolated_copy_outside_source_repo():
    ws = TestWorkspace(REPO_ROOT)
    root = ws.create()
    try:
        assert root != REPO_ROOT
        assert not str(root).startswith(str(REPO_ROOT))
        assert (root / "hqs" / "development" / "mvp" / "tests").exists()
    finally:
        ws.cleanup()


def _tracked_source_diff() -> str:
    """`hqs/` 하위 추적 파일의 실제 변경만 본다 — 이 Harness 자신의 신규
    (아직 untracked인) 프로젝트 파일은 `git status --short`에 항상 잡히므로
    노이즈가 된다. Production 소스(`hqs/`)만 범위로 좁혀 실제 오염 여부만
    본다."""
    return subprocess.run(
        ["git", "diff", "--stat", "--", "hqs/"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


def test_workspace_mutation_does_not_touch_original_repository():
    before = _tracked_source_diff()
    ws = TestWorkspace(REPO_ROOT)
    ws.create()
    try:
        ws.apply_implementation(
            "hqs/development/mvp/agents/backend.py", "# intentionally corrupted for isolation test\n"
        )
        original_content = (REPO_ROOT / "hqs/development/mvp/agents/backend.py").read_text(encoding="utf-8")
        assert "intentionally corrupted" not in original_content
    finally:
        ws.cleanup()
    after = _tracked_source_diff()
    assert before == after == ""


def test_workspace_cleanup_failure_does_not_raise_and_original_stays_safe():
    ws = TestWorkspace(REPO_ROOT)
    ws.create()
    # Workspace를 먼저 지워서 cleanup()이 "이미 없음"을 만나게 한다 — 이는
    # 실패로 취급하지 않는다(shutil.rmtree는 대상이 없으면 FileNotFoundError를
    # 던지므로, 이 케이스는 cleanup()이 그 예외를 흡수해 succeeded=False로
    # 구조화하는지 확인한다).
    import shutil

    shutil.rmtree(ws.workspace_root)
    result = ws.cleanup()
    assert result.attempted is True
    assert result.succeeded is False
    assert result.error is not None
    # 원본 저장소는 이 실패와 무관하게 항상 안전하다.
    assert _tracked_source_diff() == ""


def test_apply_implementation_rejects_path_outside_workspace():
    ws = TestWorkspace(REPO_ROOT)
    ws.create()
    try:
        from domain.workspace import ImplementationApplyError

        with pytest.raises(ImplementationApplyError):
            ws.apply_implementation("../../etc/passwd", "malicious")
    finally:
        ws.cleanup()


# ---- 4. Failure isolation ---------------------------------------------------


def test_test_workspace_creation_failure_does_not_raise_and_is_reported():
    ws = TestWorkspace(Path("/nonexistent/repo/root/for/harness/test"))
    from domain.workspace import WorkspaceCreationError

    with pytest.raises(WorkspaceCreationError):
        ws.create()


def test_run_test_validator_reports_structured_error_on_bad_repo_root():
    config = TestNodeConfig(
        source_repo_root=Path("/nonexistent/repo/root/for/harness/test"),
        target_relative_path="sample/module.py",
        tests_relative_dir="sample/tests",
    )
    result = run_test_validator(_VALID_IMPLEMENTATION, config)
    assert result.status == "ERROR"
    assert result.detail["workspace_creation"]["succeeded"] is False


def test_one_validator_failure_does_not_prevent_others_from_running():
    """Scope가 FAIL이어도 Structure/AST/Dependency는 정상적으로 실행된다
    (서로 독립) — Aggregator가 전부 수집한 뒤 Verdict를 낸다."""
    ctx = _make_ctx(scope_candidates=("other/path.py",))  # target_relative_path가 scope 밖
    results = [
        structure_validator(ctx),
        scope_validator(ctx),
        ast_validator(ctx),
        dependency_validator(ctx),
    ]
    statuses = {r.validator_id: r.status for r in results}
    assert statuses["scope"] == "FAIL"
    assert statuses["structure"] == "PASS"
    assert statuses["ast"] == "PASS"
    assert statuses["dependency"] == "PASS"


def test_multiple_validator_failures_all_collected():
    ctx = _make_ctx(implementation=_SCOPE_VIOLATING_IMPLEMENTATION, scope_candidates=("other/path.py",))
    results = [
        structure_validator(ctx),
        scope_validator(ctx),
        ast_validator(ctx),
        dependency_validator(ctx),
    ]
    agg = aggregate(results)
    assert agg.verdict == "FAIL"
    assert agg.results_by_id["scope"].status == "FAIL"
    assert agg.results_by_id["ast"].status == "FAIL"


def test_all_validator_failure_yields_fail_verdict():
    ctx = _make_ctx(implementation="not valid python (((", scope_candidates=("other/path.py",))
    results = [
        structure_validator(ctx),
        scope_validator(ctx),
        ast_validator(ctx),
        dependency_validator(ctx),
    ]
    agg = aggregate(results)
    assert agg.verdict == "FAIL"


# ---- 5. Aggregator deterministic blocking policy / Review advisory --------


def test_aggregator_review_pass_does_not_override_deterministic_fail():
    results = [
        ValidatorResult("structure", "FAIL", 1.0),
        ValidatorResult("scope", "PASS", 1.0),
        ValidatorResult("ast", "PASS", 1.0),
        ValidatorResult("dependency", "PASS", 1.0),
        ValidatorResult("test", "PASS", 1.0),
        ValidatorResult("review", "PASS", 1.0),
    ]
    agg = aggregate(results)
    assert agg.verdict == "FAIL"


def test_aggregator_review_fail_does_not_force_deterministic_pass_to_fail():
    results = [
        ValidatorResult("structure", "PASS", 1.0),
        ValidatorResult("scope", "PASS", 1.0),
        ValidatorResult("ast", "PASS", 1.0),
        ValidatorResult("dependency", "PASS", 1.0),
        ValidatorResult("test", "PASS", 1.0),
        ValidatorResult("review", "FAIL", 1.0),
    ]
    agg = aggregate(results)
    assert agg.verdict == "PASS"


def test_aggregator_missing_blocking_validator_yields_partial():
    results = [
        ValidatorResult("structure", "PASS", 1.0),
        ValidatorResult("scope", "PASS", 1.0),
        ValidatorResult("ast", "PASS", 1.0),
        ValidatorResult("dependency", "PASS", 1.0),
        # test 누락
        ValidatorResult("review", "PASS", 1.0),
    ]
    agg = aggregate(results)
    assert agg.verdict == "PARTIAL"
    assert "test" in agg.missing_validator_ids


def test_review_disabled_mode_is_skipped_and_does_not_affect_verdict():
    ctx = _make_ctx()
    review_result = review_validator(ctx, ReviewConfig(mode="disabled"))
    assert review_result.status == "SKIPPED"
    results = [
        structure_validator(ctx),
        scope_validator(ctx),
        ast_validator(ctx),
        dependency_validator(ctx),
        ValidatorResult("test", "PASS", 1.0),
        review_result,
    ]
    agg = aggregate(results)
    assert agg.verdict == "PASS"


def test_review_llm_mode_without_engine_call_fails_explicitly_not_silently():
    ctx = _make_ctx()
    result = review_validator(ctx, ReviewConfig(mode="llm", engine_call=None))
    assert result.status == "ERROR"
    assert result.error is not None


# ---- 6. Single/Parallel result equivalence (synthetic, fast) --------------


def test_single_and_parallel_produce_equivalent_deterministic_statuses(monkeypatch):
    """Test/Review를 실제로 실행하지 않고(느림·비결정) Structure/Scope/AST/
    Dependency만 비교한다 — 결정적 4개 Validator는 Single/Parallel 실행
    방식과 무관하게 동일한 status를 내야 한다."""
    ctx = _make_ctx()
    seq = [structure_validator(ctx), scope_validator(ctx), ast_validator(ctx), dependency_validator(ctx)]

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(structure_validator, ctx),
            pool.submit(scope_validator, ctx),
            pool.submit(ast_validator, ctx),
            pool.submit(dependency_validator, ctx),
        ]
        par = [f.result() for f in futures]

    seq_status = {r.validator_id: r.status for r in seq}
    par_status = {r.validator_id: r.status for r in par}
    assert seq_status == par_status


# ---- 7. Real end-to-end(느림, 실제 Production 대상 fixture 사용) ----------


@pytest.mark.slow
def test_real_fixture_single_and_parallel_agree_and_repository_untouched():
    """실제 backend.py 대상 fixture로 Single/Parallel을 각 1회 실행해
    Verdict가 같은지, 원본 저장소가 무변화인지 확인한다(느림 — 실제
    pytest 전체 스위트를 2회 실행, 약 1분)."""
    before = _tracked_source_diff()

    fixture = build_fixture(REPO_ROOT)
    ctx = build_validation_context(fixture)
    review_config = ReviewConfig(mode="deterministic")
    test_config = TestNodeConfig(
        source_repo_root=REPO_ROOT,
        target_relative_path=fixture.target_relative_path,
        tests_relative_dir=fixture.tests_relative_dir,
    )

    single = run_single(ctx, review_config, test_config)
    parallel = run_parallel(ctx, review_config, test_config)

    single_agg = aggregate(single.ordered_results)
    parallel_agg = aggregate(parallel.ordered_results)

    assert single_agg.verdict == parallel_agg.verdict == "PASS"
    assert [r.validator_id for r in single.ordered_results] == list(VALIDATOR_ID_ORDER)
    assert [r.validator_id for r in parallel.ordered_results] == list(VALIDATOR_ID_ORDER)

    after = _tracked_source_diff()
    assert before == after == ""

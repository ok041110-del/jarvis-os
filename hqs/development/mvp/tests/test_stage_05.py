"""Stage 05(Validation) `run_stage_05()` 검증 (ADR-0008,
`stages/05_validation/VALIDATION.md`).

`backend_agent_code_review`는 재구현하지 않았으므로 여기서는 (a) 4개
결정적 Capability(구조/Specification Scope/Design Scope/Test Execution)
가 Stage 02/04 Output을 정확히 반영하는지, (b) pytest 실행이 예외 발생
시에도 원본 파일을 복원하는지, (c) Code Review가 실제 implementation을
받는지, (d) PASS/FAIL/PARTIAL 판정 규칙이 정확한지를 검증한다.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_STAGE_05_PATH = Path(__file__).resolve().parents[2] / "stages" / "05_validation" / "stage_05.py"
_spec = importlib.util.spec_from_file_location("stage_05", _STAGE_05_PATH)
stage_05 = importlib.util.module_from_spec(_spec)
sys.modules["stage_05"] = stage_05
_spec.loader.exec_module(stage_05)

ORIGINAL_SOURCE = "def target_fn():\n    pass\n\n\ndef other_fn():\n    return 1\n"
SCOPE_COMPLIANT_SOURCE = "def target_fn():\n    return 42\n\n\ndef other_fn():\n    return 1\n"
SCOPE_VIOLATING_SOURCE = "def target_fn():\n    return 42\n\n\ndef other_fn():\n    return 2\n"


# --- _check_structural -------------------------------------------------------


def test_structural_check_valid_normal_implementation():
    result = stage_05._check_structural({"target": None, "implementation": "CODE", "expose_target": False})
    assert result == {"valid": True, "engine_failed": False}


def test_structural_check_detects_engine_failure():
    result = stage_05._check_structural(
        {"target": None, "implementation": "Engine call failed: boom", "expose_target": False}
    )
    assert result == {"valid": True, "engine_failed": True}


# --- _check_specification_scope ----------------------------------------------


def test_specification_scope_target_none_returns_none():
    result = stage_05._check_specification_scope(None, {"skeleton": {"scope_candidates": []}})
    assert result == {"target_in_scope": None}


def test_specification_scope_target_in_scope_candidates(monkeypatch):
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: stage_05.ROOT / "hqs/development/mvp/agents.py")

    result = stage_05._check_specification_scope(
        ("agents", "backend_agent_code_review"),
        {"skeleton": {"scope_candidates": ["hqs/development/mvp/agents.py"]}},
    )
    assert result == {"target_in_scope": True}


def test_specification_scope_target_not_in_scope_candidates(monkeypatch):
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: stage_05.ROOT / "hqs/development/mvp/agents.py")

    result = stage_05._check_specification_scope(
        ("agents", "backend_agent_code_review"),
        {"skeleton": {"scope_candidates": ["hqs/development/mvp/workflow.py"]}},
    )
    assert result == {"target_in_scope": False}


def test_specification_scope_missing_scope_candidates_returns_none_without_raising(monkeypatch):
    """`skeleton`은 있지만 nested `scope_candidates`가 없는 불완전한 Stage 02
    Output(contracts.py는 top-level 키만 검사해 감지하지 못함) — raw KeyError
    대신 target 미상과 동일한 판정 불가(None)로 처리된다."""
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: stage_05.ROOT / "hqs/development/mvp/agents.py")

    result = stage_05._check_specification_scope(
        ("agents", "backend_agent_code_review"),
        {"skeleton": {}, "specification": "x"},
    )
    assert result == {"target_in_scope": None}


def test_specification_scope_missing_skeleton_key_returns_none_without_raising(monkeypatch):
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: stage_05.ROOT / "hqs/development/mvp/agents.py")

    result = stage_05._check_specification_scope(("agents", "backend_agent_code_review"), {})
    assert result == {"target_in_scope": None}


# --- _check_design_scope ------------------------------------------------------


def test_design_scope_none_when_no_target():
    result = stage_05._check_design_scope(None, True, SCOPE_COMPLIANT_SOURCE)
    assert result == {"scope_ok": None, "changed_names": []}


def test_design_scope_none_when_not_exposed():
    result = stage_05._check_design_scope(("m", "target_fn"), False, SCOPE_COMPLIANT_SOURCE)
    assert result == {"scope_ok": None, "changed_names": []}


def test_design_scope_ok_when_only_target_changed(tmp_path, monkeypatch):
    fake_module = tmp_path / "sample_module.py"
    fake_module.write_text(ORIGINAL_SOURCE)
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: fake_module)

    result = stage_05._check_design_scope(("sample_module", "target_fn"), True, SCOPE_COMPLIANT_SOURCE)

    assert result == {"scope_ok": True, "changed_names": []}


def test_design_scope_violation_when_other_function_changed(tmp_path, monkeypatch):
    fake_module = tmp_path / "sample_module.py"
    fake_module.write_text(ORIGINAL_SOURCE)
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: fake_module)

    result = stage_05._check_design_scope(("sample_module", "target_fn"), True, SCOPE_VIOLATING_SOURCE)

    assert result["scope_ok"] is False
    assert result["changed_names"] == ["other_fn"]


# malformed Engine implementation(신뢰할 수 없는 입력) — ast.parse()가
# raw SyntaxError를 던지는 대신 구조화된 blocking FAIL로 처리되는지 확인.
MALFORMED_IMPLEMENTATIONS = {
    "unterminated_string": '"unterminated',
    "unterminated_paren": "def target_fn(:\n    return 42\n",
    "bad_indentation": "def target_fn():\nreturn 42\n",
}


@pytest.mark.parametrize("implementation", MALFORMED_IMPLEMENTATIONS.values(), ids=MALFORMED_IMPLEMENTATIONS.keys())
def test_design_scope_handles_malformed_implementation_without_raising(tmp_path, monkeypatch, implementation):
    fake_module = tmp_path / "sample_module.py"
    fake_module.write_text(ORIGINAL_SOURCE)
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: fake_module)

    result = stage_05._check_design_scope(("sample_module", "target_fn"), True, implementation)

    assert result["scope_ok"] is False
    assert result["changed_names"] == []
    assert "parse_error" in result


@pytest.mark.parametrize("implementation", MALFORMED_IMPLEMENTATIONS.values(), ids=MALFORMED_IMPLEMENTATIONS.keys())
def test_malformed_implementation_yields_fail_verdict_via_design_scope_blocking(tmp_path, monkeypatch, implementation):
    """design_scope는 blocking이므로, malformed implementation이 구조화된
    FAIL로 처리되면 최종 Verdict도 raw exception 없이 FAIL이 된다."""
    fake_module = tmp_path / "sample_module.py"
    fake_module.write_text(ORIGINAL_SOURCE)
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: fake_module)
    monkeypatch.setattr(stage_05, "backend_agent_code_review", lambda code: "REVIEW")
    monkeypatch.setattr(
        stage_05, "_check_specification_scope", lambda target, stage_02_output: {"target_in_scope": True}
    )
    monkeypatch.setattr(
        stage_05,
        "_run_pytest_with_applied_implementation",
        lambda target, expose_target, implementation: {"executed": False, "returncode": None, "output": ""},
    )

    stage_04_output = {"target": ("sample_module", "target_fn"), "implementation": implementation, "expose_target": True}
    stage_02_output = {"skeleton": {"scope_candidates": []}}

    result = stage_05.run_stage_05(stage_02_output, stage_04_output)

    design_scope = next(check for check in result["check_results"] if check["name"] == "design_scope")
    assert design_scope["status"] == "FAIL"
    assert design_scope["blocking"] is True
    assert result["verdict"] == "FAIL"


# --- _run_pytest_with_applied_implementation ----------------------------------


def test_pytest_execution_skipped_without_target():
    result = stage_05._run_pytest_with_applied_implementation(None, True, "CODE")
    assert result == {"executed": False, "returncode": None, "output": ""}


def test_pytest_execution_skipped_without_exposure():
    result = stage_05._run_pytest_with_applied_implementation(("m", "f"), False, "CODE")
    assert result == {"executed": False, "returncode": None, "output": ""}


def test_pytest_execution_restores_original_file_even_on_subprocess_exception(tmp_path, monkeypatch):
    fake_module = tmp_path / "sample_module.py"
    fake_module.write_text(ORIGINAL_SOURCE)
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: fake_module)

    def raising_run(*args, **kwargs):
        raise RuntimeError("subprocess boom")

    monkeypatch.setattr(stage_05.subprocess, "run", raising_run)

    try:
        stage_05._run_pytest_with_applied_implementation(("sample_module", "target_fn"), True, "CHANGED CONTENT")
    except RuntimeError:
        pass

    assert fake_module.read_text() == ORIGINAL_SOURCE


def test_pytest_execution_reports_returncode(tmp_path, monkeypatch):
    fake_module = tmp_path / "sample_module.py"
    fake_module.write_text(ORIGINAL_SOURCE)
    monkeypatch.setattr(stage_05, "module_source_path", lambda module: fake_module)

    class FakeResult:
        returncode = 0
        stdout = "1 passed"
        stderr = ""

    monkeypatch.setattr(stage_05.subprocess, "run", lambda *args, **kwargs: FakeResult())

    result = stage_05._run_pytest_with_applied_implementation(("sample_module", "target_fn"), True, SCOPE_COMPLIANT_SOURCE)

    assert result == {"executed": True, "returncode": 0, "output": "1 passed"}
    assert fake_module.read_text() == ORIGINAL_SOURCE


# --- _determine_verdict --------------------------------------------------------


def _checks(structural_valid=True, engine_failed=False, target_in_scope=True, scope_ok=True, executed=True, returncode=0):
    return (
        {"valid": structural_valid, "engine_failed": engine_failed},
        {"target_in_scope": target_in_scope},
        {"scope_ok": scope_ok, "changed_names": []},
        {"executed": executed, "returncode": returncode, "output": ""},
    )


def test_verdict_pass_when_all_checks_succeed():
    assert stage_05._determine_verdict(*_checks()) == "PASS"


def test_verdict_fail_on_engine_failure():
    assert stage_05._determine_verdict(*_checks(engine_failed=True)) == "FAIL"


def test_verdict_fail_on_pytest_failure():
    assert stage_05._determine_verdict(*_checks(returncode=1)) == "FAIL"


def test_verdict_fail_on_design_scope_violation():
    assert stage_05._determine_verdict(*_checks(scope_ok=False)) == "FAIL"


def test_verdict_partial_when_test_not_executed():
    assert stage_05._determine_verdict(*_checks(executed=False, returncode=None)) == "PARTIAL"


def test_verdict_partial_when_target_not_in_scope():
    assert stage_05._determine_verdict(*_checks(target_in_scope=False)) == "PARTIAL"


def test_verdict_partial_when_scope_undetermined():
    assert stage_05._determine_verdict(*_checks(scope_ok=None)) == "PARTIAL"


# --- run_stage_05(통합) --------------------------------------------------------


def test_run_stage_05_engine_failure_short_circuits_to_fail(monkeypatch):
    stage_04_output = {"target": None, "implementation": "Engine call failed: boom", "expose_target": False}

    result = stage_05.run_stage_05({"skeleton": {"scope_candidates": []}}, stage_04_output)

    assert result["verdict"] == "FAIL"
    assert result["code_review"] == "(Stage 04 Engine 실패로 Code Review를 건너뜀)"


def test_run_stage_05_code_review_receives_implementation(monkeypatch):
    seen = {}

    def fake_review(code):
        seen["code"] = code
        return "REVIEW"

    monkeypatch.setattr(stage_05, "backend_agent_code_review", fake_review)

    stage_04_output = {"target": None, "implementation": "SOME CODE", "expose_target": False}
    result = stage_05.run_stage_05({"skeleton": {"scope_candidates": []}}, stage_04_output)

    assert seen["code"] == "SOME CODE"
    assert result["code_review"] == "REVIEW"
    assert result["verdict"] == "PARTIAL"


def test_run_stage_05_code_review_engine_failure_preserves_verdict_logic(monkeypatch):
    def raising_review(code):
        raise RuntimeError("boom")

    monkeypatch.setattr(stage_05, "backend_agent_code_review", raising_review)

    stage_04_output = {"target": None, "implementation": "SOME CODE", "expose_target": False}
    result = stage_05.run_stage_05({"skeleton": {"scope_candidates": []}}, stage_04_output)

    assert result["code_review"] == "Engine call failed: boom"
    assert result["verdict"] == "PARTIAL"


# --- required_checks / VerificationResult Contract (regression) --------------


def test_required_checks_is_declared_and_stable():
    assert stage_05.REQUIRED_CHECKS == ("structural", "specification_scope", "design_scope", "test_execution")


def test_run_stage_05_exposes_structured_check_results(monkeypatch):
    monkeypatch.setattr(stage_05, "backend_agent_code_review", lambda code: "REVIEW")

    stage_04_output = {"target": None, "implementation": "SOME CODE", "expose_target": False}
    result = stage_05.run_stage_05({"skeleton": {"scope_candidates": []}}, stage_04_output)

    assert result["required_checks"] == stage_05.REQUIRED_CHECKS
    names = [check["name"] for check in result["check_results"]]
    assert names == list(stage_05.REQUIRED_CHECKS)
    for check in result["check_results"]:
        assert check["status"] in ("PASS", "FAIL", "INCONCLUSIVE")


def test_blocking_check_failure_is_reflected_in_check_results(monkeypatch):
    stage_04_output = {"target": None, "implementation": "Engine call failed: boom", "expose_target": False}

    result = stage_05.run_stage_05({"skeleton": {"scope_candidates": []}}, stage_04_output)

    structural = next(check for check in result["check_results"] if check["name"] == "structural")
    assert structural["status"] == "FAIL"
    assert structural["blocking"] is True
    assert result["verdict"] == "FAIL"


# --- required_checks가 실제 실행/Verdict에 인과적 영향을 주는지(회귀) ----------


def _stub_deterministic_checks(monkeypatch, code_review="REVIEW"):
    monkeypatch.setattr(stage_05, "_check_structural", lambda stage_04_output: {"valid": True, "engine_failed": False})
    monkeypatch.setattr(
        stage_05, "_check_specification_scope", lambda target, stage_02_output: {"target_in_scope": True}
    )
    monkeypatch.setattr(
        stage_05,
        "_check_design_scope",
        lambda target, expose_target, implementation: {"scope_ok": True, "changed_names": []},
    )
    monkeypatch.setattr(stage_05, "backend_agent_code_review", lambda code: code_review)


def test_excluding_test_execution_from_required_checks_skips_its_actual_execution(monkeypatch):
    """required_checks에서 `test_execution`을 빼면, 그 검사 함수가 실제로
    호출되지 않는다(단순 결과 무시가 아니라 실행 자체가 skip됨)."""
    _stub_deterministic_checks(monkeypatch)
    calls = []

    def fake_pytest(target, expose_target, implementation):
        calls.append((target, expose_target, implementation))
        return {"executed": True, "returncode": 1, "output": "1 failed"}

    monkeypatch.setattr(stage_05, "_run_pytest_with_applied_implementation", fake_pytest)

    stage_04_output = {"target": ("m", "f"), "implementation": "SOME CODE", "expose_target": True}
    stage_02_output = {"skeleton": {"scope_candidates": []}}

    stage_05.run_stage_05(
        stage_02_output, stage_04_output, required_checks=("structural", "specification_scope", "design_scope")
    )

    assert calls == []  # pytest 실행 함수가 아예 호출되지 않았다


def test_required_checks_value_changes_verdict_for_same_underlying_state(monkeypatch):
    """동일한 Stage 04 Output(test_execution이 FAIL할 상태)에서, required_checks에
    `test_execution`을 포함하느냐 빼느냐에 따라 Verdict가 실제로 달라진다."""
    _stub_deterministic_checks(monkeypatch)
    monkeypatch.setattr(
        stage_05,
        "_run_pytest_with_applied_implementation",
        lambda target, expose_target, implementation: {"executed": True, "returncode": 1, "output": "1 failed"},
    )

    stage_04_output = {"target": ("m", "f"), "implementation": "SOME CODE", "expose_target": True}
    stage_02_output = {"skeleton": {"scope_candidates": []}}

    result_full = stage_05.run_stage_05(stage_02_output, stage_04_output)
    assert result_full["verdict"] == "FAIL"
    test_check_full = next(c for c in result_full["check_results"] if c["name"] == "test_execution")
    assert test_check_full["status"] == "FAIL"

    result_without_test_execution = stage_05.run_stage_05(
        stage_02_output, stage_04_output, required_checks=("structural", "specification_scope", "design_scope")
    )
    assert result_without_test_execution["verdict"] == "PASS"
    test_check_skipped = next(
        c for c in result_without_test_execution["check_results"] if c["name"] == "test_execution"
    )
    assert test_check_skipped["status"] == "SKIPPED"
    assert test_check_skipped["blocking"] is False


def test_required_checks_result_always_lists_all_known_checks_with_skip_marker(monkeypatch):
    _stub_deterministic_checks(monkeypatch)
    monkeypatch.setattr(
        stage_05,
        "_run_pytest_with_applied_implementation",
        lambda target, expose_target, implementation: {"executed": True, "returncode": 0, "output": ""},
    )

    stage_04_output = {"target": None, "implementation": "CODE", "expose_target": False}
    result = stage_05.run_stage_05(
        {"skeleton": {"scope_candidates": []}}, stage_04_output, required_checks=("structural",)
    )

    statuses = {check["name"]: check["status"] for check in result["check_results"]}
    assert statuses["structural"] != "SKIPPED"
    assert statuses["specification_scope"] == "SKIPPED"
    assert statuses["design_scope"] == "SKIPPED"
    assert statuses["test_execution"] == "SKIPPED"
    assert result["required_checks"] == ("structural",)


def test_run_stage_05_rejects_empty_required_checks_instead_of_silently_passing():
    stage_04_output = {"target": None, "implementation": "CODE", "expose_target": False}

    with pytest.raises(Exception) as exc_info:
        stage_05.run_stage_05({"skeleton": {"scope_candidates": []}}, stage_04_output, required_checks=())

    assert "required_checks" in str(exc_info.value)


def test_run_stage_05_rejects_unknown_required_check_name():
    stage_04_output = {"target": None, "implementation": "CODE", "expose_target": False}

    with pytest.raises(Exception) as exc_info:
        stage_05.run_stage_05(
            {"skeleton": {"scope_candidates": []}}, stage_04_output, required_checks=("not_a_real_check",)
        )

    assert "not_a_real_check" in str(exc_info.value)

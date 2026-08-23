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

_STAGE_05_PATH = Path(__file__).resolve().parents[2] / "stages" / "05_validation" / "stage_05.py"
_spec = importlib.util.spec_from_file_location("stage_05", _STAGE_05_PATH)
stage_05 = importlib.util.module_from_spec(_spec)
sys.modules["stage_05"] = stage_05
_spec.loader.exec_module(stage_05)

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}

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

    result = stage_05.run_stage_05(SAMPLE_ISSUE, {"skeleton": {"scope_candidates": []}}, {"design": "D"}, stage_04_output)

    assert result["verdict"] == "FAIL"
    assert result["code_review"] == "(Stage 04 Engine 실패로 Code Review를 건너뜀)"


def test_run_stage_05_code_review_receives_implementation(monkeypatch):
    seen = {}

    def fake_review(code):
        seen["code"] = code
        return "REVIEW"

    monkeypatch.setattr(stage_05, "backend_agent_code_review", fake_review)

    stage_04_output = {"target": None, "implementation": "SOME CODE", "expose_target": False}
    result = stage_05.run_stage_05(SAMPLE_ISSUE, {"skeleton": {"scope_candidates": []}}, {"design": "D"}, stage_04_output)

    assert seen["code"] == "SOME CODE"
    assert result["code_review"] == "REVIEW"
    assert result["verdict"] == "PARTIAL"


def test_run_stage_05_code_review_engine_failure_preserves_verdict_logic(monkeypatch):
    def raising_review(code):
        raise RuntimeError("boom")

    monkeypatch.setattr(stage_05, "backend_agent_code_review", raising_review)

    stage_04_output = {"target": None, "implementation": "SOME CODE", "expose_target": False}
    result = stage_05.run_stage_05(SAMPLE_ISSUE, {"skeleton": {"scope_candidates": []}}, {"design": "D"}, stage_04_output)

    assert result["code_review"] == "Engine call failed: boom"
    assert result["verdict"] == "PARTIAL"

"""01→05 Integrated Workflow(`hqs/development/workflow.py`) `run_workflow()`
검증.

각 Stage의 내부 로직은 재구현하지 않았으므로 여기서는 (a) 5개 Stage가
정확한 순서로, 문서화된 Input/Output Handover 그대로 호출되는지, (b)
중간 Stage 실패 시 이후 Stage가 호출되지 않고 즉시 중단하는지, (c)
Stage 05의 `verdict`가 재해석 없이 그대로 반환되는지, (d) 각 Stage
Output이 `stages/contracts.py` 필수 키를 채우지 못하면 명시적으로
실패 처리되는지만 mock으로 검증한다.
"""

import importlib.util
import sys
from pathlib import Path

_WORKFLOW_PATH = Path(__file__).resolve().parents[2] / "workflow.py"
_spec = importlib.util.spec_from_file_location("workflow", _WORKFLOW_PATH)
workflow = importlib.util.module_from_spec(_spec)
sys.modules["workflow"] = workflow
_spec.loader.exec_module(workflow)

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}

STAGE_01_OUTPUT = {
    "directory_structure": "...",
    "context_bundle": {},
    "candidate_index": "INDEX",
    "target": None,
    "dependency_closure": None,
}
STAGE_02_OUTPUT = {"skeleton": {}, "specification": "SPEC"}
STAGE_03_OUTPUT = {"skeleton": {}, "design": "DESIGN"}
STAGE_04_OUTPUT = {"target": None, "implementation": "CODE", "expose_target": False}
STAGE_05_OUTPUT = {
    "required_checks": ("structural",),
    "check_results": [{"name": "structural", "status": "PASS", "blocking": True, "detail": {}}],
    "verdict": "PASS",
}


def _stub_happy_path(monkeypatch):
    calls = []

    def fake_stage_01(issue):
        calls.append(("stage_01", issue))
        return dict(STAGE_01_OUTPUT)

    def fake_stage_02(issue, stage_01_context):
        calls.append(("stage_02", issue, stage_01_context))
        return dict(STAGE_02_OUTPUT)

    def fake_stage_03(issue, stage_01_context, stage_02_output):
        calls.append(("stage_03", issue, stage_01_context, stage_02_output))
        return dict(STAGE_03_OUTPUT)

    def fake_stage_04(stage_01_context, stage_03_output, expose_target=False):
        calls.append(("stage_04", stage_01_context, stage_03_output, expose_target))
        return {**STAGE_04_OUTPUT, "expose_target": expose_target}

    def fake_stage_05(stage_02_output, stage_04_output):
        calls.append(("stage_05", stage_02_output, stage_04_output))
        return dict(STAGE_05_OUTPUT)

    monkeypatch.setattr(workflow.stage_01, "run_stage_01", fake_stage_01)
    monkeypatch.setattr(workflow.stage_02, "run_stage_02", fake_stage_02)
    monkeypatch.setattr(workflow.stage_03, "run_stage_03", fake_stage_03)
    monkeypatch.setattr(workflow.stage_04, "run_stage_04", fake_stage_04)
    monkeypatch.setattr(workflow.stage_05, "run_stage_05", fake_stage_05)
    return calls


# --- 순서 / Handover -----------------------------------------------------------


def test_stages_execute_in_order_with_documented_handover(monkeypatch):
    calls = _stub_happy_path(monkeypatch)

    result = workflow.run_workflow(SAMPLE_ISSUE)

    order = [call[0] for call in calls]
    assert order == ["stage_01", "stage_02", "stage_03", "stage_04", "stage_05"]

    assert calls[0] == ("stage_01", SAMPLE_ISSUE)
    assert calls[1] == ("stage_02", SAMPLE_ISSUE, STAGE_01_OUTPUT)
    assert calls[2] == ("stage_03", SAMPLE_ISSUE, STAGE_01_OUTPUT, STAGE_02_OUTPUT)
    assert calls[3] == ("stage_04", STAGE_01_OUTPUT, STAGE_03_OUTPUT, False)
    assert calls[4] == ("stage_05", STAGE_02_OUTPUT, STAGE_04_OUTPUT)

    assert result["stage_01"] == STAGE_01_OUTPUT
    assert result["stage_02"] == STAGE_02_OUTPUT
    assert result["stage_03"] == STAGE_03_OUTPUT
    assert result["stage_04"] == STAGE_04_OUTPUT
    assert result["stage_05"] == STAGE_05_OUTPUT
    assert result["failed_at"] is None
    assert result["error"] is None


def test_expose_target_is_passed_through_to_stage_04(monkeypatch):
    calls = _stub_happy_path(monkeypatch)

    workflow.run_workflow(SAMPLE_ISSUE, expose_target=True)

    stage_04_call = next(call for call in calls if call[0] == "stage_04")
    assert stage_04_call[3] is True


def test_verdict_is_returned_unchanged_not_reinterpreted(monkeypatch):
    _stub_happy_path(monkeypatch)
    monkeypatch.setattr(
        workflow.stage_05,
        "run_stage_05",
        lambda s2, s4: {
            "required_checks": ("structural",),
            "check_results": [{"name": "structural", "status": "PASS", "blocking": True, "detail": {}}],
            "verdict": "PARTIAL",
            "extra": "untouched",
        },
    )

    result = workflow.run_workflow(SAMPLE_ISSUE)

    assert result["stage_05"] == {
        "required_checks": ("structural",),
        "check_results": [{"name": "structural", "status": "PASS", "blocking": True, "detail": {}}],
        "verdict": "PARTIAL",
        "extra": "untouched",
    }


# --- Contract validation(Handover 시점 필수 키 검증) ----------------------------


def test_stage_output_missing_required_key_fails_explicitly_not_silently(monkeypatch):
    """Stage 01이 Contract가 요구하는 키(`candidate_index`)를 채우지 못하면
    다음 Stage로 조용히 넘어가지 않고 `failed_at`/`error`로 명시적으로
    드러나야 한다."""
    incomplete_stage_01_output = dict(STAGE_01_OUTPUT)
    del incomplete_stage_01_output["candidate_index"]

    monkeypatch.setattr(workflow.stage_01, "run_stage_01", lambda issue: incomplete_stage_01_output)
    monkeypatch.setattr(workflow.stage_02, "run_stage_02", _fail_if_called("stage_02"))
    monkeypatch.setattr(workflow.stage_03, "run_stage_03", _fail_if_called("stage_03"))
    monkeypatch.setattr(workflow.stage_04, "run_stage_04", _fail_if_called("stage_04"))
    monkeypatch.setattr(workflow.stage_05, "run_stage_05", _fail_if_called("stage_05"))

    result = workflow.run_workflow(SAMPLE_ISSUE)

    assert result["failed_at"] == "stage_01"
    assert "candidate_index" in result["error"]


# --- 중간 실패 시 즉시 중단 ------------------------------------------------------


def _fail_if_called(name):
    def _raise(*args, **kwargs):
        raise AssertionError(f"{name}는 이전 Stage 실패 후 호출되면 안 된다")

    return _raise


def test_stage_01_failure_stops_before_any_later_stage(monkeypatch):
    monkeypatch.setattr(workflow.stage_01, "run_stage_01", lambda issue: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(workflow.stage_02, "run_stage_02", _fail_if_called("stage_02"))
    monkeypatch.setattr(workflow.stage_03, "run_stage_03", _fail_if_called("stage_03"))
    monkeypatch.setattr(workflow.stage_04, "run_stage_04", _fail_if_called("stage_04"))
    monkeypatch.setattr(workflow.stage_05, "run_stage_05", _fail_if_called("stage_05"))

    result = workflow.run_workflow(SAMPLE_ISSUE)

    assert result["failed_at"] == "stage_01"
    assert result["error"] == "boom"
    assert result["stage_01"] is None
    assert result["stage_05"] is None


def test_stage_03_failure_stops_before_stage_04_and_05(monkeypatch):
    monkeypatch.setattr(workflow.stage_01, "run_stage_01", lambda issue: dict(STAGE_01_OUTPUT))
    monkeypatch.setattr(workflow.stage_02, "run_stage_02", lambda issue, s1: dict(STAGE_02_OUTPUT))
    monkeypatch.setattr(
        workflow.stage_03,
        "run_stage_03",
        lambda issue, s1, s2: (_ for _ in ()).throw(RuntimeError("design failed")),
    )
    monkeypatch.setattr(workflow.stage_04, "run_stage_04", _fail_if_called("stage_04"))
    monkeypatch.setattr(workflow.stage_05, "run_stage_05", _fail_if_called("stage_05"))

    result = workflow.run_workflow(SAMPLE_ISSUE)

    assert result["failed_at"] == "stage_03"
    assert result["error"] == "design failed"
    assert result["stage_01"] == STAGE_01_OUTPUT
    assert result["stage_02"] == STAGE_02_OUTPUT
    assert result["stage_03"] is None
    assert result["stage_04"] is None
    assert result["stage_05"] is None

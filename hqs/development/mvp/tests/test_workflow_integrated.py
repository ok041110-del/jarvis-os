"""01→05 Integrated Workflow(`hqs/development/workflow.py`) `run_workflow()`
검증.

각 Stage의 내부 로직은 재구현하지 않았으므로 여기서는 (a) 5개 Stage가
정확한 순서로, 문서화된 Input/Output Handover 그대로 호출되는지, (b)
중간 Stage 실패 시 이후 Stage가 호출되지 않고 즉시 중단하는지, (c)
Stage 05의 `verdict`가 재해석 없이 그대로 반환되는지만 mock으로
검증한다.
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


def _stub_happy_path(monkeypatch):
    calls = []

    def fake_stage_01(issue):
        calls.append(("stage_01", issue))
        return {"stage": 1}

    def fake_stage_02(issue, stage_01_context):
        calls.append(("stage_02", issue, stage_01_context))
        return {"stage": 2}

    def fake_stage_03(issue, stage_01_context, stage_02_output):
        calls.append(("stage_03", issue, stage_01_context, stage_02_output))
        return {"stage": 3}

    def fake_stage_04(issue, stage_03_output, expose_target=False):
        calls.append(("stage_04", issue, stage_03_output, expose_target))
        return {"stage": 4}

    def fake_stage_05(issue, stage_02_output, stage_03_output, stage_04_output):
        calls.append(("stage_05", issue, stage_02_output, stage_03_output, stage_04_output))
        return {"stage": 5, "verdict": "PASS"}

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
    assert calls[1] == ("stage_02", SAMPLE_ISSUE, {"stage": 1})
    assert calls[2] == ("stage_03", SAMPLE_ISSUE, {"stage": 1}, {"stage": 2})
    assert calls[3] == ("stage_04", SAMPLE_ISSUE, {"stage": 3}, False)
    assert calls[4] == ("stage_05", SAMPLE_ISSUE, {"stage": 2}, {"stage": 3}, {"stage": 4})

    assert result["stage_01"] == {"stage": 1}
    assert result["stage_02"] == {"stage": 2}
    assert result["stage_03"] == {"stage": 3}
    assert result["stage_04"] == {"stage": 4}
    assert result["stage_05"] == {"stage": 5, "verdict": "PASS"}
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
        lambda issue, s2, s3, s4: {"verdict": "PARTIAL", "extra": "untouched"},
    )

    result = workflow.run_workflow(SAMPLE_ISSUE)

    assert result["stage_05"] == {"verdict": "PARTIAL", "extra": "untouched"}


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
    monkeypatch.setattr(workflow.stage_01, "run_stage_01", lambda issue: {"stage": 1})
    monkeypatch.setattr(workflow.stage_02, "run_stage_02", lambda issue, s1: {"stage": 2})
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
    assert result["stage_01"] == {"stage": 1}
    assert result["stage_02"] == {"stage": 2}
    assert result["stage_03"] is None
    assert result["stage_04"] is None
    assert result["stage_05"] is None

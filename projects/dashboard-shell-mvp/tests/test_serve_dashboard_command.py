"""Dashboard Shell MVP — `/api/command`의 `execute_workflow`(Development HQ) 라우팅 검증.

`serve_dashboard.py`가 (a) `execute_workflow`+`development`일 때만 기존
`hqs/development/workflow.py::run_workflow()`를 호출해 Issue({"title", "description"})로
감싸고, (b) 결과를 재해석 없이 `CommandResult.detail`(JSON)로 그대로 반환하며, (c) 그 외
intent는 `resolver.resolve()`(무수정)로 그대로 넘기는지 확인한다. 실제 Engine 호출은 하지
않는다 — `sys.modules["workflow"]`에 가짜 `run_workflow()`를 심어 Stage 01~05 재실행 없이
배선만 검증한다.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import serve_dashboard as sd  # noqa: E402
from command import Command  # noqa: E402


def _happy_workflow_result():
    return {
        "stage_01": {"ok": True}, "stage_02": {"ok": True}, "stage_03": {"ok": True},
        "stage_04": {"ok": True}, "stage_05": {"verdict": "PASS"},
        "failed_at": None, "error": None,
    }


def _install_fake_workflow_module(monkeypatch, run_workflow_fn):
    fake_module = types.ModuleType("workflow")
    fake_module.run_workflow = run_workflow_fn
    monkeypatch.setitem(sys.modules, "workflow", fake_module)


def test_run_development_workflow_wraps_raw_input_as_minimal_issue(monkeypatch):
    captured = {}

    def fake_run_workflow(issue, expose_target=False):
        captured["issue"] = issue
        return _happy_workflow_result()

    _install_fake_workflow_module(monkeypatch, fake_run_workflow)

    result = sd._run_development_workflow("development workflow 실행해줘")

    assert result == _happy_workflow_result()
    assert captured["issue"] == {
        "title": "development workflow 실행해줘",
        "description": "development workflow 실행해줘",
    }


def test_run_development_workflow_wraps_unhandled_exception(monkeypatch):
    def raising_run_workflow(issue, expose_target=False):
        raise RuntimeError("boom")

    _install_fake_workflow_module(monkeypatch, raising_run_workflow)

    try:
        sd._run_development_workflow("development workflow 실행해줘")
        assert False, "WorkflowExecutionError를 기대했다"
    except sd.WorkflowExecutionError as exc:
        assert "boom" in str(exc)


def test_execute_workflow_development_returns_ok_with_full_result(monkeypatch):
    monkeypatch.setattr(sd, "_run_development_workflow", lambda raw_input: _happy_workflow_result())

    command = Command(raw_input="development workflow 실행해줘", intent="execute_workflow", target_hq="development")
    result = sd._resolve_or_execute(command)

    assert result.status == "ok"
    assert result.reason is None
    assert result.hq_identity == "Development HQ"
    assert json.loads(result.detail[0]) == _happy_workflow_result()


def test_execute_workflow_reports_stage_failure_without_reinterpretation(monkeypatch):
    failed_result = {**_happy_workflow_result(), "stage_03": None, "failed_at": "stage_03", "error": "boom"}
    monkeypatch.setattr(sd, "_run_development_workflow", lambda raw_input: failed_result)

    command = Command(raw_input="development workflow 실행해줘", intent="execute_workflow", target_hq="development")
    result = sd._resolve_or_execute(command)

    assert result.status == "ok"
    assert result.reason == "workflow_failed_at_stage_03"
    assert json.loads(result.detail[0]) == failed_result


def test_execute_workflow_import_or_run_failure_returns_invalid(monkeypatch):
    def raise_execution_error(raw_input):
        raise sd.WorkflowExecutionError("run_workflow 실행 실패: boom")

    monkeypatch.setattr(sd, "_run_development_workflow", raise_execution_error)

    command = Command(raw_input="development workflow 실행해줘", intent="execute_workflow", target_hq="development")
    result = sd._resolve_or_execute(command)

    assert result.status == "invalid"
    assert "run_workflow 실행 실패" in result.reason


def test_execute_workflow_non_development_hq_falls_back_to_resolve():
    """`execute_workflow`라도 target_hq가 development가 아니면 기존 resolve()(unsupported_intent)로 그대로 넘어간다."""
    command = Command(raw_input="Investment HQ 실행해줘", intent="execute_workflow", target_hq="investment")
    result = sd._resolve_or_execute(command)

    assert result.status == "invalid"
    assert result.reason == "unsupported_intent"


def test_show_status_still_uses_unmodified_resolver():
    command = Command(raw_input="Development HQ 상태를 보여줘", intent="show_status", target_hq="development")
    result = sd._resolve_or_execute(command)

    assert result.status == "ok"
    assert result.hq_identity == "Development HQ"

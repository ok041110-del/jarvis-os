"""Characterization tests for `mvp.workflow_hello_sdlc.run_hello_sdlc` (P1-2).

Production code(`workflow_hello_sdlc.py`)는 수정하지 않았다. 외부
의존성은 mock/stub한다.

**중요**: 이 함수의 실패 반환 shape은 다른 workflow_*.py들("Engine call
failed: {exc}" 문자열을 각 키에 채우는 방식)과 **다르다** — `None` 값 +
`status`/`error` 키를 쓴다. 이 차이를 있는 그대로 고정한다(P1-1 리팩토링
전에 이 비대칭 자체가 실제 현재 behavior임을 증명하기 위함).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp import workflow_hello_sdlc

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}


def test_happy_path_returns_complete_status_and_all_artifacts(monkeypatch):
    monkeypatch.setattr(
        workflow_hello_sdlc, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT"
    )
    monkeypatch.setattr(workflow_hello_sdlc, "design_agent_design", lambda issue, req: "DESIGN")
    monkeypatch.setattr(workflow_hello_sdlc, "backend_agent_code_generation", lambda design: "CODE")
    monkeypatch.setattr(workflow_hello_sdlc, "backend_agent_code_review", lambda code: "REVIEW")
    monkeypatch.setattr(
        workflow_hello_sdlc, "qa_agent_test_execution", lambda code, review: "TESTS"
    )

    result = workflow_hello_sdlc.run_hello_sdlc(SAMPLE_ISSUE)

    assert list(result.keys()) == ["planning", "design", "implementation", "validation", "status"]
    assert result == {
        "planning": "REQUIREMENT",
        "design": "DESIGN",
        "implementation": "CODE",
        "validation": {"code_review": "REVIEW", "test_execution": "TESTS"},
        "status": "Complete",
    }


def test_requirement_analysis_receives_raw_issue(monkeypatch):
    """이 함수는 Project Intelligence를 쓰지 않으므로, Planning은 원본
    issue를 그대로 받는다(Context enrichment 없음)."""
    seen = {}

    def fake_requirement(issue):
        seen["requirement_input"] = issue
        return "REQUIREMENT"

    monkeypatch.setattr(workflow_hello_sdlc, "requirements_agent_requirement_analysis", fake_requirement)
    monkeypatch.setattr(workflow_hello_sdlc, "design_agent_design", lambda issue, req: "DESIGN")
    monkeypatch.setattr(workflow_hello_sdlc, "backend_agent_code_generation", lambda design: "CODE")
    monkeypatch.setattr(workflow_hello_sdlc, "backend_agent_code_review", lambda code: "REVIEW")
    monkeypatch.setattr(
        workflow_hello_sdlc, "qa_agent_test_execution", lambda code, review: "TESTS"
    )

    workflow_hello_sdlc.run_hello_sdlc(SAMPLE_ISSUE)

    assert seen["requirement_input"] == SAMPLE_ISSUE


def test_engine_failure_returns_none_artifacts_with_failed_status_and_error(monkeypatch):
    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(workflow_hello_sdlc, "requirements_agent_requirement_analysis", raising_requirement)

    result = workflow_hello_sdlc.run_hello_sdlc(SAMPLE_ISSUE)

    assert result == {
        "planning": None,
        "design": None,
        "implementation": None,
        "validation": None,
        "status": "Failed",
        "error": "boom",
    }


def test_engine_failure_at_last_step_still_uses_none_shape(monkeypatch):
    monkeypatch.setattr(
        workflow_hello_sdlc, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT"
    )
    monkeypatch.setattr(workflow_hello_sdlc, "design_agent_design", lambda issue, req: "DESIGN")
    monkeypatch.setattr(workflow_hello_sdlc, "backend_agent_code_generation", lambda design: "CODE")
    monkeypatch.setattr(workflow_hello_sdlc, "backend_agent_code_review", lambda code: "REVIEW")

    def raising_test_execution(code, review):
        raise TimeoutError("timed out")

    monkeypatch.setattr(workflow_hello_sdlc, "qa_agent_test_execution", raising_test_execution)

    result = workflow_hello_sdlc.run_hello_sdlc(SAMPLE_ISSUE)

    assert result == {
        "planning": None,
        "design": None,
        "implementation": None,
        "validation": None,
        "status": "Failed",
        "error": "timed out",
    }

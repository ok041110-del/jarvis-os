"""Characterization tests for `mvp.workflow_project_intelligence`
(P1-2): `run_issue_to_planning`, `run_issue_to_design`.

Production code(`workflow_project_intelligence.py`)는 수정하지 않았다.
외부 의존성은 mock/stub한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp import workflow_project_intelligence as wpi

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}
SAMPLE_CONTEXT = {"relevant_documents": ["doc.md"], "directory_structure": ["ignored"]}


def _patch_context(monkeypatch):
    monkeypatch.setattr(wpi, "collect_relevant_context", lambda issue: SAMPLE_CONTEXT)


# --- run_issue_to_planning -------------------------------------------------


def test_planning_happy_path_returns_context_and_planning(monkeypatch):
    _patch_context(monkeypatch)
    monkeypatch.setattr(wpi, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT")

    result = wpi.run_issue_to_planning(SAMPLE_ISSUE)

    assert result == {"context": SAMPLE_CONTEXT, "planning": "REQUIREMENT"}


def test_planning_receives_enriched_issue_with_summarized_context(monkeypatch):
    _patch_context(monkeypatch)
    seen = {}

    def fake_requirement(issue):
        seen["input"] = issue
        return "REQUIREMENT"

    monkeypatch.setattr(wpi, "requirements_agent_requirement_analysis", fake_requirement)

    wpi.run_issue_to_planning(SAMPLE_ISSUE)

    assert "[Relevant Context]" in seen["input"]["description"]
    assert "relevant_documents: doc.md" in seen["input"]["description"]
    # directory_structure는 _summarize_context가 명시적으로 제외한다
    assert "directory_structure" not in seen["input"]["description"]


def test_planning_engine_failure_preserves_context_and_fills_error_string(monkeypatch):
    _patch_context(monkeypatch)

    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(wpi, "requirements_agent_requirement_analysis", raising_requirement)

    result = wpi.run_issue_to_planning(SAMPLE_ISSUE)

    assert result == {"context": SAMPLE_CONTEXT, "planning": "Engine call failed: boom"}


# --- run_issue_to_design -----------------------------------------------------


def test_design_happy_path_returns_context_planning_and_design(monkeypatch):
    _patch_context(monkeypatch)
    monkeypatch.setattr(wpi, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT")
    monkeypatch.setattr(wpi, "design_agent_design", lambda issue, req: "DESIGN")

    result = wpi.run_issue_to_design(SAMPLE_ISSUE)

    assert result == {"context": SAMPLE_CONTEXT, "planning": "REQUIREMENT", "design": "DESIGN"}


def test_design_receives_enriched_issue_not_original(monkeypatch):
    """`run_issue_to_design`의 계약(모듈 docstring): Planning과 Design
    양쪽 모두 동일한(enriched) Issue를 받는다 — `workflow_artifact_flow`/
    `workflow_0008`이 Design에 원본 Issue를 넘기는 것과 다른 지점이다."""
    _patch_context(monkeypatch)
    seen = {}

    monkeypatch.setattr(wpi, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT")

    def fake_design(issue, req):
        seen["design_input"] = issue
        return "DESIGN"

    monkeypatch.setattr(wpi, "design_agent_design", fake_design)

    wpi.run_issue_to_design(SAMPLE_ISSUE)

    assert "[Relevant Context]" in seen["design_input"]["description"]
    assert seen["design_input"] != SAMPLE_ISSUE


def test_design_engine_failure_preserves_context_and_fills_both_errors(monkeypatch):
    _patch_context(monkeypatch)

    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(wpi, "requirements_agent_requirement_analysis", raising_requirement)

    result = wpi.run_issue_to_design(SAMPLE_ISSUE)

    assert result == {
        "context": SAMPLE_CONTEXT,
        "planning": "Engine call failed: boom",
        "design": "Engine call failed: boom",
    }


def test_design_engine_failure_at_design_step(monkeypatch):
    _patch_context(monkeypatch)
    monkeypatch.setattr(wpi, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT")

    def raising_design(issue, req):
        raise TimeoutError("timed out")

    monkeypatch.setattr(wpi, "design_agent_design", raising_design)

    result = wpi.run_issue_to_design(SAMPLE_ISSUE)

    assert result == {
        "context": SAMPLE_CONTEXT,
        "planning": "Engine call failed: timed out",
        "design": "Engine call failed: timed out",
    }


# --- helpers -----------------------------------------------------------------


def test_summarize_context_excludes_directory_structure_and_empty_categories():
    context = {"relevant_documents": ["a.md", "b.md"], "relevant_code": [], "directory_structure": ["x"]}
    summary = wpi._summarize_context(context)
    assert "relevant_documents: a.md, b.md" in summary
    assert "relevant_code" not in summary
    assert "directory_structure" not in summary


def test_summarize_context_all_empty_returns_placeholder():
    assert wpi._summarize_context({"relevant_documents": []}) == "(관련 자료 없음)"

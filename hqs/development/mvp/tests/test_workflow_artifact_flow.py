"""Characterization tests for `mvp.workflow_artifact_flow.run_issue_to_implementation`
(P1-2).

Production code(`workflow_artifact_flow.py`)는 수정하지 않았다. 외부
의존성은 mock/stub한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp import workflow_artifact_flow

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}
SAMPLE_CONTEXT = {"relevant_documents": ["doc.md"]}
SAMPLE_ENRICHED_ISSUE = {**SAMPLE_ISSUE, "description": "Do the thing.\n\n[Relevant Context]\ndoc.md"}


def _patch_pre_try_deps(monkeypatch):
    monkeypatch.setattr(
        workflow_artifact_flow, "collect_relevant_context", lambda issue: SAMPLE_CONTEXT
    )
    monkeypatch.setattr(
        workflow_artifact_flow, "_enrich_issue", lambda issue, context: SAMPLE_ENRICHED_ISSUE
    )


def test_happy_path_returns_all_four_keys_in_order(monkeypatch):
    _patch_pre_try_deps(monkeypatch)
    monkeypatch.setattr(
        workflow_artifact_flow, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT"
    )
    monkeypatch.setattr(workflow_artifact_flow, "design_agent_design", lambda issue, req: "DESIGN")
    monkeypatch.setattr(
        workflow_artifact_flow, "backend_agent_code_generation", lambda design: "CODE"
    )

    result = workflow_artifact_flow.run_issue_to_implementation(SAMPLE_ISSUE)

    assert list(result.keys()) == ["context", "planning", "design", "implementation"]
    assert result == {
        "context": SAMPLE_CONTEXT,
        "planning": "REQUIREMENT",
        "design": "DESIGN",
        "implementation": "CODE",
    }


def test_design_receives_original_issue_not_enriched(monkeypatch):
    """Docstring 계약: Design에는 Context가 섞이지 않은 원본 Issue를
    그대로 넘긴다."""
    _patch_pre_try_deps(monkeypatch)
    seen = {}

    def fake_requirement(issue):
        seen["requirement_input"] = issue
        return "REQUIREMENT"

    def fake_design(issue, req):
        seen["design_input"] = issue
        return "DESIGN"

    monkeypatch.setattr(
        workflow_artifact_flow, "requirements_agent_requirement_analysis", fake_requirement
    )
    monkeypatch.setattr(workflow_artifact_flow, "design_agent_design", fake_design)
    monkeypatch.setattr(
        workflow_artifact_flow, "backend_agent_code_generation", lambda design: "CODE"
    )

    workflow_artifact_flow.run_issue_to_implementation(SAMPLE_ISSUE)

    assert seen["requirement_input"] == SAMPLE_ENRICHED_ISSUE
    assert seen["design_input"] == SAMPLE_ISSUE


def test_engine_failure_preserves_precomputed_context_and_fills_error(monkeypatch):
    _patch_pre_try_deps(monkeypatch)

    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        workflow_artifact_flow, "requirements_agent_requirement_analysis", raising_requirement
    )

    result = workflow_artifact_flow.run_issue_to_implementation(SAMPLE_ISSUE)

    assert result == {
        "context": SAMPLE_CONTEXT,
        "planning": "Engine call failed: boom",
        "design": "Engine call failed: boom",
        "implementation": "Engine call failed: boom",
    }


def test_engine_failure_at_last_step_still_produces_full_error_shape(monkeypatch):
    _patch_pre_try_deps(monkeypatch)
    monkeypatch.setattr(
        workflow_artifact_flow, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT"
    )
    monkeypatch.setattr(workflow_artifact_flow, "design_agent_design", lambda issue, req: "DESIGN")

    def raising_code_generation(design):
        raise TimeoutError("timed out")

    monkeypatch.setattr(
        workflow_artifact_flow, "backend_agent_code_generation", raising_code_generation
    )

    result = workflow_artifact_flow.run_issue_to_implementation(SAMPLE_ISSUE)

    assert list(result.keys()) == ["context", "planning", "design", "implementation"]
    assert result["context"] == SAMPLE_CONTEXT
    assert result["implementation"] == "Engine call failed: timed out"

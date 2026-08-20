"""Characterization tests for `mvp.workflow_0009` (P1-2):
`run_issue_to_planning_with_bundle`, `run_comparison`.

Production code(`workflow_0009.py`)는 수정하지 않았다. 외부 의존성은
mock/stub한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp import workflow_0009

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}
SAMPLE_BUNDLE = {
    "issue": SAMPLE_ISSUE,
    "goal": "Ship the thing.",
    "relevant_documents": [],
    "relevant_code": [],
    "relevant_observations": [],
    "relevant_decisions": [],
    "known_constraints": [],
    "open_questions": [],
}


def test_happy_path_returns_bundle_and_planning(monkeypatch):
    monkeypatch.setattr(workflow_0009, "build_context_bundle", lambda issue: SAMPLE_BUNDLE)
    monkeypatch.setattr(
        workflow_0009, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT"
    )

    result = workflow_0009.run_issue_to_planning_with_bundle(SAMPLE_ISSUE)

    assert result == {"context_bundle": SAMPLE_BUNDLE, "planning": "REQUIREMENT"}


def test_engine_failure_preserves_bundle_and_fills_planning_error(monkeypatch):
    monkeypatch.setattr(workflow_0009, "build_context_bundle", lambda issue: SAMPLE_BUNDLE)

    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(workflow_0009, "requirements_agent_requirement_analysis", raising_requirement)

    result = workflow_0009.run_issue_to_planning_with_bundle(SAMPLE_ISSUE)

    assert result == {
        "context_bundle": SAMPLE_BUNDLE,
        "planning": "Engine call failed: boom",
    }


def test_render_context_bundle_includes_all_sections():
    rendered = workflow_0009._render_context_bundle(SAMPLE_BUNDLE)

    for heading in [
        "## Issue",
        "## Goal",
        "## Relevant Documents",
        "## Relevant Code",
        "## Relevant Observations",
        "## Relevant Decisions",
        "## Known Constraints",
        "## Open Questions",
    ]:
        assert heading in rendered


def test_render_context_bundle_empty_lists_render_placeholder():
    rendered = workflow_0009._render_context_bundle(SAMPLE_BUNDLE)
    assert rendered.count("- (없음)") == 6  # 6 of the 8 sections are empty lists in the fixture


def test_run_comparison_assembles_flat_and_bundled_results(monkeypatch):
    def fake_flat(issue):
        return {"context": {"a": 1}, "planning": "FLAT_PLANNING"}

    def fake_bundled(issue):
        return {"context_bundle": SAMPLE_BUNDLE, "planning": "BUNDLED_PLANNING"}

    monkeypatch.setattr(workflow_0009, "run_issue_to_planning", fake_flat)
    monkeypatch.setattr(workflow_0009, "run_issue_to_planning_with_bundle", fake_bundled)

    result = workflow_0009.run_comparison(SAMPLE_ISSUE)

    assert result == {
        "flat_context_planning": "FLAT_PLANNING",
        "context_bundle_planning": "BUNDLED_PLANNING",
        "context_bundle": SAMPLE_BUNDLE,
    }

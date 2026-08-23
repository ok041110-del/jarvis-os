"""Stage 02(Planning & Specification) `run_stage_02()` 검증 (ADR-0008,
`stages/02_planning_specification/VALIDATION.md`).

`requirements_agent_requirement_analysis`는 재구현하지 않았으므로 여기서는
(a) Skeleton 추출이 Stage 01 Context를 정확히 반영하는지, (b) Skeleton이
반영된 Issue가 실제로 Engine에 전달되는지, (c) 기존 오류 포맷 유지 여부만
mock으로 검증한다.
"""

import importlib.util
import sys
from pathlib import Path

_STAGE_02_PATH = (
    Path(__file__).resolve().parents[2] / "stages" / "02_planning_specification" / "stage_02.py"
)
_spec = importlib.util.spec_from_file_location("stage_02", _STAGE_02_PATH)
stage_02 = importlib.util.module_from_spec(_spec)
sys.modules["stage_02"] = stage_02
_spec.loader.exec_module(stage_02)

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}

SAMPLE_STAGE_01_CONTEXT = {
    "directory_structure": ["hqs/development/mvp/"],
    "context_bundle": {
        "issue": SAMPLE_ISSUE,
        "goal": "Sample Issue",
        "relevant_documents": ["docs/01_mvp/MVP.md"],
        "relevant_code": ["hqs/development/mvp/agents.py"],
        "relevant_observations": [],
        "relevant_decisions": ["docs/governance/adc/ADC-0005.md"],
        "known_constraints": ["docs/governance/rt/RT-0001.md"],
        "open_questions": ["docs/governance/rt/RT-0001.md: 미해결 항목"],
    },
    "candidate_index": "FILE: hqs/development/mvp/agents.py\nFUNCTION: ...",
    "target": None,
    "dependency_closure": None,
}

EMPTY_CONTEXT_BUNDLE = {
    "issue": SAMPLE_ISSUE,
    "goal": "Sample Issue",
    "relevant_documents": [],
    "relevant_code": [],
    "relevant_observations": [],
    "relevant_decisions": [],
    "known_constraints": [],
    "open_questions": [],
}


# --- Skeleton 추출(Capability 1) --------------------------------------------


def test_skeleton_reflects_stage_01_context():
    skeleton = stage_02._structure_from_context(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert skeleton["problem_definition"] == "Sample Issue: Do the thing."
    assert skeleton["constraints"] == ["docs/governance/rt/RT-0001.md"]
    assert skeleton["risks"] == ["docs/governance/rt/RT-0001.md: 미해결 항목"]
    assert skeleton["scope_candidates"] == ["hqs/development/mvp/agents.py"]


def test_skeleton_handles_empty_context_bundle():
    empty_stage_01_context = {**SAMPLE_STAGE_01_CONTEXT, "context_bundle": EMPTY_CONTEXT_BUNDLE}

    skeleton = stage_02._structure_from_context(SAMPLE_ISSUE, empty_stage_01_context)

    assert skeleton["constraints"] == []
    assert skeleton["risks"] == []
    assert skeleton["scope_candidates"] == []


# --- run_stage_02(Capability 1 + 2 통합) ------------------------------------


def test_run_stage_02_happy_path_returns_skeleton_and_specification(monkeypatch):
    monkeypatch.setattr(
        stage_02, "requirements_agent_requirement_analysis", lambda issue: "SPECIFICATION"
    )

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert result["specification"] == "SPECIFICATION"
    assert result["skeleton"]["constraints"] == ["docs/governance/rt/RT-0001.md"]


def test_engine_receives_issue_enriched_with_skeleton(monkeypatch):
    seen = {}

    def fake_requirement(issue):
        seen["input"] = issue
        return "SPECIFICATION"

    monkeypatch.setattr(stage_02, "requirements_agent_requirement_analysis", fake_requirement)

    stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    description = seen["input"]["description"]
    assert "[Specification Skeleton]" in description
    assert "docs/governance/rt/RT-0001.md" in description
    assert "hqs/development/mvp/agents.py" in description


def test_engine_failure_preserves_skeleton_and_fills_error_string(monkeypatch):
    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(stage_02, "requirements_agent_requirement_analysis", raising_requirement)

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert result["specification"] == "Engine call failed: boom"
    assert result["skeleton"]["constraints"] == ["docs/governance/rt/RT-0001.md"]

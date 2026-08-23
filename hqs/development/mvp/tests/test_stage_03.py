"""Stage 03(Architecture / Design) `run_stage_03()` 검증 (ADR-0008,
`stages/03_architecture_design/VALIDATION.md`).

`design_agent_design`은 재구현하지 않았으므로 여기서는 (a) Skeleton
추출이 Stage 01/02 Output을 정확히 반영하는지, (b) 골격+Specification이
반영된 `requirement`가 실제로 Engine에 전달되는지, (c) 기존 오류 포맷
유지 여부만 mock으로 검증한다.
"""

import importlib.util
import sys
from pathlib import Path

_STAGE_03_PATH = (
    Path(__file__).resolve().parents[2] / "stages" / "03_architecture_design" / "stage_03.py"
)
_spec = importlib.util.spec_from_file_location("stage_03", _STAGE_03_PATH)
stage_03 = importlib.util.module_from_spec(_spec)
sys.modules["stage_03"] = stage_03
_spec.loader.exec_module(stage_03)

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}

SAMPLE_STAGE_01_CONTEXT = {
    "directory_structure": ["hqs/development/mvp/"],
    "context_bundle": {},
    "candidate_index": "FILE: hqs/development/mvp/agents.py\nFUNCTION: def design_agent_design(...)",
    "target": None,
    "dependency_closure": None,
}

SAMPLE_STAGE_02_OUTPUT = {
    "skeleton": {
        "problem_definition": "Sample Issue: Do the thing.",
        "constraints": ["docs/governance/rt/RT-0001.md"],
        "risks": ["docs/governance/rt/RT-0001.md: 미해결 항목"],
        "scope_candidates": ["hqs/development/mvp/agents.py"],
    },
    "specification": "SPECIFICATION TEXT",
}

EMPTY_STAGE_02_OUTPUT = {
    "skeleton": {
        "problem_definition": "Sample Issue: Do the thing.",
        "constraints": [],
        "risks": [],
        "scope_candidates": [],
    },
    "specification": "SPECIFICATION TEXT",
}


# --- Skeleton 추출(Capability 1) --------------------------------------------


def test_skeleton_reflects_stage_01_and_stage_02_output():
    skeleton = stage_03._structure_from_specification(SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_02_OUTPUT)

    assert skeleton["component_candidates"] == SAMPLE_STAGE_01_CONTEXT["candidate_index"]
    assert skeleton["scope_candidates"] == ["hqs/development/mvp/agents.py"]
    assert skeleton["constraints"] == ["docs/governance/rt/RT-0001.md"]
    assert skeleton["risks"] == ["docs/governance/rt/RT-0001.md: 미해결 항목"]


def test_skeleton_handles_empty_stage_02_output():
    skeleton = stage_03._structure_from_specification(SAMPLE_STAGE_01_CONTEXT, EMPTY_STAGE_02_OUTPUT)

    assert skeleton["constraints"] == []
    assert skeleton["risks"] == []
    assert skeleton["scope_candidates"] == []


# --- run_stage_03(Capability 1 + 2 통합) ------------------------------------


def test_run_stage_03_happy_path_returns_skeleton_and_design(monkeypatch):
    monkeypatch.setattr(stage_03, "design_agent_design", lambda issue, requirement: "DESIGN")

    result = stage_03.run_stage_03(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_02_OUTPUT)

    assert result["design"] == "DESIGN"
    assert result["skeleton"]["scope_candidates"] == ["hqs/development/mvp/agents.py"]


def test_engine_receives_requirement_enriched_with_specification_and_skeleton(monkeypatch):
    seen = {}

    def fake_design(issue, requirement):
        seen["issue"] = issue
        seen["requirement"] = requirement
        return "DESIGN"

    monkeypatch.setattr(stage_03, "design_agent_design", fake_design)

    stage_03.run_stage_03(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_02_OUTPUT)

    requirement = seen["requirement"]
    assert "SPECIFICATION TEXT" in requirement
    assert "[Architecture Design Skeleton]" in requirement
    assert "hqs/development/mvp/agents.py" in requirement
    assert "docs/governance/rt/RT-0001.md" in requirement
    assert seen["issue"] == SAMPLE_ISSUE


def test_engine_failure_preserves_skeleton_and_fills_error_string(monkeypatch):
    def raising_design(issue, requirement):
        raise RuntimeError("boom")

    monkeypatch.setattr(stage_03, "design_agent_design", raising_design)

    result = stage_03.run_stage_03(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT, SAMPLE_STAGE_02_OUTPUT)

    assert result["design"] == "Engine call failed: boom"
    assert result["skeleton"]["scope_candidates"] == ["hqs/development/mvp/agents.py"]

"""Stage 01 PRD/Specification Synthesis 검증(`stages/01_context_analysis/
prd_synthesis.py`, RFC-0034/ADC-0037/ADR-0022) — Structured Understanding +
Repository Context를 종합해 기존 Requirement Agent를 정확히 1회 호출하는지,
Engine 실패 시 오류 포맷을 유지하는지 mock으로 검증한다."""

import importlib.util
import sys
from pathlib import Path

_PRD_SYNTHESIS_PATH = Path(__file__).resolve().parents[2] / "stages" / "01_context_analysis" / "prd_synthesis.py"
_spec = importlib.util.spec_from_file_location("prd_synthesis", _PRD_SYNTHESIS_PATH)
prd_synthesis = importlib.util.module_from_spec(_spec)
sys.modules["prd_synthesis"] = prd_synthesis
_spec.loader.exec_module(prd_synthesis)

SAMPLE_ISSUE = {"title": "Add caching", "description": "Cache expensive lookups."}

SAMPLE_CONTEXT_BUNDLE = {
    "issue": SAMPLE_ISSUE,
    "goal": "Add caching",
    "relevant_documents": [],
    "relevant_code": ["hqs/development/mvp/engine.py"],
    "relevant_observations": [],
    "relevant_decisions": [],
    "known_constraints": ["docs/governance/rt/RT-0001.md"],
    "open_questions": ["docs/governance/rt/RT-0001.md: 미해결 항목"],
}

SAMPLE_STRUCTURED_UNDERSTANDING = {
    "intent": {"action": "add", "target": "cache", "domain": "perf", "explicit_intent": "speed up", "confidence": 0.9},
    "goal": {"desired_outcome": "faster reads", "success_direction": "less latency", "underlying_goal": "scale", "confidence": 0.8},
    "requirement": {
        "functional_requirements": ["cache reads"], "non_functional_requirements": ["low latency"],
        "constraints": [], "scope_candidates": ["caching"], "confidence": 0.7,
    },
    "ambiguity": {
        "ambiguous_points": [], "missing_information": [], "conflicting_interpretations": [],
        "unresolved_questions": ["which cache backend?"], "confidence": 0.6,
    },
    "status": "OK",
    "conflicts": [],
    "missing_agents": [],
    "overall_confidence": 0.75,
    "search_specification": {"keywords": [], "scope_candidates": []},
}


def test_synthesize_prd_calls_requirement_agent_exactly_once(monkeypatch):
    calls = []

    def fake_requirement_agent(issue):
        calls.append(issue)
        return "PRD TEXT"

    monkeypatch.setattr(prd_synthesis, "requirements_agent_requirement_analysis", fake_requirement_agent)

    result = prd_synthesis.synthesize_prd(
        issue=SAMPLE_ISSUE,
        structured_understanding=SAMPLE_STRUCTURED_UNDERSTANDING,
        context_bundle=SAMPLE_CONTEXT_BUNDLE,
        directory_structure=["hqs/development/mvp/"],
        candidate_index="FILE: hqs/development/mvp/engine.py\nFUNCTION: def call_engine(prompt): ...",
    )

    assert len(calls) == 1
    assert result["specification"] == "PRD TEXT"


def test_synthesize_prd_skeleton_reflects_context_bundle(monkeypatch):
    monkeypatch.setattr(prd_synthesis, "requirements_agent_requirement_analysis", lambda issue: "PRD TEXT")

    result = prd_synthesis.synthesize_prd(
        issue=SAMPLE_ISSUE,
        structured_understanding=SAMPLE_STRUCTURED_UNDERSTANDING,
        context_bundle=SAMPLE_CONTEXT_BUNDLE,
        directory_structure=[],
        candidate_index="",
    )

    assert result["skeleton"]["constraints"] == ["docs/governance/rt/RT-0001.md"]
    assert result["skeleton"]["risks"] == ["docs/governance/rt/RT-0001.md: 미해결 항목"]
    assert result["skeleton"]["scope_candidates"] == ["hqs/development/mvp/engine.py"]


def test_synthesize_prd_input_includes_structured_understanding_not_reasoned_again(monkeypatch):
    """PRD 생성이 Structured Understanding을 재추론하지 않고 그대로
    직렬화해 Engine에 전달하는지(Synthesis) 확인한다."""
    seen = {}

    def fake_requirement_agent(issue):
        seen["description"] = issue["description"]
        return "PRD TEXT"

    monkeypatch.setattr(prd_synthesis, "requirements_agent_requirement_analysis", fake_requirement_agent)

    prd_synthesis.synthesize_prd(
        issue=SAMPLE_ISSUE,
        structured_understanding=SAMPLE_STRUCTURED_UNDERSTANDING,
        context_bundle=SAMPLE_CONTEXT_BUNDLE,
        directory_structure=["hqs/development/mvp/"],
        candidate_index="FILE: hqs/development/mvp/engine.py",
    )

    description = seen["description"]
    assert "action=add" in description
    assert "desired_outcome=faster reads" in description
    assert "which cache backend?" in description
    assert "hqs/development/mvp/" in description


def test_synthesize_prd_engine_failure_preserves_skeleton_and_fills_error_string(monkeypatch):
    def raising_requirement_agent(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(prd_synthesis, "requirements_agent_requirement_analysis", raising_requirement_agent)

    result = prd_synthesis.synthesize_prd(
        issue=SAMPLE_ISSUE,
        structured_understanding=SAMPLE_STRUCTURED_UNDERSTANDING,
        context_bundle=SAMPLE_CONTEXT_BUNDLE,
        directory_structure=[],
        candidate_index="",
    )

    assert result["specification"] == "Engine call failed: boom"
    assert result["skeleton"]["constraints"] == ["docs/governance/rt/RT-0001.md"]


def test_synthesize_prd_handles_missing_agent_results_gracefully(monkeypatch):
    """Reasoning이 일부/전부 실패해도(INSUFFICIENT) 크래시하지 않고
    '(unknown)'/'(없음)' 표시로 진행한다."""
    monkeypatch.setattr(prd_synthesis, "requirements_agent_requirement_analysis", lambda issue: "PRD TEXT")
    empty_understanding = {
        "intent": None, "goal": None, "requirement": None, "ambiguity": None,
        "status": "INSUFFICIENT", "conflicts": [], "missing_agents": ["intent", "goal", "requirement", "ambiguity"],
        "overall_confidence": 0.0, "search_specification": {"keywords": [], "scope_candidates": []},
    }

    result = prd_synthesis.synthesize_prd(
        issue=SAMPLE_ISSUE,
        structured_understanding=empty_understanding,
        context_bundle={},
        directory_structure=[],
        candidate_index="",
    )

    assert result["skeleton"]["constraints"] == []
    assert isinstance(result["specification"], str)

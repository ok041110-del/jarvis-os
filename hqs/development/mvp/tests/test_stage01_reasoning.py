"""Stage 01 Multi-Agent Reasoning 검증(`stages/01_context_analysis/reasoning.py`)
— Intent/Goal/Requirement/Ambiguity Agent(mock Engine)와 Reasoning
Aggregator(schema validation/dedup/conflict/confidence/search spec)를
확인한다."""

import importlib.util
import json
import sys
from pathlib import Path

_REASONING_PATH = Path(__file__).resolve().parents[2] / "stages" / "01_context_analysis" / "reasoning.py"
_spec = importlib.util.spec_from_file_location("reasoning", _REASONING_PATH)
reasoning = importlib.util.module_from_spec(_spec)
sys.modules["reasoning"] = reasoning
_spec.loader.exec_module(reasoning)

import pytest

from mvp.parallel_runner import ParallelBatchResult, ParallelTaskResult, TaskStatus

SAMPLE_ISSUE = {"title": "Add caching", "description": "Cache expensive lookups."}


# --- Agents -------------------------------------------------------------------


def test_intent_agent_returns_parsed_structured_output(monkeypatch):
    payload = {
        "action": "add", "target": "cache layer", "domain": "performance",
        "explicit_intent": "reduce repeated lookups", "confidence": 0.9,
    }
    monkeypatch.setattr(reasoning, "call_engine", lambda prompt: json.dumps(payload))

    result = reasoning.intent_agent(SAMPLE_ISSUE)

    assert result == payload


def test_agent_raises_agent_output_error_when_no_json_found(monkeypatch):
    monkeypatch.setattr(reasoning, "call_engine", lambda prompt: "I cannot help with that.")

    with pytest.raises(reasoning.AgentOutputError):
        reasoning.goal_agent(SAMPLE_ISSUE)


def test_agent_raises_agent_output_error_when_missing_required_key(monkeypatch):
    incomplete = {"functional_requirements": [], "non_functional_requirements": []}
    monkeypatch.setattr(reasoning, "call_engine", lambda prompt: json.dumps(incomplete))

    with pytest.raises(reasoning.AgentOutputError):
        reasoning.requirement_agent(SAMPLE_ISSUE)


def test_agent_extracts_json_wrapped_in_markdown_fence(monkeypatch):
    payload = {
        "ambiguous_points": ["x"], "missing_information": [], "conflicting_interpretations": [],
        "unresolved_questions": [], "confidence": 0.5,
    }
    fenced = f"Here is the analysis:\n```json\n{json.dumps(payload)}\n```"
    monkeypatch.setattr(reasoning, "call_engine", lambda prompt: fenced)

    result = reasoning.ambiguity_agent(SAMPLE_ISSUE)

    assert result == payload


# --- Reasoning Aggregator -------------------------------------------------------


def _success(task_id, output):
    return ParallelTaskResult(task_id=task_id, status=TaskStatus.SUCCESS, output=output, duration=0.01, attempts=1)


def _failed(task_id):
    return ParallelTaskResult(task_id=task_id, status=TaskStatus.TIMEOUT, error="timed out", duration=1.0, attempts=1)


def _batch(*results):
    return ParallelBatchResult(results=list(results), started_at=0.0, completed_at=0.1, total_duration=0.1, summary={})


INTENT = {"action": "add", "target": "cache", "domain": "perf", "explicit_intent": "speed up", "confidence": 0.8}
GOAL = {"desired_outcome": "faster reads", "success_direction": "less latency", "underlying_goal": "scale", "confidence": 0.7}
REQUIREMENT = {
    "functional_requirements": ["cache reads", "CACHE READS"],
    "non_functional_requirements": [],
    "constraints": [],
    "scope_candidates": ["caching"],
    "confidence": 0.6,
}
AMBIGUITY = {
    "ambiguous_points": [], "missing_information": [], "conflicting_interpretations": [],
    "unresolved_questions": ["which cache backend?"], "confidence": 0.5,
}


def test_aggregate_all_success_returns_ok_status_with_confidence_average():
    batch = _batch(_success("intent", INTENT), _success("goal", GOAL), _success("requirement", REQUIREMENT), _success("ambiguity", AMBIGUITY))

    understanding = reasoning.aggregate_reasoning(batch)

    assert understanding["status"] == "OK"
    assert understanding["missing_agents"] == []
    assert understanding["overall_confidence"] == pytest.approx((0.8 + 0.7 + 0.6 + 0.5) / 4)


def test_aggregate_dedups_requirement_lists_case_insensitively():
    batch = _batch(_success("intent", INTENT), _success("goal", GOAL), _success("requirement", REQUIREMENT), _success("ambiguity", AMBIGUITY))

    understanding = reasoning.aggregate_reasoning(batch)

    assert understanding["requirement"]["functional_requirements"] == ["cache reads"]


def test_aggregate_one_agent_missing_is_partial_not_insufficient():
    batch = _batch(_success("intent", INTENT), _success("goal", GOAL), _success("requirement", REQUIREMENT), _failed("ambiguity"))

    understanding = reasoning.aggregate_reasoning(batch)

    assert understanding["status"] == "PARTIAL"
    assert understanding["missing_agents"] == ["ambiguity"]


def test_aggregate_two_or_more_missing_is_insufficient():
    batch = _batch(_success("intent", INTENT), _failed("goal"), _failed("requirement"), _success("ambiguity", AMBIGUITY))

    understanding = reasoning.aggregate_reasoning(batch)

    assert understanding["status"] == "INSUFFICIENT"
    assert set(understanding["missing_agents"]) == {"goal", "requirement"}


def test_aggregate_detects_conflict_and_does_not_arbitrarily_pick_a_winner():
    conflicting_requirement = dict(REQUIREMENT)
    conflicting_requirement["constraints"] = ["no add allowed in this module"]
    batch = _batch(
        _success("intent", INTENT), _success("goal", GOAL),
        _success("requirement", conflicting_requirement), _success("ambiguity", AMBIGUITY),
    )

    understanding = reasoning.aggregate_reasoning(batch)

    assert understanding["status"] == "CONFLICT"
    assert len(understanding["conflicts"]) == 1
    # Aggregator는 intent도 requirement도 "승자"로 고르지 않고 둘 다 보존한다.
    assert understanding["intent"] == INTENT
    assert understanding["requirement"]["constraints"] == ["no add allowed in this module"]


def test_search_specification_collects_keywords_and_scope_candidates():
    batch = _batch(_success("intent", INTENT), _success("goal", GOAL), _success("requirement", REQUIREMENT), _success("ambiguity", AMBIGUITY))

    understanding = reasoning.aggregate_reasoning(batch)

    spec = understanding["search_specification"]
    assert "add" in spec["keywords"]
    assert "cache" in spec["keywords"]
    assert spec["scope_candidates"] == ["caching"]

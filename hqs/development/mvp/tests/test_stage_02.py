"""Stage 02(Planning & Specification) `run_stage_02()` 검증(ADR-0008,
RFC-0035/ADC-0038/ADR-0023, `stages/02_planning_specification/VALIDATION.md`).

Stage 01의 PRD(`skeleton`/`specification`)는 재생성 없이 그대로 전달되고
(ADR-0022 유지), Task & Dependency Agent(mock) + Deterministic Layer가
`tasks`/`dependencies`/`plan`을 새로 산출하는지 확인한다. PRD Synthesis
자체의 검증은 `test_stage01_prd_synthesis.py` 참조."""

import importlib.util
import sys
from pathlib import Path

_STAGE_DIR = Path(__file__).resolve().parents[2] / "stages"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reasoning = _load("reasoning", _STAGE_DIR / "01_context_analysis" / "reasoning.py")
task_dependency_agent = _load(
    "task_dependency_agent", _STAGE_DIR / "02_planning_specification" / "task_dependency_agent.py"
)
planning_pipeline = _load(
    "planning_pipeline", _STAGE_DIR / "02_planning_specification" / "planning_pipeline.py"
)
stage_02 = _load("stage_02", _STAGE_DIR / "02_planning_specification" / "stage_02.py")

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}

SAMPLE_PRD = {
    "skeleton": {
        "problem_definition": "Sample Issue: Do the thing.",
        "constraints": ["docs/governance/rt/RT-0001.md"],
        "risks": ["docs/governance/rt/RT-0001.md: 미해결 항목"],
        "scope_candidates": ["hqs/development/mvp/agents.py"],
    },
    "specification": "SPECIFICATION TEXT",
}

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
    "prd": SAMPLE_PRD,
}


def _mock_agent_output(monkeypatch, tasks=None, dependencies=None):
    output = {"tasks": tasks if tasks is not None else [], "dependencies": dependencies if dependencies is not None else []}
    monkeypatch.setattr(
        task_dependency_agent, "decompose_tasks_and_dependencies", lambda specification: output
    )


def test_run_stage_02_passes_through_stage_01_prd_unchanged(monkeypatch):
    _mock_agent_output(monkeypatch)

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert result["skeleton"] == SAMPLE_PRD["skeleton"]
    assert result["specification"] == SAMPLE_PRD["specification"]


def test_run_stage_02_does_not_mutate_input_prd(monkeypatch):
    _mock_agent_output(monkeypatch)
    original = dict(SAMPLE_PRD)

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)
    result["specification"] = "MUTATED"

    assert SAMPLE_STAGE_01_CONTEXT["prd"] == original


def test_run_stage_02_output_matches_specification_result_contract_shape(monkeypatch):
    _mock_agent_output(monkeypatch)

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert set(result.keys()) == {"skeleton", "specification", "tasks", "dependencies", "plan"}
    assert set(result["skeleton"].keys()) == {
        "problem_definition", "constraints", "risks", "scope_candidates",
    }


def test_run_stage_02_runs_deterministic_layer_on_agent_output(monkeypatch):
    tasks = [
        {"id": "a", "title": "A", "description": "do a"},
        {"id": "b", "title": "B", "description": "do b"},
    ]
    dependencies = [{"task": "b", "depends_on": "a"}]
    _mock_agent_output(monkeypatch, tasks=tasks, dependencies=dependencies)

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert result["tasks"] == tasks
    assert result["dependencies"] == dependencies
    assert result["plan"] == {"execution_order": ["a", "b"]}


def test_run_stage_02_falls_back_to_empty_planning_on_agent_failure(monkeypatch):
    def _raise(specification):
        raise task_dependency_agent.AgentOutputError("boom")

    monkeypatch.setattr(task_dependency_agent, "decompose_tasks_and_dependencies", _raise)

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert result["skeleton"] == SAMPLE_PRD["skeleton"]
    assert result["specification"] == SAMPLE_PRD["specification"]
    assert result["tasks"] == []
    assert result["dependencies"] == []
    assert result["plan"] == {"execution_order": []}


def test_run_stage_02_falls_back_to_empty_planning_on_cycle(monkeypatch):
    tasks = [{"id": "a", "title": "A", "description": "do a"}, {"id": "b", "title": "B", "description": "do b"}]
    dependencies = [{"task": "a", "depends_on": "b"}, {"task": "b", "depends_on": "a"}]
    _mock_agent_output(monkeypatch, tasks=tasks, dependencies=dependencies)

    result = stage_02.run_stage_02(SAMPLE_ISSUE, SAMPLE_STAGE_01_CONTEXT)

    assert result["tasks"] == []
    assert result["dependencies"] == []
    assert result["plan"] == {"execution_order": []}

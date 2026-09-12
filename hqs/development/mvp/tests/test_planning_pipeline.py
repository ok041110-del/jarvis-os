"""Stage 02 Deterministic Layer(`planning_pipeline.py`) 검증(RFC-0035/
ADC-0038/ADR-0023 Decision 3) — Schema Validation, Dependency Graph
Validation, Cycle Detection, Topological Ordering, Plan Assembly를 각각
LLM 없이 순수 Python 데이터로 검증한다."""

import importlib.util
import sys
from pathlib import Path

import pytest

_PIPELINE_PATH = (
    Path(__file__).resolve().parents[2] / "stages" / "02_planning_specification" / "planning_pipeline.py"
)
_spec = importlib.util.spec_from_file_location("planning_pipeline", _PIPELINE_PATH)
planning_pipeline = importlib.util.module_from_spec(_spec)
sys.modules["planning_pipeline"] = planning_pipeline
_spec.loader.exec_module(planning_pipeline)


def _task(task_id):
    return {"id": task_id, "title": task_id, "description": f"do {task_id}"}


# --- Schema Validation --------------------------------------------------


def test_validate_schema_accepts_well_formed_output():
    agent_output = {
        "tasks": [_task("a"), _task("b")],
        "dependencies": [{"task": "b", "depends_on": "a"}],
    }
    planning_pipeline.validate_schema(agent_output)  # 예외 없이 통과


def test_validate_schema_rejects_missing_tasks_key():
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.validate_schema({"dependencies": []})


def test_validate_schema_rejects_task_missing_required_field():
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.validate_schema(
            {"tasks": [{"id": "a", "title": "a"}], "dependencies": []}
        )


def test_validate_schema_rejects_dependency_missing_required_field():
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.validate_schema(
            {"tasks": [_task("a")], "dependencies": [{"task": "a"}]}
        )


# --- Dependency Graph Validation (참조 무결성) ----------------------------


def test_validate_dependency_graph_rejects_unknown_reference():
    tasks = [_task("a")]
    dependencies = [{"task": "a", "depends_on": "missing"}]
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.validate_dependency_graph(tasks, dependencies)


def test_validate_dependency_graph_rejects_self_dependency():
    tasks = [_task("a")]
    dependencies = [{"task": "a", "depends_on": "a"}]
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.validate_dependency_graph(tasks, dependencies)


def test_validate_dependency_graph_accepts_valid_references():
    tasks = [_task("a"), _task("b")]
    dependencies = [{"task": "b", "depends_on": "a"}]
    planning_pipeline.validate_dependency_graph(tasks, dependencies)  # 예외 없이 통과


# --- Cycle Detection ------------------------------------------------------


def test_detect_cycles_raises_on_direct_cycle():
    tasks = [_task("a"), _task("b")]
    dependencies = [{"task": "a", "depends_on": "b"}, {"task": "b", "depends_on": "a"}]
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.detect_cycles(tasks, dependencies)


def test_detect_cycles_raises_on_indirect_cycle():
    tasks = [_task("a"), _task("b"), _task("c")]
    dependencies = [
        {"task": "a", "depends_on": "b"},
        {"task": "b", "depends_on": "c"},
        {"task": "c", "depends_on": "a"},
    ]
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.detect_cycles(tasks, dependencies)


def test_detect_cycles_passes_on_dag():
    tasks = [_task("a"), _task("b"), _task("c")]
    dependencies = [{"task": "b", "depends_on": "a"}, {"task": "c", "depends_on": "b"}]
    planning_pipeline.detect_cycles(tasks, dependencies)  # 예외 없이 통과


# --- Topological Ordering --------------------------------------------------


def test_topological_order_places_prerequisites_first():
    tasks = [_task("a"), _task("b"), _task("c")]
    dependencies = [{"task": "b", "depends_on": "a"}, {"task": "c", "depends_on": "b"}]
    order = planning_pipeline.topological_order(tasks, dependencies)
    assert order.index("a") < order.index("b") < order.index("c")


def test_topological_order_handles_independent_tasks():
    tasks = [_task("a"), _task("b")]
    order = planning_pipeline.topological_order(tasks, [])
    assert set(order) == {"a", "b"}


# --- Implementation Plan Assembly / Final Aggregation ----------------------


def test_assemble_plan_wraps_execution_order():
    assert planning_pipeline.assemble_plan(["a", "b"]) == {"execution_order": ["a", "b"]}


def test_run_planning_pipeline_full_flow():
    agent_output = {
        "tasks": [_task("a"), _task("b"), _task("c")],
        "dependencies": [{"task": "b", "depends_on": "a"}, {"task": "c", "depends_on": "b"}],
    }
    result = planning_pipeline.run_planning_pipeline(agent_output)

    assert result["tasks"] == agent_output["tasks"]
    assert result["dependencies"] == agent_output["dependencies"]
    assert result["plan"]["execution_order"] == ["a", "b", "c"]


def test_run_planning_pipeline_raises_on_cycle():
    agent_output = {
        "tasks": [_task("a"), _task("b")],
        "dependencies": [{"task": "a", "depends_on": "b"}, {"task": "b", "depends_on": "a"}],
    }
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.run_planning_pipeline(agent_output)


def test_run_planning_pipeline_raises_on_invalid_reference():
    agent_output = {
        "tasks": [_task("a")],
        "dependencies": [{"task": "a", "depends_on": "ghost"}],
    }
    with pytest.raises(planning_pipeline.PlanningPipelineError):
        planning_pipeline.run_planning_pipeline(agent_output)

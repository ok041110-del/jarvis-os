import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import planning_pipeline  # noqa: E402
import task_dependency_agent  # noqa: E402


def run_stage_02(issue: dict, stage_01_context: dict) -> dict:
    """Agent/Pipeline 실패 시에도 `tasks`/`dependencies`/`plan`을 빈 값으로
    채워 Contract 5-key를 항상 만족시킨다(`skeleton`/`specification`은 무관)."""
    prd = stage_01_context["prd"]
    skeleton = prd["skeleton"]
    specification = prd["specification"]

    try:
        agent_output = task_dependency_agent.decompose_tasks_and_dependencies(specification)
        planning_result = planning_pipeline.run_planning_pipeline(agent_output)
        tasks = planning_result["tasks"]
        dependencies = planning_result["dependencies"]
        plan = planning_result["plan"]
    except Exception:
        tasks = []
        dependencies = []
        plan = {"execution_order": []}

    return {
        "skeleton": skeleton,
        "specification": specification,
        "tasks": tasks,
        "dependencies": dependencies,
        "plan": plan,
    }

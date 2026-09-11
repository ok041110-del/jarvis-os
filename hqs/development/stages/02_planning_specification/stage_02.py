"""Stage 02: Planning & Specification 실행 진입점(ADR-0008 §4, ADR-0023).

Stage 01이 생성한 PRD(`skeleton`/`specification`)는 그대로 통과시키고
(ADR-0022 유지, 재생성하지 않음), Task & Dependency Agent(LLM 1회) +
Deterministic Layer(Schema/Graph Validation, Cycle Detection, Topological
Ordering, Plan Assembly)로 `tasks`/`dependencies`/`plan`을 새로 산출한다
(RFC-0035/ADC-0038/ADR-0023)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import planning_pipeline  # noqa: E402
import task_dependency_agent  # noqa: E402


def run_stage_02(issue: dict, stage_01_context: dict) -> dict:
    """`skeleton`/`specification`은 Stage 01의 `prd`를 그대로 전달받는다
    (재생성 없음, ADR-0022). Task & Dependency Agent 호출 또는 Deterministic
    Layer 검증이 실패해도 `skeleton`/`specification`은 영향받지 않고,
    `tasks`/`dependencies`/`plan`만 안전한 빈 값으로 채워 Contract의 5-key를
    항상 만족시킨다."""
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

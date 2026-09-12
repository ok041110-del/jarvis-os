"""Stage 02 Deterministic Layer — Task & Dependency Agent 출력을 LLM 호출
없이 코드로만 검증/정렬/조립한다(RFC-0035/ADC-0038/ADR-0023 Decision 3):
Schema Validation → Dependency Graph Validation → Cycle Detection →
Topological Ordering → Implementation Plan Assembly → Final Aggregation.
Cycle Detection은 구조적 무결성(순환 여부)만 보장하며, 의미적으로 잘못됐지만
순환이 아닌 의존관계는 걸러내지 못한다는 한계를 그대로 안는다(ADR-0023)."""


class PlanningPipelineError(ValueError):
    """Deterministic Layer의 어느 단계에서든 검증 실패 시 발생한다."""


def validate_schema(agent_output: dict) -> None:
    """`tasks`/`dependencies`가 존재하고 리스트이며, 각 항목이 필수 키를
    갖추고 있는지 확인한다(Task & Dependency Agent 출력의 구조 검증)."""
    if not isinstance(agent_output, dict):
        raise PlanningPipelineError("agent output is not a JSON object")

    tasks = agent_output.get("tasks")
    dependencies = agent_output.get("dependencies")

    if not isinstance(tasks, list):
        raise PlanningPipelineError("'tasks' must be a list")
    if not isinstance(dependencies, list):
        raise PlanningPipelineError("'dependencies' must be a list")

    for task in tasks:
        if not isinstance(task, dict):
            raise PlanningPipelineError(f"task entry is not an object: {task!r}")
        missing = [key for key in ("id", "title", "description") if key not in task]
        if missing:
            raise PlanningPipelineError(f"task {task!r} missing keys: {missing}")

    for edge in dependencies:
        if not isinstance(edge, dict):
            raise PlanningPipelineError(f"dependency entry is not an object: {edge!r}")
        missing = [key for key in ("task", "depends_on") if key not in edge]
        if missing:
            raise PlanningPipelineError(f"dependency {edge!r} missing keys: {missing}")


def validate_dependency_graph(tasks: list, dependencies: list) -> None:
    """Dependency edge가 참조하는 task id가 실제 존재하는지(참조 무결성),
    self-dependency가 없는지 확인한다."""
    task_ids = {task["id"] for task in tasks}

    for edge in dependencies:
        task_id, depends_on_id = edge["task"], edge["depends_on"]
        if task_id not in task_ids:
            raise PlanningPipelineError(f"dependency references unknown task: {task_id!r}")
        if depends_on_id not in task_ids:
            raise PlanningPipelineError(f"dependency references unknown task: {depends_on_id!r}")
        if task_id == depends_on_id:
            raise PlanningPipelineError(f"task cannot depend on itself: {task_id!r}")


def _adjacency(tasks: list, dependencies: list) -> dict:
    """task id -> depends_on id 목록(선행 task 목록)으로 그래프를 구성한다."""
    graph = {task["id"]: [] for task in tasks}
    for edge in dependencies:
        graph[edge["task"]].append(edge["depends_on"])
    return graph


def detect_cycles(tasks: list, dependencies: list) -> None:
    """DFS white/gray/black coloring으로 순환 의존관계를 탐지한다. 구조적
    무결성만 보장하며 의미적 오판은 걸러내지 못한다(ADR-0023 한계 인정)."""
    graph = _adjacency(tasks, dependencies)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {task_id: WHITE for task_id in graph}
    path: list = []

    def visit(node: str) -> None:
        color[node] = GRAY
        path.append(node)
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                cycle = path[path.index(neighbor):] + [neighbor]
                raise PlanningPipelineError(f"dependency cycle detected: {' -> '.join(cycle)}")
            if color[neighbor] == WHITE:
                visit(neighbor)
        path.pop()
        color[node] = BLACK

    for task_id in graph:
        if color[task_id] == WHITE:
            visit(task_id)


def topological_order(tasks: list, dependencies: list) -> list:
    """Kahn's algorithm으로 선행 task가 먼저 오는 실행 순서를 만든다.
    `detect_cycles`가 이미 순환 없음을 보장했다는 전제 위에서 동작한다."""
    graph = _adjacency(tasks, dependencies)
    in_degree = {task_id: len(depends_on) for task_id, depends_on in graph.items()}

    dependents: dict = {task_id: [] for task_id in graph}
    for task_id, depends_on in graph.items():
        for prerequisite in depends_on:
            dependents[prerequisite].append(task_id)

    queue = sorted(task_id for task_id, degree in in_degree.items() if degree == 0)
    order: list = []

    while queue:
        queue.sort()
        node = queue.pop(0)
        order.append(node)
        for dependent in dependents[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(graph):
        raise PlanningPipelineError("topological order incomplete — unresolved dependency structure")

    return order


def assemble_plan(execution_order: list) -> dict:
    """Topological Ordering 결과를 `ImplementationPlan` 형태로 조립한다."""
    return {"execution_order": execution_order}


def run_planning_pipeline(agent_output: dict) -> dict:
    """Deterministic Layer 전 구간을 순서대로 실행해 `tasks`/`dependencies`/
    `plan`을 반환한다(Final Aggregation)."""
    validate_schema(agent_output)
    tasks = agent_output["tasks"]
    dependencies = agent_output["dependencies"]

    validate_dependency_graph(tasks, dependencies)
    detect_cycles(tasks, dependencies)
    execution_order = topological_order(tasks, dependencies)
    plan = assemble_plan(execution_order)

    return {"tasks": tasks, "dependencies": dependencies, "plan": plan}

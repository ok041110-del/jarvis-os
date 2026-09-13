"""Stage 02 Deterministic Layer(RFC-0035/ADC-0038/ADR-0023 Decision 3) — LLM 호출 없이 코드로만 검증/정렬/조립한다. Cycle Detection은 구조적 무결성만 보장하며, 순환이 아닌 의미적 오류는 걸러내지 못한다(ADR-0023 한계)."""


class PlanningPipelineError(ValueError):
    pass


def validate_schema(agent_output: dict) -> None:
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
    graph = {task["id"]: [] for task in tasks}
    for edge in dependencies:
        graph[edge["task"]].append(edge["depends_on"])
    return graph


def detect_cycles(tasks: list, dependencies: list) -> None:
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
    return {"execution_order": execution_order}


def run_planning_pipeline(agent_output: dict) -> dict:
    validate_schema(agent_output)
    tasks = agent_output["tasks"]
    dependencies = agent_output["dependencies"]

    validate_dependency_graph(tasks, dependencies)
    detect_cycles(tasks, dependencies)
    execution_order = topological_order(tasks, dependencies)
    plan = assemble_plan(execution_order)

    return {"tasks": tasks, "dependencies": dependencies, "plan": plan}

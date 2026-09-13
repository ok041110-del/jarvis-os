"""Dashboard Observation — Task Registry를 읽기만 한다(Observe-only, async-command의 dashboard_view.py와 동일 원칙).

Task 표현 방식이 바뀌어도 Dashboard는 Registry 조회만 하면 된다는 것을 in-process 버전에서도 재확인한다.
"""

from __future__ import annotations

from inproc_case_b import Task, _TASK_REGISTRY


def list_running_tasks() -> list[Task]:
    return [t for t in _TASK_REGISTRY.values() if t.status == "RUNNING"]


def list_all_tasks() -> list[Task]:
    return list(_TASK_REGISTRY.values())

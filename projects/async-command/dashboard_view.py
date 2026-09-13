"""Dashboard Observation — Task Registry를 읽기만 한다.

Dashboard는 실행을 관리하지 않는다(작업 지시 §11: Dashboard = Observe, Command/Prototype Executor = Execute). 이 모듈은 `case_b_ command_task._TASK_REGISTRY`를 읽어 상태만 나열할 뿐, `start()`/ `refresh()`/`retry()`를 호출하지 않는다.
"""

from __future__ import annotations

from case_b_command_task import _TASK_REGISTRY, Task


def list_running_tasks() -> list[Task]:
    """읽기 전용 — Registry의 항목을 나열만 한다."""
    return [t for t in _TASK_REGISTRY.values() if t.status in ("PENDING", "RUNNING")]


def list_all_tasks() -> list[Task]:
    return list(_TASK_REGISTRY.values())

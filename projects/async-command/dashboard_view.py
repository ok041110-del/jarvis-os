"""Dashboard Observation — Task Registry를 읽기만 한다.

Dashboard는 실행을 관리하지 않는다 — `start()`/`refresh()`/`retry()`를 호출하지 않는다.
"""

from __future__ import annotations

from case_b_command_task import _TASK_REGISTRY, Task


def list_running_tasks() -> list[Task]:
    return [t for t in _TASK_REGISTRY.values() if t.status in ("PENDING", "RUNNING")]


def list_all_tasks() -> list[Task]:
    return list(_TASK_REGISTRY.values())

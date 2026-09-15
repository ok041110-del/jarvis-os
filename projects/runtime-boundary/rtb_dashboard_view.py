"""Dashboard Observation — Task Registry를 읽기만 한다(전략과 무관, 실행을 시작/재시도하지 않음).

Process Worker에서 나온 결과도 Task 객체에 반영되면 Dashboard 입장에서는 Thread 결과와 구분되지 않는다 — 둘 다 그냥 값이다.
"""

from __future__ import annotations

from rtb_task import Task, _REGISTRY


def list_running_tasks() -> list[Task]:
    return [t for t in _REGISTRY.values() if t.status in ("PENDING", "RUNNING")]


def list_all_tasks() -> list[Task]:
    return list(_REGISTRY.values())

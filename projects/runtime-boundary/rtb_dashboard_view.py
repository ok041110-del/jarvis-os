"""Dashboard Observation — Task Registry를 읽기만 한다(전략과 무관).

이전 두 Prototype과 동일한 원칙: Dashboard는 실행을 시작/재시도하지
않는다. 이 파일은 `rtb_task._REGISTRY`가 Thread 전략이든 Process
전략이든 상관없이 `task_id`/`status`/`result`라는 동일한 평면적
값으로 관찰 가능하다는 것을 확인한다 — Process Worker에서 나온
결과도 Task 객체에 반영되면 Dashboard 입장에서는 Thread와 구분되지
않는다(둘 다 그냥 값이다, pickled/unpickled 여부를 Dashboard가 알
필요 없음).
"""

from __future__ import annotations

from rtb_task import Task, _REGISTRY


def list_running_tasks() -> list[Task]:
    return [t for t in _REGISTRY.values() if t.status in ("PENDING", "RUNNING")]


def list_all_tasks() -> list[Task]:
    return list(_REGISTRY.values())

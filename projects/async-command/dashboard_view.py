"""Dashboard Observation — Task Registry를 읽기만 한다.

Dashboard는 실행을 관리하지 않는다(작업 지시 §11: Dashboard =
Observe, Command/Prototype Executor = Execute). 이 모듈은 `case_b_
command_task._TASK_REGISTRY`를 읽어 상태만 나열할 뿐, `start()`/
`refresh()`/`retry()`를 호출하지 않는다.

Case A(`case_a_command_only.py`)에는 이 관찰이 불가능하다 — Command
객체를 어딘가에서 계속 들고 있지 않으면 실행 중인 작업의 목록
자체를 얻을 방법이 없다(Registry가 없음). 이것이 Q5("Dashboard가
실행 중인 작업을 관찰해야 하는가")에 대한 실측 Evidence다.
"""

from __future__ import annotations

from case_b_command_task import _TASK_REGISTRY, Task


def list_running_tasks() -> list[Task]:
    """읽기 전용 — Registry의 항목을 나열만 한다."""
    return [t for t in _TASK_REGISTRY.values() if t.status in ("PENDING", "RUNNING")]


def list_all_tasks() -> list[Task]:
    return list(_TASK_REGISTRY.values())

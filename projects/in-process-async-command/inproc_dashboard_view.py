"""Dashboard Observation — Task Registry를 읽기만 한다.

`async-command` Prototype의 `dashboard_view.py`와 동일한 원칙: Dashboard는
실행을 시작/재시도하지 않는다(Observe-only). 이 파일은 subprocess
버전과 별개로 in-process Task Registry(`case_b_command_task._TASK_REGISTRY`)
를 관찰한다 — Task 표현 방식이 바뀌어도 Dashboard는 Registry 조회만
하면 된다는 것을 다시 확인한다.
"""

from __future__ import annotations

from inproc_case_b import Task, _TASK_REGISTRY


def list_running_tasks() -> list[Task]:
    return [t for t in _TASK_REGISTRY.values() if t.status == "RUNNING"]


def list_all_tasks() -> list[Task]:
    return list(_TASK_REGISTRY.values())

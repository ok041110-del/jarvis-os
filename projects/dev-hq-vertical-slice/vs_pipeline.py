"""Pipeline — Command → Task → Runtime → Dev HQ → Result 저장까지 연결한다.

Dashboard는 이 모듈을 거치지 않는다 — `vs_dashboard_view.py`는 Task
Registry와 Result Store를 직접 읽기만 한다(Observe-only, 작업 지시
§4). 이 모듈에는 Dashboard 관련 코드가 없다.

`rtb_task`/`rtb_runtime`(`runtime-boundary` Prototype, 이미 main에
병합됨)을 그대로 재사용한다 — 중복 구현하지 않는다.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_RUNTIME_BOUNDARY_DIR = _THIS_DIR.parents[0] / "runtime-boundary"
sys.path.insert(0, str(_THIS_DIR))
sys.path.insert(0, str(_RUNTIME_BOUNDARY_DIR))

import rtb_task as task  # noqa: E402

import vs_command as command  # noqa: E402
import vs_dev_hq_adapter as adapter  # noqa: E402
import vs_result_store as result_store  # noqa: E402

_STRATEGY = "process"  # 작업 지시 §3: Process 전략 우선 사용, 선택 API는 만들지 않는다


def submit(raw_input: str) -> task.Task:
    cmd = command.parse_command(raw_input)
    if cmd.action is None or not command.is_known_action(cmd.action):
        failed = task.Task(
            task_id=str(uuid.uuid4()), target=raw_input, strategy=_STRATEGY,
            status="FAILED", error="unknown_action",
        )
        task._REGISTRY[failed.task_id] = failed
        _maybe_persist(failed)
        return failed

    target = adapter.resolve_target(cmd.action)
    t = task.start(target, _STRATEGY)
    _maybe_persist(t)
    return t


def refresh(task_id: str) -> task.Task:
    t = task.refresh(task_id)
    _maybe_persist(t)
    return t


def _maybe_persist(t: task.Task) -> None:
    if t.status in ("COMPLETED", "FAILED"):
        result_store.save_result(t)

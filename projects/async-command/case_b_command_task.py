"""Case B — Command은 불변(요청 그 자체), Task가 실행 상태를 소유한다.

Case A의 Command는 실행 상태 때문에 frozen=True가 불가능했다 — Case B는 변하는 것(실행 상태)만 Task가 소유하게 해 이 문제가 해소되는지 검증한다.
"""

from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

_COMMAND_CONTRACT_DIR = Path(__file__).resolve().parents[1] / "command-contract"
sys.path.insert(0, str(_COMMAND_CONTRACT_DIR))

from resolver import _detect_hq  # noqa: E402  (기존 HQ 파싱 재사용)

import operation  # noqa: E402


@dataclass(frozen=True)
class Command:
    """불변 — Case A와 달리 실행 상태를 갖지 않는다."""

    raw_input: str
    target_hq: str | None


@dataclass
class Task:
    """가변 — 실행 상태(lifecycle)를 소유한다. `task_id`는 Command 객체 없이도 Registry에서 다시 찾을 수 있게 한다."""

    task_id: str
    command: Command
    execution_id: str | None = None
    status: str = "PENDING"  # PENDING | RUNNING | COMPLETED | FAILED
    result: str | None = None
    error: str | None = None


# Registry — Task를 Python 객체 참조 없이 task_id만으로 다시 찾을 수
# 있게 한다(Case A에는 이런 Command Registry가 없었다).
_TASK_REGISTRY: dict[str, Task] = {}


def start(raw_input: str, valid_path: bool = True) -> Task:
    target_hq = _detect_hq(raw_input)
    command = Command(raw_input=raw_input, target_hq=target_hq)
    task = Task(task_id=str(uuid.uuid4()), command=command)
    _TASK_REGISTRY[task.task_id] = task

    if target_hq is None:
        task.status = "FAILED"
        task.error = "unknown_hq"
        return task

    task.execution_id = operation.start_operation(target_hq, valid_path=valid_path)
    task.status = "RUNNING"
    return task


def get_task(task_id: str) -> Task:
    return _TASK_REGISTRY[task_id]


def refresh(task_id: str) -> Task:
    task = _TASK_REGISTRY[task_id]
    if task.execution_id is None:
        return task

    op_status = operation.poll(task.execution_id)
    if op_status.status == "RUNNING":
        task.status = "RUNNING"
    elif op_status.status == "COMPLETED":
        task.status = "COMPLETED"
        task.result = op_status.output_tail
    else:
        task.status = "FAILED"
        task.error = op_status.output_tail

    return task


def retry(task_id: str) -> Task:
    """실패한 Task를 같은 Command로 재실행한다 — Command가 불변이므로 원본 요청을 다시 조립할 필요가 없다."""

    old_task = _TASK_REGISTRY[task_id]
    if old_task.status != "FAILED":
        raise ValueError("retry는 FAILED 상태에서만 허용")

    new_task = Task(task_id=str(uuid.uuid4()), command=old_task.command)
    _TASK_REGISTRY[new_task.task_id] = new_task
    new_task.execution_id = operation.start_operation(old_task.command.target_hq, valid_path=True)
    new_task.status = "RUNNING"
    return new_task

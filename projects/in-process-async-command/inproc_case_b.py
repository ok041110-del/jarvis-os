"""Case B — Command는 불변, Task가 in-process 실행 lifecycle을 소유한다.

Command / Task 필드는 최소한으로 유지한다(작업 지시 §7) — task_id,
status, result, error만 사용한다. Result는 passed/failed 튜플로 표현
한다(operation.OperationStatus를 그대로 감싸지 않고 Task 자신의 최소
표현으로 압축 — Task가 Operation 세부 구현을 몰라도 되게 한다).
"""

from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

_COMMAND_CONTRACT_DIR = Path(__file__).resolve().parents[1] / "command-contract"
sys.path.insert(0, str(_COMMAND_CONTRACT_DIR))

from resolver import _detect_hq  # noqa: E402

import inproc_operation as operation  # noqa: E402


@dataclass(frozen=True)
class Command:
    raw_input: str
    target_hq: str | None


@dataclass
class Task:
    task_id: str
    command: Command
    execution_id: str | None = None
    status: str = "PENDING"
    result: tuple[int, int] | None = None  # (passed, failed)
    error: str | None = None


_TASK_REGISTRY: dict[str, Task] = {}


def start(raw_input: str, valid_path: bool = True) -> Task:
    command = Command(raw_input=raw_input, target_hq=_detect_hq(raw_input))
    task = Task(task_id=str(uuid.uuid4()), command=command)
    _TASK_REGISTRY[task.task_id] = task

    if command.target_hq is None:
        task.status = "FAILED"
        task.error = "unknown_hq"
        return task

    task.execution_id = operation.start_operation(command.target_hq, valid_path=valid_path)
    task.status = "RUNNING"
    return task


def get_task(task_id: str) -> Task:
    return _TASK_REGISTRY[task_id]


def refresh(task_id: str) -> Task:
    task = _TASK_REGISTRY[task_id]
    if task.execution_id is None or task.status != "RUNNING":
        return task
    op_status = operation.poll(task.execution_id)
    task.status = op_status.status
    if op_status.status == "COMPLETED":
        task.result = (op_status.passed, op_status.failed)
    elif op_status.status == "FAILED":
        task.error = f"return_code={op_status.return_code}"
    return task


def retry(task_id: str) -> Task:
    """원본 immutable Command를 재사용해 새 Task를 만든다 — Command
    자체는 변경하지 않는다(작업 지시 §17)."""

    old_task = _TASK_REGISTRY[task_id]
    new_task = Task(task_id=str(uuid.uuid4()), command=old_task.command)
    _TASK_REGISTRY[new_task.task_id] = new_task

    if old_task.command.target_hq is None:
        new_task.status = "FAILED"
        new_task.error = "unknown_hq"
        return new_task

    new_task.execution_id = operation.start_operation(old_task.command.target_hq, valid_path=True)
    new_task.status = "RUNNING"
    return new_task

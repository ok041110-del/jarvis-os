"""Task — Identity/Lifecycle 책임만 담당한다(Scheduling/Isolation은 rtb_runtime이 담당).

이 모듈은 `ThreadPoolExecutor`/`ProcessPoolExecutor`를 전혀 모른다 —
`rtb_runtime.start()`/`rtb_runtime.poll()`만 호출한다. Task가 아는
것은 "어떤 대상을, 어떤 전략으로, 실행했고, 지금 상태가 무엇인가"
뿐이다. 최소 필드만 사용한다(task_id, target, strategy, status,
result, error) — `context`/`priority` 등은 추가하지 않는다.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import rtb_runtime as runtime


@dataclass
class Task:
    task_id: str
    target: str
    strategy: str
    execution_id: str | None = None
    status: str = "PENDING"
    result: tuple[int, int] | None = None  # (passed, failed)
    error: str | None = None


_REGISTRY: dict[str, Task] = {}


def start(target: str, strategy: str) -> Task:
    task = Task(task_id=str(uuid.uuid4()), target=target, strategy=strategy)
    _REGISTRY[task.task_id] = task

    try:
        task.execution_id = runtime.start(strategy, target)
    except ValueError as exc:
        task.status = "FAILED"
        task.error = str(exc)
        return task

    _apply(task, runtime.poll(task.execution_id))
    return task


def get_task(task_id: str) -> Task:
    return _REGISTRY[task_id]


def refresh(task_id: str) -> Task:
    task = _REGISTRY[task_id]
    if task.execution_id is None or task.status not in ("PENDING", "RUNNING"):
        return task
    _apply(task, runtime.poll(task.execution_id))
    return task


def retry(task_id: str) -> Task:
    """원본 target/strategy를 그대로 재사용해 새 Task를 만든다 — 원본
    Task는 변경하지 않는다."""

    old_task = _REGISTRY[task_id]
    return start(old_task.target, old_task.strategy)


def _apply(task: Task, op_status: "runtime.OperationStatus") -> None:
    task.status = op_status.status
    if op_status.status == "COMPLETED":
        task.result = (op_status.passed, op_status.failed)
    elif op_status.status == "FAILED":
        task.error = f"return_code={op_status.return_code}"

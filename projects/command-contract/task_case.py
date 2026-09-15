"""Case B: User -> Command -> Task -> HQ.

Case A와 동일한 Command Resolution을 Task로 감싸, Task가 실제로 무엇을 추가하는지 관찰한다.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from command import Command, CommandResult
from resolver import resolve


@dataclass
class Task:
    """필드는 Case A 대비 "무엇이 추가로 필요한가"를 관찰하기 위한 최소 후보만 담는다."""

    task_id: str
    command: Command
    status: str = "pending"  # "pending" | "completed" | "failed"
    result: CommandResult | None = None


def run_via_task(raw_input: str, command: Command) -> Task:
    task = Task(task_id=str(uuid.uuid4()), command=command)
    task.result = resolve(command)
    task.status = "completed" if task.result.status == "ok" else "failed"
    return task

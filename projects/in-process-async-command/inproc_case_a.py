"""Case A — Command 하나에 in-process 실행 상태를 직접 담는다.

`async-command` Prototype의 Case A(subprocess 버전)와 동일한 질문을
in-process 실행에서 반복한다: Command가 실행 상태까지 스스로 표현할
수 있는가? 여기서는 mutable Command만 사용한다(frozen=True 불가 —
실행 도중 `status`/`result`가 바뀌어야 하므로).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_COMMAND_CONTRACT_DIR = Path(__file__).resolve().parents[1] / "command-contract"
sys.path.insert(0, str(_COMMAND_CONTRACT_DIR))

from resolver import _detect_hq  # noqa: E402

import inproc_operation as operation  # noqa: E402


@dataclass
class AsyncCommand:
    raw_input: str
    target_hq: str | None = None
    execution_id: str | None = None
    status: str = "UNSTARTED"
    passed: int = 0
    failed: int = 0
    error: str | None = None


def start(raw_input: str, valid_path: bool = True) -> AsyncCommand:
    command = AsyncCommand(raw_input=raw_input, target_hq=_detect_hq(raw_input))
    if command.target_hq is None:
        command.status = "FAILED"
        command.error = "unknown_hq"
        return command

    command.execution_id = operation.start_operation(command.target_hq, valid_path=valid_path)
    command.status = "RUNNING"
    return command


def refresh(command: AsyncCommand) -> AsyncCommand:
    if command.execution_id is None or command.status != "RUNNING":
        return command
    op_status = operation.poll(command.execution_id)
    command.status = op_status.status
    if op_status.status == "COMPLETED":
        command.passed, command.failed = op_status.passed, op_status.failed
    elif op_status.status == "FAILED":
        command.error = f"return_code={op_status.return_code}"
    return command

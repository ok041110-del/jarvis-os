"""Case A — Command 하나에 실행 상태를 직접 담는다(Task 없음).

User Command -> Command Resolver -> Long-running Operation -> Result.
Command 자체가 started_at/status/result/error를 보유한다(작업 지시
§6이 예시한 필드). Task를 미리 설계하지 않고, 이 구조가 실제로
막히는 지점을 관찰하는 것이 목적이다.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

_COMMAND_CONTRACT_DIR = Path(__file__).resolve().parents[1] / "command-contract"
sys.path.insert(0, str(_COMMAND_CONTRACT_DIR))

from resolver import _detect_hq  # noqa: E402  (기존 HQ 파싱 재사용, 중복 구현 금지)

import operation  # noqa: E402


@dataclass
class AsyncCommand:
    """Case A Contract — Command 하나가 요청과 실행 상태를 함께
    가진다. `execution_id`는 이 Command가 시작한 Operation을
    가리키는 참조일 뿐, 별도 Entity(Task)가 아니다."""

    raw_input: str
    target_hq: str | None = None
    execution_id: str | None = None
    status: str = "UNSTARTED"  # UNSTARTED | RUNNING | COMPLETED | FAILED
    started_at: float | None = None
    result: str | None = None
    error: str | None = None


def start(raw_input: str, valid_path: bool = True) -> AsyncCommand:
    """Command 생성과 동시에 Operation을 시작하고 즉시 반환한다."""

    target_hq = _detect_hq(raw_input)
    command = AsyncCommand(raw_input=raw_input, target_hq=target_hq)

    if target_hq is None:
        command.status = "FAILED"
        command.error = "unknown_hq"
        return command

    command.execution_id = operation.start_operation(target_hq, valid_path=valid_path)
    command.status = "RUNNING"
    return command


def refresh(command: AsyncCommand) -> AsyncCommand:
    """Command 자신의 상태를 최신화한다 — 별도 조회 대상(Task)이
    없으므로 Command를 직접 mutate한다."""

    if command.execution_id is None:
        return command

    op_status = operation.poll(command.execution_id)
    if op_status.status == "RUNNING":
        command.status = "RUNNING"
    elif op_status.status == "COMPLETED":
        command.status = "COMPLETED"
        command.result = op_status.output_tail
    else:
        command.status = "FAILED"
        command.error = op_status.output_tail

    return command

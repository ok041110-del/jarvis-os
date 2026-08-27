"""Command Contract — Experimental Prototype Contract.

Production Contract가 아니다(docs/research/JARVIS-OS-V2.0-COMMAND-
CONTRACT-PROTOTYPE-0001.md 참조). Q1~Q4를 검증하기 위한 최소
구현이며, Evidence 없이 필드를 미리 넣지 않는다 — Agent ID/Context
ID/Task ID/Permission/Priority/Dependency는 이 Prototype에 없다.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Command:
    """사용자가 무엇을 요청했는가. `target_hq`는 사용자가 직접
    채우지 않는다 — Resolver가 raw_input에서 파싱한 결과를 담는다
    (Q2: target_hq를 별도 필드로 분리할 필요가 있는지 검증하기 위해
    "사용자 입력"과 "파싱 결과"를 의도적으로 분리했다)."""

    raw_input: str
    intent: str | None = None
    target_hq: str | None = None


@dataclass(frozen=True)
class CommandResult:
    """Command 실행(읽기 전용) 결과."""

    status: str  # "ok" | "invalid"
    reason: str | None = None
    hq_identity: str | None = None
    detail: list[str] = field(default_factory=list)

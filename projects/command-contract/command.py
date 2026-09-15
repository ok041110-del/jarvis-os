"""Command Contract — Experimental Prototype Contract.

Production Contract가 아니다 — Evidence 없이 필드를 미리 넣지 않는다(Agent ID/Context ID/Task ID/Permission/Priority/Dependency 없음).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Command:
    """`target_hq`는 사용자가 직접 채우지 않는다 — Resolver가 raw_input에서 파싱한 결과를 담는다(Q2 검증용 의도적 분리)."""

    raw_input: str
    intent: str | None = None
    target_hq: str | None = None


@dataclass(frozen=True)
class CommandResult:
    status: str  # "ok" | "invalid"
    reason: str | None = None
    hq_identity: str | None = None
    detail: list[str] = field(default_factory=list)

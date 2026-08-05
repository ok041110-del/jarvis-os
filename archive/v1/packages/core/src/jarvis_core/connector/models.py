"""Connector Domain Model (ADR-0006). Core 소속 — 어떤 Adapter(MCP/Mock/HTTP)를
쓰든 이 모델은 바뀌지 않는다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

DEFAULT_TIMEOUT_MS = 5_000


@dataclass
class ToolRequest:
    """ADR-0006 결정 3. Connector 입장에서 arguments는 불투명(opaque) 값이다."""

    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = DEFAULT_TIMEOUT_MS
    idempotency_key: str | None = None


class ToolCallStatus(str, Enum):
    """ADR-0006 결정 4."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ToolResponse:
    """ADR-0006 결정 4·9. status가 SUCCESS가 아니면 error는 반드시 채워진다
    (No Silent Failure)."""

    status: ToolCallStatus
    result: Any | None = None
    error: str | None = None


class ConnectorLifecycleState(str, Enum):
    """ADR-0006 결정 13. 이번 Phase는 State 정의까지만 — 전이 로직/Health Check/
    Failover/Auto Recovery는 범위 밖이다. 어떤 실행 경로도 이 State로 분기하지 않는다.
    """

    REGISTERED = "registered"
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"
    REMOVED = "removed"

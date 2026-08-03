"""Workflow Domain Model (ADR-0007 결정 11).

TeamState(organization/entities.py)를 대체하지 않는다 — WorkflowStatus는
"그 생명주기가 어떻게 끝났는가"를, TeamState는 "지금 어느 단계에 있는가"를
나타내는 서로 다른 축이다.
"""
from dataclasses import dataclass
from enum import Enum


class WorkflowStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"


@dataclass
class WorkflowResult:
    status: WorkflowStatus
    error: str | None = None  # SUCCESS가 아닐 때 반드시 채워짐 (No Silent Failure)

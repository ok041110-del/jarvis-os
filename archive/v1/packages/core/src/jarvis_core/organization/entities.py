"""HQ / Division / Team / Agent 도메인 엔티티. Reference_Architecture_v1.md 1장 그대로."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

from jarvis_core.lifecycle.hq_state import HQState, transition as hq_transition


class TeamState(str, Enum):
    FORMING = "forming"
    ACTIVE = "active"
    COMPLETING = "completing"
    TERMINATED = "terminated"


@dataclass
class Agent:
    role_id: str
    capability_id: str
    required_tools: list[str] = field(default_factory=list)


@dataclass
class Division:
    division_id: str
    hq_id: str
    agent_catalog: list[Agent] = field(default_factory=list)


@dataclass
class Team:
    """Ephemeral. Forming -> Active -> Completing -> Terminated 외의 상태를 갖지 않는다
    (Core_Design_Principles_v1 §3 확정 사항 — Idle 상태를 의도적으로 두지 않음).
    """
    division_id: str
    agents: list[Agent]
    state: TeamState = TeamState.FORMING
    log: list[str] = field(default_factory=list)

    def activate(self) -> None:
        assert self.state is TeamState.FORMING
        self.state = TeamState.ACTIVE
        self.log.append("Team ACTIVE")

    def complete(self) -> None:
        assert self.state is TeamState.ACTIVE
        self.state = TeamState.COMPLETING
        self.log.append("Team COMPLETING")

    def terminate(self) -> None:
        assert self.state is TeamState.COMPLETING
        self.state = TeamState.TERMINATED
        self.log.append("Team TERMINATED")


@dataclass
class HQ:
    hq_id: str
    state: HQState = HQState.IDLE
    divisions: dict[str, Division] = field(default_factory=dict)
    audit: list[str] = field(default_factory=list)

    def transition_to(self, target: HQState, *, triggered_by_human: bool = False) -> None:
        new_state = hq_transition(self.state, target, triggered_by_human=triggered_by_human)
        self.audit.append(f"{self.hq_id}: {self.state.value} -> {new_state.value}")
        self.state = new_state

    def select_division(self, capability_id: str) -> Division:
        """Stage 6 (Division Selection) — 이건 Kernel이 아니라 HQ 자신의 책임이다.
        지금은 Division이 1개뿐이므로 그걸 반환한다.
        """
        return next(iter(self.divisions.values()))

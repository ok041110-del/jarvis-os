"""HQ Lifecycle 상태 정의 및 프레임워크 독립적인 전이 규칙.
Core_Design_Principles_v1.md §2 그대로 구현.

python-statemachine 등 실제 FSM 라이브러리는 adapters/lifecycle-statemachine에서
이 규칙을 감싸는 형태로 구현될 예정(v1.1 증분). 지금은 Core가 규칙 자체를 직접
가지고 있어도 무방하다 — 오히려 Guard 규칙(특히 Disabled는 자동 wake 불가)이
프레임워크 없이도 명확히 검증 가능해야 하기 때문이다.
"""
from enum import Enum


class HQState(str, Enum):
    PROVISIONING = "provisioning"
    RUNNING = "running"
    IDLE = "idle"
    SLEEPING = "sleeping"
    DISABLED = "disabled"
    UPDATING = "updating"
    ERROR = "error"
    DECOMMISSIONED = "decommissioned"


# 허용된 전이 (source -> {target, ...})
_ALLOWED_TRANSITIONS: dict[HQState, set[HQState]] = {
    HQState.PROVISIONING: {HQState.IDLE, HQState.ERROR},
    HQState.IDLE: {HQState.RUNNING, HQState.SLEEPING, HQState.UPDATING,
                    HQState.DISABLED, HQState.ERROR, HQState.DECOMMISSIONED},
    HQState.RUNNING: {HQState.IDLE, HQState.ERROR},
    HQState.SLEEPING: {HQState.RUNNING, HQState.DISABLED, HQState.DECOMMISSIONED},
    HQState.DISABLED: {HQState.IDLE},  # 사람의 명시적 재활성화만 (Guard로 강제)
    HQState.UPDATING: {HQState.IDLE, HQState.ERROR},
    HQState.ERROR: {HQState.IDLE, HQState.DISABLED},
    HQState.DECOMMISSIONED: set(),
}


class TransitionDenied(Exception):
    pass


def transition(current: HQState, target: HQState, *, triggered_by_human: bool = False) -> HQState:
    """핵심 Guard: Disabled -> Idle 전이는 반드시 사람이 트리거해야 한다.
    자동화(Wake-up 트리거 등)로는 Disabled를 벗어날 수 없다 — Core_Design_Principles_v1
    §2-2에서 확정한 규칙.
    """
    if target not in _ALLOWED_TRANSITIONS.get(current, set()):
        raise TransitionDenied(f"{current} -> {target} 전이는 허용되지 않음")
    if current is HQState.DISABLED and target is HQState.IDLE and not triggered_by_human:
        raise TransitionDenied("Disabled 상태는 사람의 명시적 재활성화로만 벗어날 수 있음")
    return target


def is_discoverable(state: HQState) -> bool:
    """Capability_Registry_v1.md §5 Lifecycle 연동 표 그대로."""
    return state in (HQState.RUNNING, HQState.IDLE, HQState.SLEEPING)

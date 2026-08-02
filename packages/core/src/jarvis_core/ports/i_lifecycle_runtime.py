"""i_lifecycle_runtime.py — Port(Interface) 정의.
Core는 이 Interface만 알고, 실제 구현(Casbin/LangGraph/MCP/...)은 모른다.
adapters/ 아래 패키지가 이 Interface를 implements 한다.

ADR-0003: 이 Port는 Domain Interface다 — 특정 FSM 라이브러리(python-statemachine 등)를
지칭하는 이름/타입을 노출하지 않는다. Guard 판정(허용된 전이, Disabled -> Idle의
사람 트리거 요구, Discoverable 여부)은 jarvis_core.lifecycle.hq_state 가 유일한
진실 공급원이며, 이 Port의 구현체는 그 판정을 위임받아 실행하는 엔진 역할만 한다.
"""
from abc import ABC, abstractmethod

from jarvis_core.lifecycle.hq_state import HQState


class LifecycleRuntime(ABC):
    """HQ의 Lifecycle 상태 전이를 실행하는 도메인 인터페이스."""

    @property
    @abstractmethod
    def current_state(self) -> HQState: ...

    @abstractmethod
    def transition(
        self,
        target: HQState,
        *,
        triggered_by_human: bool = False,
    ) -> HQState:
        """jarvis_core.lifecycle.hq_state.transition()의 판정을 실행한다.
        허용되지 않은 전이는 jarvis_core.lifecycle.hq_state.TransitionDenied를 그대로 전파한다.
        """
        ...

    @abstractmethod
    def is_discoverable(self) -> bool:
        """jarvis_core.lifecycle.hq_state.is_discoverable(self.current_state)와 동일해야 한다."""
        ...

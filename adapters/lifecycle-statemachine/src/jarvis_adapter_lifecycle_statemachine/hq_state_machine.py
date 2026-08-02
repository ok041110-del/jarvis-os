"""HQ Lifecycle을 python-statemachine으로 구현.

ADR-0003 결정 3: Guard 판정(허용된 전이, Disabled -> Idle의 사람 트리거 요구,
Discoverable 여부)은 전부 jarvis_core.lifecycle.hq_state에 위임한다. 이 어댑터는
그 판정을 실행하는 FSM 엔진일 뿐이며, 전이 규칙을 별도로 다시 정의하지 않는다 —
python-statemachine 그래프 자체를 hq_state의 전이표로부터 파생시켜서, 두 곳에
같은 규칙이 따로 존재하는 Drift를 원천적으로 방지한다.
"""
from statemachine import State, StateMachine

from jarvis_core.lifecycle import hq_state as hq_state_module
from jarvis_core.lifecycle.hq_state import (
    HQState,
    is_discoverable,
    transition as hq_transition,
)
from jarvis_core.ports.i_lifecycle_runtime import LifecycleRuntime


def _event_name(source: HQState, target: HQState) -> str:
    return f"t_{source.value}_to_{target.value}"


def _build_state_graph_class() -> type[StateMachine]:
    states = {
        s: State(
            s.value,
            initial=(s is HQState.PROVISIONING),
            final=(not hq_state_module._ALLOWED_TRANSITIONS.get(s)),
        )
        for s in HQState
    }
    attrs: dict = dict(states)
    for source, targets in hq_state_module._ALLOWED_TRANSITIONS.items():
        for target in targets:
            attrs[_event_name(source, target)] = states[source].to(states[target])
    attrs["__module__"] = __name__
    return type("_HQStateGraph", (StateMachine,), attrs)


_HQStateGraph = _build_state_graph_class()


class HQStateMachineRuntime(LifecycleRuntime):
    """LifecycleRuntime Port(jarvis_core)의 python-statemachine 기반 구현."""

    def __init__(self, initial_state: HQState = HQState.PROVISIONING) -> None:
        self._graph = _HQStateGraph(start_value=initial_state.value)

    @property
    def current_state(self) -> HQState:
        return HQState(self._graph.current_state_value)

    def transition(self, target: HQState, *, triggered_by_human: bool = False) -> HQState:
        # 판정은 Core(hq_transition)가 내린다. 여기서 TransitionDenied가 나면
        # 그대로 전파하고, 통과한 경우에만 FSM 엔진의 실제 상태를 이동시킨다.
        new_state = hq_transition(self.current_state, target, triggered_by_human=triggered_by_human)
        getattr(self._graph, _event_name(self.current_state, target))()
        return new_state

    def is_discoverable(self) -> bool:
        return is_discoverable(self.current_state)

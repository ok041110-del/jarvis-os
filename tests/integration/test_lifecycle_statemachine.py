"""Integration — Phase 1: Lifecycle Adapter(python-statemachine).

목적: HQStateMachineRuntime(LifecycleRuntime의 python-statemachine 구현)이
jarvis_core.lifecycle.hq_state의 판정과 100% 동일한 결과를 내는지 검증한다.
Guard 판정 자체를 이 어댑터가 재구현하지 않고 Core에 위임하고 있는지(ADR-0003
결정 3)를 실제 라이브러리 실행 경로로 증명하는 것이 이 테스트의 핵심 목적이다.

실행: PYTHONPATH에 각 패키지 src를 추가한 뒤
  python3 -m unittest tests.integration.test_lifecycle_statemachine -v
(uv sync 가능한 네트워크 환경에서는 `uv run pytest tests/integration` 로 대체)
"""
import itertools
import unittest

from jarvis_core.lifecycle.hq_state import (
    HQState,
    TransitionDenied,
    _ALLOWED_TRANSITIONS,
    transition as core_transition,
)
from jarvis_adapter_lifecycle_statemachine.hq_state_machine import HQStateMachineRuntime


class TestHQStateMachineRuntimeParity(unittest.TestCase):
    """Core의 전이표 전체를 순회하며 어댑터가 Core와 동일하게 판정하는지 확인한다."""

    def test_full_transition_table_matches_core(self):
        for source, target in itertools.product(HQState, HQState):
            for triggered_by_human in (False, True):
                with self.subTest(source=source, target=target, triggered_by_human=triggered_by_human):
                    runtime = HQStateMachineRuntime(initial_state=source)

                    core_denied = None
                    try:
                        core_transition(source, target, triggered_by_human=triggered_by_human)
                    except TransitionDenied as e:
                        core_denied = e

                    if core_denied is None:
                        result = runtime.transition(target, triggered_by_human=triggered_by_human)
                        self.assertEqual(result, target)
                        self.assertEqual(runtime.current_state, target)
                    else:
                        with self.assertRaises(TransitionDenied):
                            runtime.transition(target, triggered_by_human=triggered_by_human)
                        # 거부된 경우 상태가 그대로 유지되어야 한다(부분 전이 없음)
                        self.assertEqual(runtime.current_state, source)

    def test_allowed_transitions_table_is_exhaustive_for_non_terminal_states(self):
        # Decommissioned를 제외한 모든 상태는 최소 하나의 허용된 전이를 가져야 한다.
        for state, targets in _ALLOWED_TRANSITIONS.items():
            if state is HQState.DECOMMISSIONED:
                self.assertEqual(targets, set())
            else:
                self.assertTrue(targets, f"{state}에 허용된 전이가 없음")


class TestHQStateMachineRuntimeGuard(unittest.TestCase):
    """Core_Design_Principles_v1 §2 핵심 Guard: Disabled는 사람만 재활성화 가능."""

    def test_sleeping_can_auto_wake(self):
        runtime = HQStateMachineRuntime(initial_state=HQState.SLEEPING)
        result = runtime.transition(HQState.RUNNING, triggered_by_human=False)
        self.assertEqual(result, HQState.RUNNING)

    def test_disabled_cannot_auto_wake_but_human_trigger_allowed(self):
        runtime = HQStateMachineRuntime(initial_state=HQState.DISABLED)
        with self.assertRaises(TransitionDenied):
            runtime.transition(HQState.IDLE, triggered_by_human=False)
        self.assertEqual(runtime.current_state, HQState.DISABLED)

        result = runtime.transition(HQState.IDLE, triggered_by_human=True)
        self.assertEqual(result, HQState.IDLE)

    def test_is_discoverable_matches_core(self):
        for state in HQState:
            runtime = HQStateMachineRuntime(initial_state=state)
            from jarvis_core.lifecycle.hq_state import is_discoverable
            self.assertEqual(runtime.is_discoverable(), is_discoverable(state))


class TestAdapterReversibility(unittest.TestCase):
    """ADR-0003 결정 5: Adapter를 제거하고 기존(Core 직접 호출) 방식으로 되돌렸을 때
    Core 수정 없이 동일한 결과가 나와야 한다.
    """

    def test_runtime_result_matches_direct_core_call_for_same_sequence(self):
        sequence = [
            (HQState.RUNNING, False),
            (HQState.IDLE, False),
        ]
        # 기존 방식(Core 직접 호출)
        core_state = HQState.IDLE
        for target, human in sequence:
            core_state = core_transition(core_state, target, triggered_by_human=human)

        # Adapter 경유 방식
        runtime = HQStateMachineRuntime(initial_state=HQState.IDLE)
        for target, human in sequence:
            runtime.transition(target, triggered_by_human=human)

        self.assertEqual(runtime.current_state, core_state)


if __name__ == "__main__":
    unittest.main()

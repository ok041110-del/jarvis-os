"""E2E — PoC_Backlog_and_OSS_Survey_v1.md의 Must 11개 항목과 1:1 대응되는 테스트.

실행: PYTHONPATH에 각 패키지 src를 추가한 뒤
  python3 -m unittest tests.e2e.test_walking_skeleton -v
(uv sync 가능한 네트워크 환경에서는 `uv run pytest tests/e2e` 로 대체)
"""
import unittest

from jarvis_core.capability_registry.models import Capability
from jarvis_core.capability_registry.registry import CapabilityRegistry
from jarvis_core.organization.entities import HQ, Division, Agent, Team, TeamState
from jarvis_core.lifecycle.hq_state import HQState, TransitionDenied
from jarvis_core.kernel import intent_recognition, task_classification, task_router, hq_selection
from jarvis_core.policy.models import PolicyRequest, PolicyTier

from jarvis_adapter_policy_inmemory.engine import InMemoryPolicyEngine
from jarvis_adapter_connector_mock.connector import MockConnector


def _build_registry() -> CapabilityRegistry:
    reg = CapabilityRegistry()
    reg.register(Capability(
        capability_id="dev-hq.code-task.v1", domain="development.general",
        description="개발 작업", input_profile="", output_profile="",
        owner="development-hq", required_permission="standard",
        keywords=["코드", "리뷰"],
    ))
    reg.register(Capability(
        capability_id="invest-hq.market-task.v1", domain="investment.general",
        description="투자 작업", input_profile="", output_profile="",
        owner="investment-hq", required_permission="restricted",
        keywords=["시장", "투자"],
    ))
    return reg


class TestMustItems(unittest.TestCase):
    def setUp(self):
        self.registry = _build_registry()
        self.dev_hq = HQ(hq_id="development-hq", state=HQState.IDLE)
        self.invest_hq = HQ(hq_id="investment-hq", state=HQState.SLEEPING)
        self.hqs = {"development-hq": self.dev_hq, "investment-hq": self.invest_hq}
        self.policy = InMemoryPolicyEngine({"user-A": "standard", "user-B": "restricted"})

    # Must #1, #2 — Kernel Routing + Capability 매칭
    def test_capability_matching_routes_to_correct_hq(self):
        intent = intent_recognition.recognize("코드 리뷰 좀 해줘")
        classification = task_classification.classify(intent, self.registry)
        plan = task_router.route(classification, self.registry)
        self.assertEqual(plan.target_hq_candidates[0], "development-hq")

    # Must #5 — HQ 간 Routing 정확성 (다른 텍스트는 다른 HQ로)
    def test_different_intents_route_to_different_hqs(self):
        for text, expected in [("코드 리뷰 좀 해줘", "development-hq"),
                                 ("시장 투자 상황 알려줘", "investment-hq")]:
            intent = intent_recognition.recognize(text)
            classification = task_classification.classify(intent, self.registry)
            plan = task_router.route(classification, self.registry)
            self.assertEqual(plan.target_hq_candidates[0], expected)

    # Must #6 — Policy Engine Permission Tier
    def test_permission_denied_for_insufficient_level(self):
        decision = self.policy.evaluate(PolicyRequest(
            subject="user-A", action="invoke_capability",
            resource="invest-hq.market-task.v1", required_permission="restricted",
        ))
        self.assertFalse(decision.allow)
        self.assertEqual(decision.tier, PolicyTier.TIER1_ABSOLUTE)

    def test_permission_allowed_for_sufficient_level(self):
        decision = self.policy.evaluate(PolicyRequest(
            subject="user-B", action="invoke_capability",
            resource="invest-hq.market-task.v1", required_permission="restricted",
        ))
        self.assertTrue(decision.allow)

    # Must #7 — Lifecycle: Idle -> Running -> Idle, Sleeping -> (자동 wake 가능)
    def test_idle_running_idle_cycle(self):
        self.dev_hq.transition_to(HQState.RUNNING)
        self.assertEqual(self.dev_hq.state, HQState.RUNNING)
        self.dev_hq.transition_to(HQState.IDLE)
        self.assertEqual(self.dev_hq.state, HQState.IDLE)

    def test_sleeping_can_auto_wake_but_disabled_cannot(self):
        self.invest_hq.transition_to(HQState.RUNNING)  # Sleeping -> Running, 사람 트리거 불필요
        self.assertEqual(self.invest_hq.state, HQState.RUNNING)

        self.dev_hq.transition_to(HQState.DISABLED)
        with self.assertRaises(TransitionDenied):
            self.dev_hq.transition_to(HQState.IDLE)  # 자동으로는 불가
        self.dev_hq.transition_to(HQState.IDLE, triggered_by_human=True)  # 사람 트리거는 허용
        self.assertEqual(self.dev_hq.state, HQState.IDLE)

    # Must #8 — Team Ephemeral: Forming -> Active -> Completing -> Terminated
    def test_team_lifecycle_is_ephemeral(self):
        team = Team(division_id="d1", agents=[])
        self.assertEqual(team.state, TeamState.FORMING)
        team.activate()
        team.complete()
        team.terminate()
        self.assertEqual(team.state, TeamState.TERMINATED)

    # Must #9 — MCP Connector 호출 경로
    def test_agent_can_call_connector(self):
        connector = MockConnector("filesystem")
        result = connector.call_tool("filesystem", {"query": "test"})
        self.assertEqual(len(connector.call_log), 1)
        self.assertIn("성공", result["result"])

    # Must #10 — No Silent Failure: Disabled HQ 요청은 이유와 함께 실패해야 함
    def test_disabled_hq_fails_with_explicit_reason(self):
        self.dev_hq.transition_to(HQState.DISABLED)
        intent = intent_recognition.recognize("코드 리뷰 좀 해줘")
        classification = task_classification.classify(intent, self.registry)
        plan = task_router.route(classification, self.registry)
        outcome = hq_selection.select(plan, intent, self.registry, self.hqs, self.policy, "user-A")
        self.assertFalse(outcome.ok)
        self.assertTrue(outcome.reason)  # reason이 비어있으면 안 됨 (No Silent Failure)

    # Must #11 — 계층 경계 준수: Kernel의 KernelOutcome은 selected_hq까지만 정하고
    # Division/Team 결정은 포함하지 않는다 (dataclass 필드 자체로 증명)
    def test_kernel_outcome_does_not_decide_division_or_team(self):
        intent = intent_recognition.recognize("코드 리뷰 좀 해줘")
        classification = task_classification.classify(intent, self.registry)
        plan = task_router.route(classification, self.registry)
        outcome = hq_selection.select(plan, intent, self.registry, self.hqs, self.policy, "user-A")
        dispatch_fields = outcome.dispatch.__dataclass_fields__.keys()
        self.assertNotIn("division_id", dispatch_fields)
        self.assertNotIn("team_id", dispatch_fields)


if __name__ == "__main__":
    unittest.main()

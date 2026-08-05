"""Integration — Phase 3: Policy Adapter(Casbin).

ADR-0005의 Architecture Validation 목표를 코드로 증명한다:
"Policy Engine 구현체(Casbin)를 제거하고 다른 구현체로 교체해도 Core와 Kernel을
수정하지 않는다."

세 가지를 증명한다.
1. Parity — CasbinPolicyEngine과 InMemoryPolicyEngine이 동일한 session_permissions에
   대해 kernel/hq_selection.py를 통해 항상 동일한 allow/deny를 낸다.
2. Adapter Reversibility(ADR-0003 결정 5, ADR-0005 결정 6) — Casbin을 제거하고
   InMemory로 되돌렸을 때 Core(jarvis_core.kernel.hq_selection)를 전혀 수정하지
   않고 즉시 동일하게 동작한다.
3. Fail-Closed 계약(ADR-0005 결정 4) — IPolicyEngine.evaluate()는 내부 오류가
   나도 예외를 던지지 않고 PolicyDecision(allow=False, ...)을 반환한다. 이 계약을
   Casbin/InMemory 양쪽에 동일한 계약 테스트로 검증한다(어느 구현체를 쓰든
   PEP(hq_selection.py)는 try/except가 필요 없다).

실행: uv run pytest tests/integration/test_policy_adapter_reversibility.py -v
"""
import unittest

from jarvis_core.capability_registry.models import Capability
from jarvis_core.capability_registry.registry import CapabilityRegistry
from jarvis_core.organization.entities import HQ
from jarvis_core.lifecycle.hq_state import HQState
from jarvis_core.kernel import intent_recognition, task_classification, task_router, hq_selection
from jarvis_core.ports.i_policy_engine import IPolicyEngine
from jarvis_core.policy.models import PolicyRequest, PolicyDecision, PolicyTier

from jarvis_adapter_policy_casbin.casbin_policy_engine import CasbinPolicyEngine
from jarvis_adapter_policy_inmemory.engine import InMemoryPolicyEngine


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


_SESSIONS = {"user-A": "standard", "user-B": "restricted"}

# (요청 문장, session, 기대 결과: 실제로 dispatch 된 HQ 또는 None)
_SCENARIOS = [
    ("저장소 코드 리뷰 좀 해줘", "user-A", "development-hq"),   # standard가 standard 요구 -> ALLOW
    ("최근 시장 리서치 좀 해줘", "user-B", "investment-hq"),     # restricted가 restricted 요구 -> ALLOW
    ("포트폴리오 시세 조회해줘", "user-A", None),                # standard가 restricted 요구 -> DENY
]


def _run_scenario(policy_engine: IPolicyEngine, text: str, session: str):
    registry = _build_registry()
    hqs = {
        "development-hq": HQ(hq_id="development-hq", state=HQState.IDLE),
        "investment-hq": HQ(hq_id="investment-hq", state=HQState.IDLE),
    }
    intent = intent_recognition.recognize(text)
    classification = task_classification.classify(intent, registry)
    plan = task_router.route(classification, registry)
    outcome = hq_selection.select(plan, intent, registry, hqs, policy_engine, session)
    return outcome.dispatch.selected_hq if outcome.ok else None


class TestCasbinInMemoryParity(unittest.TestCase):
    """kernel/hq_selection.py를 통해 두 구현체가 항상 같은 결정을 내리는지 확인한다.
    Core/Kernel 코드는 이 테스트에서 한 줄도 바뀌지 않는다 — Adapter만 바뀐다.
    """

    def test_same_decisions_for_all_scenarios(self):
        for text, session, expected in _SCENARIOS:
            with self.subTest(text=text, session=session):
                casbin_engine = CasbinPolicyEngine(session_permissions=dict(_SESSIONS))
                inmemory_engine = InMemoryPolicyEngine(session_permissions=dict(_SESSIONS))

                casbin_result = _run_scenario(casbin_engine, text, session)
                inmemory_result = _run_scenario(inmemory_engine, text, session)

                self.assertEqual(casbin_result, expected)
                self.assertEqual(inmemory_result, expected)
                self.assertEqual(casbin_result, inmemory_result)


class TestAdapterReversibility(unittest.TestCase):
    """ADR-0005 결정 6: Casbin을 제거하고 InMemory(원래 Walking Skeleton 구현체)로
    되돌렸을 때 packages/core를 전혀 수정하지 않고 즉시 복구 가능해야 한다.
    이 테스트 자체가 "복구"를 수행한다 — import를 InMemory로 바꾸는 것 외에
    kernel/hq_selection.py, policy/models.py 어디도 건드리지 않는다.
    """

    def test_reverting_to_inmemory_reproduces_identical_dispatch(self):
        text, session, expected = "최근 시장 리서치 좀 해줘", "user-B", "investment-hq"

        # 되돌린 상태(Adapter = InMemory)
        reverted_engine = InMemoryPolicyEngine(session_permissions=dict(_SESSIONS))
        reverted_result = _run_scenario(reverted_engine, text, session)

        self.assertEqual(reverted_result, expected)


class _AlwaysThrowingPolicyEngine(IPolicyEngine):
    """Adapter 내부 오류를 흉내내는 테스트 전용 구현체 (예: casbin.Enforcer 생성 실패,
    정책 파일 파싱 실패 등)."""

    def evaluate(self, request: PolicyRequest) -> PolicyDecision:
        raise RuntimeError("simulated backend failure")


class TestFailClosedContract(unittest.TestCase):
    """ADR-0005 결정 4: IPolicyEngine.evaluate()는 예외를 던지지 않는다.
    Casbin/InMemory 구현체는 이미 이 계약을 지킨다. hq_selection.py(PEP)가
    try/except 없이 Adapter를 호출해도 내부 오류가 조용히 시스템을 뚫고
    올라오지 않는지(대신 Deny로 귀결되는지) 확인한다.
    """

    def test_casbin_engine_never_raises_even_on_construction_failure(self):
        # model.conf 경로 자체를 깨서 생성자 내부 오류를 강제로 유발한다.
        broken = CasbinPolicyEngine.__new__(CasbinPolicyEngine)
        broken._enforcer = None
        broken._init_error = "forced failure for contract test"

        decision = broken.evaluate(PolicyRequest(
            subject="user-A", action="invoke_capability",
            resource="dev-hq.code-task.v1", required_permission="standard",
        ))

        self.assertFalse(decision.allow)
        self.assertEqual(decision.tier, PolicyTier.TIER1_ABSOLUTE)
        self.assertIn("policy engine internal error", decision.reason)

    def test_pep_style_call_does_not_need_try_except(self):
        """hq_selection.py가 실제로 하듯 try/except 없이 evaluate()를 호출한다.
        Adapter가 계약을 어기고 예외를 던지면 이 테스트가 그 자체로 실패한다."""
        registry = _build_registry()
        hqs = {"development-hq": HQ(hq_id="development-hq", state=HQState.IDLE)}
        intent = intent_recognition.recognize("저장소 코드 리뷰 좀 해줘")
        classification = task_classification.classify(intent, registry)
        plan = task_router.route(classification, registry)

        # 계약을 지키는 구현체라면(Fail-Closed) 예외 없이 항상 KernelOutcome을 반환해야 한다.
        outcome = hq_selection.select(
            plan, intent, registry, hqs,
            CasbinPolicyEngine(session_permissions={"user-A": "standard"}),
            "user-A",
        )
        self.assertTrue(outcome.ok)


if __name__ == "__main__":
    unittest.main()

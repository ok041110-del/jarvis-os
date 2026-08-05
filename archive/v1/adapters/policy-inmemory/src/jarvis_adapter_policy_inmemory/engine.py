"""IPolicyEngine의 Walking Skeleton 구현.

명시적으로 임시(temporary)다 — ADR-003에 따라 실제 PoC 완성 단계에서는
adapters/policy-casbin(이미 스켈레톤 존재)으로 교체된다. Core는 IPolicyEngine
Port만 알기 때문에 이 교체는 apps/poc-runner의 import 한 줄만 바뀐다.
"""
from jarvis_core.ports.i_policy_engine import IPolicyEngine
from jarvis_core.policy.models import PolicyRequest, PolicyDecision, PolicyTier

# permission 등급 서열 (standard보다 restricted가 더 엄격)
_LEVELS = {"standard": 0, "restricted": 1}


class InMemoryPolicyEngine(IPolicyEngine):
    def __init__(self, session_permissions: dict[str, str]) -> None:
        """session_permissions: {session_id: 그 세션이 가진 최대 permission 등급}"""
        self._session_permissions = session_permissions

    def evaluate(self, request: PolicyRequest) -> PolicyDecision:
        session_level = self._session_permissions.get(request.subject, "standard")
        required_level = request.required_permission
        if _LEVELS.get(session_level, 0) >= _LEVELS.get(required_level, 0):
            return PolicyDecision(
                allow=True,
                tier=PolicyTier.TIER1_ABSOLUTE,
                reason=f"session({session_level}) >= required({required_level})",
            )
        return PolicyDecision(
            allow=False,
            tier=PolicyTier.TIER1_ABSOLUTE,
            reason=f"session 권한({session_level})이 필요 권한({required_level})보다 낮음",
        )

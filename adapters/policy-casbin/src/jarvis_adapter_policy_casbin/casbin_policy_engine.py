"""IPolicyEngine을 Casbin으로 구현.
PoC 범위: Permission Tier(Tier 1)만. Budget/Priority는 v1.1에서 OPA 전환 시 확장(ADR-0005 결정 1).

ADR-0005 결정 4(Failure Policy): 이 클래스는 예외를 던지지 않는다. 생성자에서든
evaluate()에서든 무엇이 실패하든 PolicyDecision(allow=False, ...)으로 변환해
반환한다(Fail-Closed) — IPolicyEngine의 계약이다.

model.conf/policy.csv는 이 Adapter 내부에서만 사용하는 Casbin 문법이다. Core는
이 파일들의 존재도 문법도 모른다(ADR-0005 결정 6).
"""
from pathlib import Path

import casbin

from jarvis_core.ports.i_policy_engine import IPolicyEngine
from jarvis_core.policy.models import PolicyRequest, PolicyDecision, PolicyTier

_MODEL_PATH = str(Path(__file__).parent / "model.conf")
_POLICY_PATH = str(Path(__file__).parent / "policy.csv")

# required_permission(Domain Language) <-> Casbin Role 이름을 잇는 유일한 지점.
_ROLE_BY_LEVEL = {
    "standard": "standard-level",
    "restricted": "restricted-level",
}


class CasbinPolicyEngine(IPolicyEngine):
    def __init__(self, session_permissions: dict[str, str]) -> None:
        """session_permissions: {session_id: 그 세션이 가진 최대 permission 등급}.

        InMemoryPolicyEngine과 동일한 생성자 형태를 유지한다 — Composition Root에서
        import 한 줄만 바꿔 교체 가능해야 한다(ADR-0005 결정 6, Adapter Reversibility).
        """
        self._init_error: str | None = None
        try:
            self._enforcer = casbin.Enforcer(_MODEL_PATH, _POLICY_PATH)
            for session, level in session_permissions.items():
                role = _ROLE_BY_LEVEL.get(level)
                if role is not None:
                    self._enforcer.add_grouping_policy(session, role)
        except Exception as exc:  # noqa: BLE001 — Fail-Closed 계약(ADR-0005 결정 4)
            self._enforcer = None
            self._init_error = str(exc)

    def evaluate(self, request: PolicyRequest) -> PolicyDecision:
        if self._enforcer is None:
            return PolicyDecision(
                allow=False,
                tier=PolicyTier.TIER1_ABSOLUTE,
                reason=f"policy engine internal error: {self._init_error}",
            )

        try:
            allowed = self._enforcer.enforce(
                request.subject, request.required_permission, request.action
            )
        except Exception as exc:  # noqa: BLE001 — Fail-Closed 계약(ADR-0005 결정 4)
            return PolicyDecision(
                allow=False,
                tier=PolicyTier.TIER1_ABSOLUTE,
                reason=f"policy engine internal error: {exc}",
            )

        if allowed:
            return PolicyDecision(
                allow=True,
                tier=PolicyTier.TIER1_ABSOLUTE,
                reason=f"casbin: subject({request.subject})가 required({request.required_permission})를 만족함",
            )
        return PolicyDecision(
            allow=False,
            tier=PolicyTier.TIER1_ABSOLUTE,
            reason=f"casbin: subject({request.subject})가 required({request.required_permission})를 만족하지 않음",
        )

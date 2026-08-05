"""HQProvisioner — Application Service (ADR-0004 결정 3/4/6).

Composition Root(apps/poc-runner)는 이 서비스를 구체 Adapter(ICapabilityProvider
구현체, LifecycleRuntime 구현체 팩토리)와 함께 생성해 호출하기만 한다 — "객체를
연결"하는 것과 "Provisioning 절차를 실행"하는 것을 분리한다(사용자 승인 사항).
Provisioning 절차(Capability 조회 -> 구조 검증 -> Registry 등록 -> Lifecycle
Provisioning -> Idle/Error 전이)는 전부 이 클래스 안에서만 일어난다.

이 서비스는 Capability의 의미(도메인, 키워드 등)를 해석하지 않는다 — 오직
"등록에 성공했는가"라는 구조적 사실만 다룬다(ADR-0004 결정 6).

CapabilityRegistry와 HQ Lifecycle은 서로 독립이며(ADR-0004 결정 5), 이 둘을
잇는 유일한 지점이 바로 이 Application Service다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from jarvis_core.capability_registry.models import Capability
from jarvis_core.capability_registry.registry import CapabilityRegistry
from jarvis_core.lifecycle.hq_state import HQState
from jarvis_core.organization.entities import HQ, Agent, Division
from jarvis_core.ports.i_capability_provider import ICapabilityProvider
from jarvis_core.ports.i_lifecycle_runtime import LifecycleRuntime


@dataclass
class ProvisionResult:
    hq: HQ
    runtime: LifecycleRuntime
    capability: Capability | None
    ok: bool
    reason: str | None = None


class HQProvisioner:
    """새 HQ를 Provisioning 단계에서 등록시키는 Application Service."""

    def __init__(
        self,
        capability_provider: ICapabilityProvider,
        registry: CapabilityRegistry,
        runtime_factory: Callable[[HQState], LifecycleRuntime],
    ) -> None:
        self._provider = capability_provider
        self._registry = registry
        self._runtime_factory = runtime_factory

    def provision_all(self) -> dict[str, ProvisionResult]:
        """발견된 모든 Capability에 대해 HQ를 Provisioning -> Idle/Error로 진행시킨다."""
        results: dict[str, ProvisionResult] = {}
        for capability in self._provider.load():
            results[capability.owner] = self._provision_one(capability)
        return results

    def _provision_one(self, capability: Capability) -> ProvisionResult:
        hq = HQ(hq_id=capability.owner, state=HQState.PROVISIONING)
        runtime = self._runtime_factory(HQState.PROVISIONING)

        ok, reason = self._validate(capability)
        if ok:
            self._registry.register(capability)
            division = Division(
                division_id=f"{capability.owner}-division",
                hq_id=capability.owner,
                agent_catalog=[
                    Agent(role_id=f"{capability.owner}-agent",
                          capability_id=capability.capability_id)
                ],
            )
            hq.divisions[division.division_id] = division

        target = HQState.IDLE if ok else HQState.ERROR
        new_state = runtime.transition(target)
        hq.state = new_state
        hq.audit.append(
            f"{hq.hq_id}: provisioning -> {new_state.value}"
            f" ({reason if reason else 'capability registered'})"
        )
        return ProvisionResult(hq=hq, runtime=runtime, capability=capability, ok=ok, reason=reason)

    def _validate(self, capability: Capability) -> tuple[bool, str | None]:
        """ADR-0004 결정 4의 조건 중 Registry 상태에 의존하는 부분만 여기서 검사한다.
        (YAML Parsing 성공 / Owner 식별자 일치 여부는 Provider가 구조 검증 단계에서
        걸러내고 넘어오므로, 여기서 다시 검사하지 않는다 — 책임 중복 방지.)
        """
        if self._registry.is_registered(capability.capability_id):
            return False, f"duplicate capability_id: {capability.capability_id}"
        return True, None

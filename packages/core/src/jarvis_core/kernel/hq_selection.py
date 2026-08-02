"""Stage 5 — HQ Selection. Kernel의 마지막 단계 — 여기서 끝나면 Organization Layer로
제어가 넘어간다 (Request_Processing_Kernel_v1.md §2 경계선).

No Silent Failure: 후보가 없거나 전부 Disabled거나 Policy가 거부하면
반드시 reason이 채워진 KernelOutcome(ok=False)을 반환한다.
"""
from .models import Intent, ExecutionPlan, TaskDispatch, KernelOutcome
from jarvis_core.capability_registry.registry import CapabilityRegistry
from jarvis_core.organization.entities import HQ
from jarvis_core.lifecycle.hq_state import HQState, is_discoverable
from jarvis_core.policy.models import PolicyRequest, PolicyTier
from jarvis_core.ports.i_policy_engine import IPolicyEngine


def select(
    plan: ExecutionPlan,
    intent: Intent,
    registry: CapabilityRegistry,
    hqs: dict[str, HQ],
    policy_engine: IPolicyEngine,
    session: str,
) -> KernelOutcome:
    trail: list[str] = []

    if not plan.target_hq_candidates:
        trail.append("Task Classification 단계에서 매칭되는 Capability가 없었음 (unclassified)")
        return KernelOutcome(ok=False, reason="요청을 처리할 수 있는 HQ를 찾지 못했습니다.", audit_trail=trail)

    for hq_id in plan.target_hq_candidates:
        hq = hqs.get(hq_id)
        if hq is None:
            trail.append(f"{hq_id}: 레지스트리에 없음 — 건너뜀")
            continue

        if hq.state is HQState.DISABLED:
            trail.append(f"{hq_id}: Disabled 상태 — 후보에서 배제 (자동 wake 불가)")
            continue
        if not is_discoverable(hq.state):
            trail.append(f"{hq_id}: {hq.state.value} 상태라 현재 탐색 불가 — 건너뜀")
            continue

        # 이 HQ가 제공하는 capability를 다시 찾아 required_permission 확인
        owned_caps = registry.get_by_owner(hq_id)
        cap = owned_caps[0] if owned_caps else None
        if cap is None:
            trail.append(f"{hq_id}: capability 조회 실패 — 건너뜀")
            continue

        decision = policy_engine.evaluate(PolicyRequest(
            subject=session,
            action="invoke_capability",
            resource=cap.capability_id,
            required_permission=cap.required_permission,
        ))
        trail.append(f"Policy[Tier{int(decision.tier)}] subject={session} resource={cap.capability_id} "
                      f"-> {'ALLOW' if decision.allow else 'DENY'} ({decision.reason})")

        if not decision.allow:
            if decision.tier == PolicyTier.TIER1_ABSOLUTE:
                trail.append("Tier 1 거부 — 하위 후보 평가 없이 즉시 이 후보를 포기")
                continue
            trail.append("Tier 2 거부 — 축소안 없음(PoC 범위) — 이 후보 포기")
            continue

        wake_up_required = hq.state is HQState.SLEEPING
        if wake_up_required:
            trail.append(f"{hq_id}: Sleeping 상태 — Wake-up 트리거 포함하여 Dispatch")

        dispatch = TaskDispatch(
            selected_hq=hq_id,
            capability_id=cap.capability_id,
            intent=intent,
            wake_up_required=wake_up_required,
        )
        return KernelOutcome(ok=True, dispatch=dispatch, audit_trail=trail)

    trail.append("모든 후보가 배제되었음 (Disabled/미탐색/Policy 거부)")
    return KernelOutcome(ok=False, reason="현재 이 요청을 처리할 수 있는 HQ가 없습니다.", audit_trail=trail)

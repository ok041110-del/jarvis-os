"""Composition Root — Walking Skeleton.

여기서만 구체적인 구현(지금은 Walking Skeleton adapter, 이후 Casbin/MCP 실제 adapter)을
선택해 Core의 Port에 주입한다. packages/core는 이 파일의 존재조차 모른다.

4개 시나리오로 PoC Must #1,2,3,4,5,6,7,8,9,10,11을 전부 훑는다.

Phase 1(ADR-0003): HQ Lifecycle 전이는 이제 jarvis_core.organization.entities.HQ의
transition_to()를 직접 호출하지 않고, LifecycleRuntime Port를 통해 실행한다.
Guard 판정 자체는 여전히 Core(jarvis_core.lifecycle.hq_state)가 유일하게 내리며,
이 어댑터는 그 판정을 python-statemachine 엔진으로 실행할 뿐이다. 롤백 시에는
advance_hq() 호출부를 hq.transition_to() 호출로 되돌리기만 하면 되고, Core는
전혀 건드릴 필요가 없다(Adapter Reversibility, ADR-0003 결정 5).

Phase 2(ADR-0004): HQ/Capability를 이 파일에 하드코딩하지 않는다. build_world()는
jarvis_core.application.hq_provisioner.HQProvisioner(Application Service)에게
YamlCapabilityProvider(ICapabilityProvider 구현체)와 LifecycleRuntime 팩토리를
주입해 "Capability 조회 -> Registry 등록 -> Provisioning -> Idle/Error 전이"
절차 전체를 위임한다. 이 파일은 어떤 HQ가 존재하는지 전혀 알지 못한다 — 새 HQ는
hqs/<name>-hq 패키지 + entry point 선언만으로 uv workspace에 편입되고 자동
발견된다(ADR-0004 결정 7). Composition Root는 객체를 연결만 하고, Provisioning
절차 자체는 HQProvisioner가 담당한다(사용자 승인 사항).
"""
from jarvis_core.application.hq_provisioner import HQProvisioner
from jarvis_core.capability_registry.registry import CapabilityRegistry
from jarvis_core.lifecycle.hq_state import HQState
from jarvis_core.organization.entities import Team
from jarvis_core.kernel import intent_recognition, task_classification, task_router, hq_selection

from jarvis_adapter_capability_provider_yaml.provider import YamlCapabilityProvider
from jarvis_adapter_policy_inmemory.engine import InMemoryPolicyEngine
from jarvis_adapter_connector_mock.connector import MockConnector
from jarvis_adapter_lifecycle_statemachine.hq_state_machine import HQStateMachineRuntime


def log(msg: str) -> None:
    print(msg)


def build_world():
    registry = CapabilityRegistry()
    provisioner = HQProvisioner(
        capability_provider=YamlCapabilityProvider(),
        registry=registry,
        runtime_factory=HQStateMachineRuntime,
    )
    provisioned = provisioner.provision_all()

    hqs = {}
    lifecycle_runtimes = {}
    for owner, result in provisioned.items():
        if result.ok:
            hqs[owner] = result.hq
            lifecycle_runtimes[owner] = result.runtime
        else:
            log(f"[Provisioning] ❌ '{owner}' Capability 등록 실패 -> Error 상태로 전이: {result.reason}")

    connectors = {"filesystem": MockConnector("filesystem"), "fetch": MockConnector("fetch")}
    return registry, hqs, lifecycle_runtimes, connectors


def advance_hq(hq, runtime: HQStateMachineRuntime, target: HQState, *, triggered_by_human: bool = False) -> None:
    """HQ의 Lifecycle 전이를 LifecycleRuntime Port를 통해 실행한다.
    Guard 판정은 runtime.transition() 내부에서 Core(hq_state.transition)가 내린다.
    """
    previous = hq.state
    new_state = runtime.transition(target, triggered_by_human=triggered_by_human)
    hq.state = new_state
    hq.audit.append(f"{hq.hq_id}: {previous.value} -> {new_state.value} (via LifecycleRuntime adapter)")


def handle_request(text: str, session: str, registry, hqs, lifecycle_runtimes, policy_engine, connectors) -> None:
    log(f"\n=== 요청: \"{text}\" (session={session}) ===")

    # Stage 2
    intent = intent_recognition.recognize(text)
    if intent_recognition.needs_clarification(intent):
        log(f"[Kernel] Intent 모호함(confidence={intent.confidence:.2f}) -> 사용자에게 즉시 반문 (조직으로 내려보내지 않음)")
        return
    log(f"[Kernel] Intent Recognition: confidence={intent.confidence:.2f}")

    # Stage 3
    classification = task_classification.classify(intent, registry)
    if task_classification.is_unclassified(classification):
        log("[Kernel] Task Classification: unclassified -> General 경로 (No Silent Failure)")
        return
    log(f"[Kernel] Task Classification 후보: {classification.domain_candidates}")

    # Stage 4
    plan = task_router.route(classification, registry)
    log(f"[Kernel] Task Router: target 후보={plan.target_hq_candidates}, mode={plan.execution_mode}")

    # Stage 5
    outcome = hq_selection.select(plan, intent, registry, hqs, policy_engine, session)
    for line in outcome.audit_trail:
        log(f"[Audit] {line}")

    if not outcome.ok:
        log(f"[Kernel] ❌ 실패 — 사용자에게 투명하게 전달: {outcome.reason}")
        return

    dispatch = outcome.dispatch
    log(f"[Kernel] ✅ Task Dispatch 확정 -> {dispatch.selected_hq} "
        f"(wake_up_required={dispatch.wake_up_required})")

    # ---- 여기서부터 Organization Layer. Kernel 코드는 여기 관여하지 않는다 ----
    run_organization_layer(dispatch, hqs, lifecycle_runtimes, connectors)


def run_organization_layer(dispatch, hqs, lifecycle_runtimes, connectors) -> None:
    hq = hqs[dispatch.selected_hq]
    runtime = lifecycle_runtimes[dispatch.selected_hq]

    if dispatch.wake_up_required:
        advance_hq(hq, runtime, HQState.RUNNING)  # Sleeping -> Running (자동 wake, 허용됨)
    else:
        advance_hq(hq, runtime, HQState.RUNNING)  # Idle -> Running

    # Stage 6 — Division Selection은 HQ 자신의 책임 (Kernel이 아님)
    division = hq.select_division(dispatch.capability_id)
    log(f"[HQ:{hq.hq_id}] Division Selection -> {division.division_id} (HQ 자체 판단, Kernel 관여 없음)")

    # Stage 7 — Team Formation은 Division의 책임
    team = Team(division_id=division.division_id, agents=list(division.agent_catalog))
    log(f"[Division:{division.division_id}] Team Formation -> state={team.state.value}")
    team.activate()
    log(f"[Team] state={team.state.value}")

    # Stage 8 — Agent Invocation은 Team의 책임
    for agent in team.agents:
        tool = agent.required_tools[0] if agent.required_tools else None
        if tool and tool in connectors:
            result = connectors[tool].call_tool(tool, {"query": dispatch.intent.raw_text})
            log(f"[Agent:{agent.role_id}] -> MCP[{tool}] 호출 -> {result['result']}")

    team.complete()
    team.terminate()
    log(f"[Team] state={team.state.value} (Ephemeral 소멸)")

    advance_hq(hq, runtime, HQState.IDLE)
    log(f"[HQ:{hq.hq_id}] Running -> Idle (사이클 종료)")

    # Stage 9 — Result Integration (여기서는 로그로 대체, 실제로는 User Response 구성)
    log(f"[Result Integration] {hq.hq_id} 처리 완료, 사용자에게 결과 반환")


def main() -> None:
    registry, hqs, lifecycle_runtimes, connectors = build_world()
    policy_engine = InMemoryPolicyEngine(session_permissions={
        "user-A": "standard",   # Investment HQ(restricted)는 못 씀 -> 시나리오 D에서 거부됨
        "user-B": "restricted", # 둘 다 사용 가능
    })

    log("=" * 70)
    log("Jarvis OS Walking Skeleton — Must #1,2,3,4,5,6,7,8,9,10,11 검증")
    log("=" * 70)

    # Phase 2: HQProvisioner는 모든 HQ를 Idle로 Provisioning한다. Wake-up 시나리오를
    # 시연하기 위해, 데모 스크립트(main)가 investment-hq를 명시적으로 Sleeping으로
    # 재우는 것은 build_world()의 책임이 아니라 이 데모 시나리오 구성의 책임이다.
    advance_hq(hqs["investment-hq"], lifecycle_runtimes["investment-hq"], HQState.SLEEPING)

    # 시나리오 A: Investment HQ(Sleeping) -> Wake-up + 정상 처리 (Must #5,#7,#9)
    handle_request("최근 시장 리서치 좀 해줘", "user-B", registry, hqs, lifecycle_runtimes, policy_engine, connectors)

    # 시나리오 B: Development HQ를 Disabled로 만든 뒤 요청 -> No Silent Failure (Must #10)
    advance_hq(hqs["development-hq"], lifecycle_runtimes["development-hq"], HQState.DISABLED)
    handle_request("코드 리뷰 좀 해줘", "user-A", registry, hqs, lifecycle_runtimes, policy_engine, connectors)

    # 시나리오 C: Development HQ 재활성화(사람이 트리거) 후 정상 처리 (Must #6,#7,#8,#11)
    advance_hq(hqs["development-hq"], lifecycle_runtimes["development-hq"], HQState.IDLE, triggered_by_human=True)
    handle_request("저장소 코드 리뷰 좀 해줘", "user-A", registry, hqs, lifecycle_runtimes, policy_engine, connectors)

    # 시나리오 D: user-A(standard)가 Investment HQ(restricted) 요청 -> Permission Tier 거부 (Must #6,#10)
    handle_request("포트폴리오 시세 조회해줘", "user-A", registry, hqs, lifecycle_runtimes, policy_engine, connectors)

    log("\n" + "=" * 70)
    log("Walking Skeleton 실행 종료")
    log("=" * 70)


if __name__ == "__main__":
    main()

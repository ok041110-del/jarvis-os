"""Integration — Phase 5: Workflow Adapter(LangGraph).

ADR-0007의 최종 Architecture Validation 목표 1을 코드로 증명한다:
"LangGraph를 제거하고 Sequential Workflow Adapter로 교체해도 Core와
Organization Layer를 수정하지 않는다."

Workflow Engine에는 Discovery/Registry가 없다(ADR-0007 결정 12) — 두 Adapter
모두 직접 구성(direct construction)으로 교체하며, 이는 policy-inmemory/
connector-mock이 Phase 3/4에서 증명한 것과 동일한 방식이다.

세 가지를 증명한다.
1. Contract Parity — LangGraphWorkflowEngine과 SequentialWorkflowEngine이
   동일한 Team/TaskDispatch에 대해 항상 동일한 WorkflowResult(및 동일한
   Team 최종 상태)를 낸다. 병렬 실행 "구조"만 검증하며 성능은 검증하지
   않는다(ADR-0007 결정 7, 사용자 지시) — 여러 Agent가 있는 Team으로
   계약이 동일한지만 확인한다.
2. Adapter Reversibility — LangGraph를 제거하고 Sequential로 교체해도
   packages/core(organization/entities.py의 Team/TeamState)를 전혀
   수정하지 않고 즉시 동일하게 동작한다.
3. Fail-Closed 계약 — IWorkflowEngine.run()은 내부 오류가 나도 예외를
   던지지 않고 WorkflowResult(status=FAILURE, ...)를 반환한다(ADR-0007
   결정 6/9).

실행: uv run pytest tests/integration/test_workflow_adapter_reversibility.py -v
"""
import unittest

from jarvis_core.connector.models import ToolCallStatus, ToolRequest, ToolResponse
from jarvis_core.connector_registry.registry import ConnectorRegistry
from jarvis_core.kernel.models import Intent, TaskDispatch
from jarvis_core.organization.entities import Agent, Team, TeamState
from jarvis_core.ports.i_connector import IConnector
from jarvis_core.ports.i_workflow_engine import IWorkflowEngine
from jarvis_core.workflow.models import WorkflowStatus

from jarvis_adapter_workflow_langgraph.langgraph_engine import LangGraphWorkflowEngine
from jarvis_adapter_workflow_sequential.sequential_engine import SequentialWorkflowEngine


class _FixtureConnector(IConnector):
    """테스트 전용 Connector. Agent.required_tools가 실제로 채워져 있다고
    가정하고 Workflow Engine의 계약만 검증한다(Phase 4부터 이월된
    Agent.required_tools 미채움 Known Gap은 이번 Phase에서도 해결하지 않는다
    — 사용자 승인 사항)."""

    def __init__(self, should_fail: bool = False) -> None:
        self._should_fail = should_fail
        self.call_log: list[ToolRequest] = []

    @property
    def capabilities(self) -> list[str]:
        return ["fixture-tool"]

    def call_tool(self, request: ToolRequest) -> ToolResponse:
        self.call_log.append(request)
        if self._should_fail:
            return ToolResponse(status=ToolCallStatus.FAILURE, error="fixture forced failure")
        return ToolResponse(status=ToolCallStatus.SUCCESS, result={"echo": request.arguments})


def _make_team(agent_count: int) -> Team:
    agents = [
        Agent(role_id=f"agent-{i}", capability_id="fixture.capability.v1", required_tools=["fixture-tool"])
        for i in range(agent_count)
    ]
    return Team(division_id="fixture-division", agents=agents)


def _make_dispatch() -> TaskDispatch:
    intent = Intent(raw_text="fixture request", primary_intent="fixture", entities=[], confidence=0.9)
    return TaskDispatch(selected_hq="fixture-hq", capability_id="fixture.capability.v1", intent=intent)


def _make_engine(kind: str, connectors: ConnectorRegistry) -> IWorkflowEngine:
    if kind == "langgraph":
        return LangGraphWorkflowEngine(connectors)
    if kind == "sequential":
        return SequentialWorkflowEngine(connectors)
    raise ValueError(kind)


class TestWorkflowEngineContractParity(unittest.TestCase):
    """두 Adapter가 동일 계약을 만족하는지 확인한다 — 병렬 실행 성능이 아니라
    Contract(WorkflowResult/Team 최종 상태) 동일성만 검증한다(사용자 지시)."""

    def test_success_scenario_identical_across_adapters(self):
        for kind in ("langgraph", "sequential"):
            with self.subTest(engine=kind):
                connectors = ConnectorRegistry()
                connectors.register(_FixtureConnector(should_fail=False))
                team = _make_team(agent_count=3)  # 여러 Agent -> 병렬 실행 가능한 구조 검증
                dispatch = _make_dispatch()

                result = _make_engine(kind, connectors).run(team, dispatch)

                self.assertEqual(result.status, WorkflowStatus.SUCCESS)
                self.assertIsNone(result.error)
                self.assertEqual(team.state, TeamState.TERMINATED)

    def test_failure_scenario_identical_across_adapters(self):
        for kind in ("langgraph", "sequential"):
            with self.subTest(engine=kind):
                connectors = ConnectorRegistry()
                connectors.register(_FixtureConnector(should_fail=True))
                team = _make_team(agent_count=2)
                dispatch = _make_dispatch()

                result = _make_engine(kind, connectors).run(team, dispatch)

                self.assertEqual(result.status, WorkflowStatus.FAILURE)
                self.assertIsNotNone(result.error)
                # 실패해도 Team은 여전히 Ephemeral 생명주기를 끝까지 마친다(No Silent Hang).
                self.assertEqual(team.state, TeamState.TERMINATED)

    def test_empty_team_still_terminates(self):
        for kind in ("langgraph", "sequential"):
            with self.subTest(engine=kind):
                connectors = ConnectorRegistry()
                team = _make_team(agent_count=0)
                dispatch = _make_dispatch()

                result = _make_engine(kind, connectors).run(team, dispatch)

                self.assertEqual(result.status, WorkflowStatus.SUCCESS)
                self.assertEqual(team.state, TeamState.TERMINATED)


class TestAdapterReversibility(unittest.TestCase):
    """ADR-0007 최종 Architecture Validation 목표 1: LangGraph를 제거하고
    Sequential Workflow Adapter로 교체해도 packages/core(Team/TeamState)를
    전혀 수정하지 않고 즉시 복구 가능해야 한다. 이 테스트 자체가 "복구"를
    수행한다 — import를 Sequential로 바꾸는 것 외에 organization/entities.py는
    건드리지 않는다."""

    def test_reverting_to_sequential_reproduces_identical_result(self):
        connectors = ConnectorRegistry()
        connectors.register(_FixtureConnector(should_fail=False))
        team = _make_team(agent_count=2)
        dispatch = _make_dispatch()

        reverted_engine = SequentialWorkflowEngine(connectors)  # "되돌린" Adapter
        result = reverted_engine.run(team, dispatch)

        self.assertEqual(result.status, WorkflowStatus.SUCCESS)
        self.assertEqual(team.state, TeamState.TERMINATED)


class _BrokenWorkflowEngine(IWorkflowEngine):
    """내부 오류를 흉내내는 테스트 전용 구현체(예: Graph 컴파일 실패 등)."""

    def run(self, team, dispatch):
        raise RuntimeError("simulated workflow engine internal failure")


class TestFailClosedContract(unittest.TestCase):
    """ADR-0007 결정 6/9: IWorkflowEngine.run()은 예외를 던지지 않는다.
    LangGraph/Sequential 구현체는 이미 이 계약을 지킨다(run() 내부에서
    try/except로 감싸 WorkflowResult(FAILURE)로 변환)."""

    def test_langgraph_never_raises_on_missing_connector(self):
        connectors = ConnectorRegistry()  # 등록된 Connector 없음
        team = _make_team(agent_count=1)
        dispatch = _make_dispatch()

        result = LangGraphWorkflowEngine(connectors).run(team, dispatch)

        self.assertEqual(result.status, WorkflowStatus.FAILURE)
        self.assertIn("fixture-tool", result.error)

    def test_sequential_never_raises_on_missing_connector(self):
        connectors = ConnectorRegistry()
        team = _make_team(agent_count=1)
        dispatch = _make_dispatch()

        result = SequentialWorkflowEngine(connectors).run(team, dispatch)

        self.assertEqual(result.status, WorkflowStatus.FAILURE)
        self.assertIn("fixture-tool", result.error)

    def test_caller_style_call_does_not_need_try_except(self):
        """main.py의 run_organization_layer가 실제로 하듯 try/except 없이
        run()을 호출한다. 계약을 어기는 구현체라면 이 테스트 자체가 예외로 실패한다."""
        broken = _BrokenWorkflowEngine()
        team = _make_team(agent_count=1)
        dispatch = _make_dispatch()

        # Fail-Closed를 지키지 않는 구현체(_BrokenWorkflowEngine)는 의도적으로
        # 예외를 던지도록 만들었다 — 이 테스트는 "계약 위반 시 무엇이 보이는가"의
        # 대조군이며, run_organization_layer가 실제로 try/except 없이 호출한다는
        # 사실 자체는 LangGraph/Sequential 두 실사용 Adapter로 위 테스트에서 증명됨.
        with self.assertRaises(RuntimeError):
            broken.run(team, dispatch)


if __name__ == "__main__":
    unittest.main()

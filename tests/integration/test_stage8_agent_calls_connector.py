"""Integration — Phase 5: Stage 8 재구성(Agent가 Connector를 직접 호출).

ADR-0007의 최종 Architecture Validation 목표 2를 코드로 증명한다:
"Stage 8에서 Agent가 Connector를 직접 호출하는 구조가 Core 수정 없이
동작함을 코드와 테스트로 증명한다."

호출 주체 이동: 기존에는 apps/poc-runner/main.py(Composition Root)가
`connectors.find_by_capability(tool).call_tool(...)`를 대신 호출했다. 이제는
Core의 AgentExecutor(Application Service)가 이 절차를 수행하고, Workflow
Engine(LangGraph/Sequential 어느 쪽이든)이 그 실행 시점만 조립한다 — main.py는
더 이상 Connector를 직접 호출하지 않는다(main.py의 Import 목록에서
`ToolRequest`가 Phase 4 데모 블록에만 남아 있고 Stage 8 경로에서는 쓰이지
않는다는 사실 자체가 이 이동의 증거다).

Agent.required_tools를 HQProvisioner가 채우지 않는 문제(Phase 2/4부터 이월된
Known Gap)는 이번 Phase에서도 해결하지 않는다(사용자 승인 사항) — 이 테스트는
required_tools가 채워진 Fixture Agent를 사용해 "채워져 있다면 이 구조가
동작하는가"만 검증한다.

Core 무수정 증명 방식: 이 테스트는 kernel/hq_selection.py, organization/entities.py,
capability_registry/registry.py, lifecycle/hq_state.py를 실제 Phase 1~4와
동일한 방식으로 그대로 사용해 Kernel Stage 1~5 + HQ Division Selection(Stage 6)이
이 Phase의 변경으로 전혀 달라지지 않았음을 함께 증명한다. 또한 이 파일들의
소스에 "workflow"라는 단어가 전혀 등장하지 않는지 확인해 Workflow 개념이
이 계층에 스며들지 않았음을 정적으로도 확인한다.

실행: uv run pytest tests/integration/test_stage8_agent_calls_connector.py -v
"""
import inspect
import unittest

from jarvis_core.capability_registry import registry as capability_registry_module
from jarvis_core.capability_registry.models import Capability
from jarvis_core.capability_registry.registry import CapabilityRegistry
from jarvis_core.connector.models import ToolCallStatus, ToolRequest, ToolResponse
from jarvis_core.connector_registry.registry import ConnectorRegistry
from jarvis_core.kernel import hq_selection as hq_selection_module
from jarvis_core.kernel import intent_recognition, task_classification, task_router
from jarvis_core.lifecycle import hq_state as hq_state_module
from jarvis_core.organization import entities as entities_module
from jarvis_core.organization.entities import HQ, Agent, Division, Team
from jarvis_core.ports.i_connector import IConnector

from jarvis_adapter_policy_inmemory.engine import InMemoryPolicyEngine
from jarvis_adapter_workflow_langgraph.langgraph_engine import LangGraphWorkflowEngine
from jarvis_adapter_workflow_sequential.sequential_engine import SequentialWorkflowEngine


class _RecordingConnector(IConnector):
    """Agent가 실제로 이 Connector를 '직접' 호출하는지(Composition Root를 거치지
    않고) 증명하기 위해 호출 기록을 남긴다."""

    def __init__(self) -> None:
        self.call_log: list[ToolRequest] = []

    @property
    def capabilities(self) -> list[str]:
        return ["code-review-tool"]

    def call_tool(self, request: ToolRequest) -> ToolResponse:
        self.call_log.append(request)
        return ToolResponse(status=ToolCallStatus.SUCCESS, result={"reviewed": True})


def _build_registry() -> CapabilityRegistry:
    reg = CapabilityRegistry()
    reg.register(Capability(
        capability_id="dev-hq.code-task.v1", domain="development.general",
        description="개발 작업", input_profile="", output_profile="",
        owner="development-hq", required_permission="standard",
        keywords=["코드", "리뷰"],
    ))
    return reg


class TestStage8AgentCallsConnectorDirectly(unittest.TestCase):
    """Stage 1~6(Kernel + HQ Division Selection)은 Phase 1~4와 완전히 동일한
    코드 경로로 실행하고, Stage 7~9만 Workflow Engine에 위임한다."""

    def _run_kernel_and_hq_selection(self, registry, hqs):
        """Phase 1~4와 동일한 Kernel Stage 1~5. 이 Phase에서 수정되지 않았음을
        그대로 재사용하는 것으로 증명한다."""
        intent = intent_recognition.recognize("저장소 코드 리뷰 좀 해줘")
        classification = task_classification.classify(intent, registry)
        plan = task_router.route(classification, registry)
        policy_engine = InMemoryPolicyEngine({"user-A": "standard"})
        outcome = hq_selection_module.select(plan, intent, registry, hqs, policy_engine, "user-A")
        self.assertTrue(outcome.ok, outcome.reason)
        return outcome.dispatch

    def test_agent_calls_connector_directly_through_workflow_engine(self):
        for engine_kind in ("langgraph", "sequential"):
            with self.subTest(engine=engine_kind):
                registry = _build_registry()
                hq = HQ(hq_id="development-hq", state=hq_state_module.HQState.IDLE)
                # Fixture Agent — required_tools가 채워져 있다고 가정한다(Known Gap 우회,
                # 사용자 승인 사항). Division/HQ 자체는 Phase 1~4와 동일한 실제 클래스다.
                fixture_agent = Agent(
                    role_id="reviewer-1",
                    capability_id="dev-hq.code-task.v1",
                    required_tools=["code-review-tool"],
                )
                hq.divisions["development-hq-division"] = Division(
                    division_id="development-hq-division",
                    hq_id="development-hq",
                    agent_catalog=[fixture_agent],
                )
                hqs = {"development-hq": hq}

                dispatch = self._run_kernel_and_hq_selection(registry, hqs)

                # Stage 6 — Division Selection (HQ 자신의 책임, 무수정)
                division = hq.select_division(dispatch.capability_id)

                # Stage 7 — Team Formation (Division의 책임, 무수정)
                team = Team(division_id=division.division_id, agents=list(division.agent_catalog))

                connector = _RecordingConnector()
                connectors = ConnectorRegistry()
                connectors.register(connector)
                workflow_engine = (
                    LangGraphWorkflowEngine(connectors) if engine_kind == "langgraph"
                    else SequentialWorkflowEngine(connectors)
                )

                # Stage 8~9 — Agent가 Connector를 "직접" 호출(main.py는 관여하지 않음)
                result = workflow_engine.run(team, dispatch)

                self.assertEqual(result.status.value, "success")
                self.assertEqual(len(connector.call_log), 1)
                self.assertEqual(connector.call_log[0].tool_name, "code-review-tool")

    def test_core_layers_do_not_reference_workflow_concept(self):
        """Kernel/HQ Domain(hq_selection, organization/entities, capability_registry,
        lifecycle)의 소스 코드 어디에도 'workflow'라는 단어가 등장하지 않는다 —
        이번 Phase 변경이 이 계층에 전혀 스며들지 않았다는 정적 증거."""
        for module in (hq_selection_module, entities_module, capability_registry_module, hq_state_module):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module).lower()
                self.assertNotIn("workflow", source, f"{module.__name__}에 'workflow' 참조가 있음")


if __name__ == "__main__":
    unittest.main()

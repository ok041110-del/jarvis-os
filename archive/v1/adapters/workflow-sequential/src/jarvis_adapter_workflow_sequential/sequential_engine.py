"""IWorkflowEngine을 순차 함수 호출로 구현한 Adapter.

LangGraph Adapter를 제거하고 이 Adapter로 교체해도 Core/Organization Layer
무수정으로 즉시 복구 가능함을 증명하는 Adapter Reversibility 테스트 전용
Adapter다(policy-inmemory, connector-mock과 동일한 역할) — 프로덕션 배선에는
쓰지 않는다(ADR-0007 이번 Phase의 최종 Architecture Validation 목표 1).
"""
from jarvis_core.application.agent_executor import AgentExecutor
from jarvis_core.connector.models import ToolCallStatus
from jarvis_core.connector_registry.registry import ConnectorRegistry
from jarvis_core.kernel.models import TaskDispatch
from jarvis_core.organization.entities import Team
from jarvis_core.ports.i_workflow_engine import IWorkflowEngine
from jarvis_core.workflow.models import WorkflowResult, WorkflowStatus


class SequentialWorkflowEngine(IWorkflowEngine):
    def __init__(self, connectors: ConnectorRegistry) -> None:
        self._executor = AgentExecutor(connectors)

    def run(self, team: Team, dispatch: TaskDispatch) -> WorkflowResult:
        try:
            team.activate()
            errors: list[str] = []
            for agent in team.agents:
                response = self._executor.execute(agent, dispatch.intent.raw_text)
                if response is not None and response.status != ToolCallStatus.SUCCESS:
                    errors.append(f"{agent.role_id}: {response.error}")
            team.complete()
            team.terminate()
        except Exception as e:
            return WorkflowResult(status=WorkflowStatus.FAILURE, error=f"Workflow 실행 중 내부 오류: {e}")

        if errors:
            return WorkflowResult(status=WorkflowStatus.FAILURE, error="; ".join(errors))
        return WorkflowResult(status=WorkflowStatus.SUCCESS)

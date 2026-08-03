"""agent_executor.py — Application Service (Application Layer, Domain Service 아님).

이번 Phase(ADR-0007)가 이 서비스를 추가하는 이유는 Agent에게 새 책임을 주기
위해서가 아니라, 기존 `apps/poc-runner/main.py` Stage 8에 있던 실행 절차(반복문)를
그대로 Core 쪽으로 옮기기 위해서다 — Agent의 Domain Logic을 추가하지 않는다.

이 서비스가 담당하는 것 (ADR-0006 Connector Execution Model을 그대로 재사용):
  - Agent.required_tools로부터 필요한 Capability를 읽는다.
  - ConnectorRegistry.find_by_capability()로 Connector를 조회한다(Discovery).
  - ToolRequest를 만들어 Connector.call_tool()을 호출한다.
  - ToolResponse를 그대로 반환한다.

이 서비스가 담당하지 않는 것:
  - Agent가 어떤 tool을 요구해야 하는지 결정하는 것 (Agent의 Domain 지식,
    HQProvisioner/Capability 스키마의 몫 — Phase 4부터 이월된 Known Gap이며
    이번 Phase에서도 건드리지 않는다)
  - 호출 순서/병렬 여부를 결정하는 것 (Workflow Engine의 몫, ADR-0007 결정 7)
  - 실패 시 재시도/에스컬레이션 여부 (Policy Engine의 몫, ADR-0005/0006)
  - 허용 여부 판단 (Policy Engine의 몫)
"""
from jarvis_core.connector.models import ToolCallStatus, ToolRequest, ToolResponse
from jarvis_core.connector_registry.registry import ConnectorRegistry
from jarvis_core.organization.entities import Agent


class AgentExecutor:
    """Application Service. main.py Stage 8의 실행 절차를 옮겨온 것일 뿐,
    Agent/Workflow/Policy의 판단을 대신하지 않는다.
    """

    def __init__(self, connectors: ConnectorRegistry) -> None:
        self._connectors = connectors

    def execute(self, agent: Agent, query_text: str) -> ToolResponse | None:
        tool = agent.required_tools[0] if agent.required_tools else None
        if tool is None:
            return None

        connector = self._connectors.find_by_capability(tool)
        if connector is None:
            return ToolResponse(
                status=ToolCallStatus.FAILURE,
                error=f"Capability '{tool}'을 처리할 Connector를 찾지 못함",
            )

        request = ToolRequest(tool_name=tool, arguments={"query": query_text})
        return connector.call_tool(request)

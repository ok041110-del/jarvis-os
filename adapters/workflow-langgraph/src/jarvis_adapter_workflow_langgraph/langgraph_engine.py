"""IWorkflowEngine을 LangGraph로 구현하는 Adapter (ADR-0007).

Team Formation~Agent 실행~Team 종료 구간(Stage 7 끝~Stage 9 시작)만 담당한다.
Kernel(Stage 1~5), HQ의 Division Selection(Stage 6)은 이 Adapter가 개입하기
전에 이미 끝나 있다(ADR-0007 결정 1, 5).

LangGraph의 StateGraph/Node/START/END 문법은 이 파일 내부에서만 쓰인다 — Team/Agent
(Core Domain Model)를 이 파일의 `_WorkflowState`로 변환하는 지점이 LangGraph 문법과
Domain Language의 유일한 경계다(ADR-0007 결정 4).

병렬 실행 가능한 구조(ADR-0007 결정 7): Team에 속한 각 Agent를 activate_team 이후
별도 Node로 fan-out하고 terminate_team 이전에 fan-in한다 — LangGraph의 Superstep
실행 모델이 이 fan-out을 병렬로 처리할 수 있는 구조를 그대로 제공한다. 이번 Phase는
이 "구조"만 검증하며, 실제 병렬 스케줄링 성능이나 동시성 제어는 검증하지 않는다
(향후 별도 Phase에서 Parallel Scheduler/Execution Pool과 함께 다룬다).
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from jarvis_core.application.agent_executor import AgentExecutor
from jarvis_core.connector.models import ToolCallStatus
from jarvis_core.connector_registry.registry import ConnectorRegistry
from jarvis_core.kernel.models import TaskDispatch
from jarvis_core.organization.entities import Agent, Team
from jarvis_core.ports.i_workflow_engine import IWorkflowEngine
from jarvis_core.workflow.models import WorkflowResult, WorkflowStatus


class _WorkflowState(TypedDict):
    team: Team
    dispatch: TaskDispatch
    errors: Annotated[list[str], operator.add]


class LangGraphWorkflowEngine(IWorkflowEngine):
    def __init__(self, connectors: ConnectorRegistry) -> None:
        self._executor = AgentExecutor(connectors)

    def run(self, team: Team, dispatch: TaskDispatch) -> WorkflowResult:
        try:
            graph = self._build_graph(team)
            result_state = graph.invoke({"team": team, "dispatch": dispatch, "errors": []})
        except Exception as e:
            return WorkflowResult(status=WorkflowStatus.FAILURE, error=f"Workflow 실행 중 내부 오류: {e}")

        errors = result_state.get("errors") or []
        if errors:
            return WorkflowResult(status=WorkflowStatus.FAILURE, error="; ".join(errors))
        return WorkflowResult(status=WorkflowStatus.SUCCESS)

    def _build_graph(self, team: Team):
        graph = StateGraph(_WorkflowState)
        graph.add_node("activate_team", self._activate_team)
        graph.add_node("terminate_team", self._terminate_team)
        graph.add_edge(START, "activate_team")

        if not team.agents:
            graph.add_edge("activate_team", "terminate_team")
        else:
            for index, agent in enumerate(team.agents):
                node_name = f"agent_{index}_{agent.role_id}"
                graph.add_node(node_name, self._make_agent_node(agent))
                graph.add_edge("activate_team", node_name)   # fan-out (병렬 실행 가능한 구조)
                graph.add_edge(node_name, "terminate_team")  # fan-in

        graph.add_edge("terminate_team", END)
        return graph.compile()

    def _activate_team(self, state: _WorkflowState) -> dict:
        state["team"].activate()
        return {}

    def _terminate_team(self, state: _WorkflowState) -> dict:
        state["team"].complete()
        state["team"].terminate()
        return {}

    def _make_agent_node(self, agent: Agent):
        def _node(state: _WorkflowState) -> dict:
            dispatch = state["dispatch"]
            response = self._executor.execute(agent, dispatch.intent.raw_text)
            if response is not None and response.status != ToolCallStatus.SUCCESS:
                return {"errors": [f"{agent.role_id}: {response.error}"]}
            return {}
        return _node

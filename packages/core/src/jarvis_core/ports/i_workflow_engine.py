"""i_workflow_engine.py — Port(Interface) 정의. ADR-0007.
Core는 이 Interface만 알고, 실제 구현(LangGraph/Sequential/...)은 모른다.
adapters/ 아래 패키지가 이 Interface를 implements 한다.

Workflow는 HQ/Connector와 달리 Plugin이 아니다(ADR-0007 결정 12) — 여러
구현체가 동시에 Discovery/Registry로 발견·선택되는 대상이 아니라, Composition
Root가 조립 시점에 하나만 선택해 Team에 주입하는 단일 실행 엔진이다.
"""
from abc import ABC, abstractmethod

from jarvis_core.kernel.models import TaskDispatch
from jarvis_core.organization.entities import Team
from jarvis_core.workflow.models import WorkflowResult


class IWorkflowEngine(ABC):
    @abstractmethod
    def run(self, team: Team, dispatch: TaskDispatch) -> WorkflowResult:
        """Team을 구성하는 Agent들의 실행 순서를 조립하고 진행시킨 뒤,
        Team이 TERMINATED에 도달하면 WorkflowResult를 반환한다.
        예외를 던지지 않는다 — 실패는 WorkflowResult.status로 표현한다
        (Fail-Closed 계약, ADR-0005 결정 4/ADR-0006 결정 9와 동일한 패턴).
        """
        raise NotImplementedError

"""MVP-0007: Artifact Flow 관찰 — Issue -> Planning(Requirement) ->
Design(Architecture) -> Implementation(Code).

이번 MVP의 관찰 대상은 Project Intelligence가 아니라 Artifact
전달 경로다. Project Intelligence(`collect_relevant_context`,
MVP-0005/0006)는 Planning에서만 사용한다 — Design/Implementation에는
Relevant Context를 전달하지 않는다. MVP-0006과 달리 Design에는
Context가 섞이지 않은 원본 Issue를 그대로 넘긴다.

기존 Task Dispatcher 패턴(하드코딩된 순차 함수 호출, ADC-0002/0004에서
Keep in MVP로 유지됨)을 그대로 재사용한다. 새로운 Dispatcher/Runtime/
Stage Runner/Pipeline Runner를 만들지 않는다. 새 Capability도 추가하지
않는다 — `agents.py`의 기존 4개 함수(requirement_analysis, design,
code_generation)만 그대로 호출한다.
"""

from .agents import (
    backend_agent_code_generation,
    design_agent_design,
    requirements_agent_requirement_analysis,
)
from .project_intelligence import collect_relevant_context
from .workflow import _engine_failure_message
from .workflow_project_intelligence import _enrich_issue


def run_issue_to_implementation(issue: dict) -> dict:
    """Issue를 Planning(PI 포함) -> Design -> Implementation까지
    순서대로 통과시키고, 각 단계에서 실제로 넘어간 Artifact를 그대로
    반환해 전달 경로를 관찰할 수 있게 한다.

    MVP-0037: `run_mvp_0001`(MVP-0036)과 동일한 이유로 Engine 호출
    실패(예: timeout)를 잡아 기존 반환 계약(4개 키)을 유지한 채
    반환한다. `context`는 Engine 호출 없이 이미 계산된 값이므로
    실패 시에도 그대로 유지한다."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    try:
        requirement = requirements_agent_requirement_analysis(enriched_issue)
        design = design_agent_design(issue, requirement)
        code = backend_agent_code_generation(design)
    except Exception as exc:
        error_message = _engine_failure_message(exc)
        return {
            "context": context,
            "planning": error_message,
            "design": error_message,
            "implementation": error_message,
        }

    return {
        "context": context,
        "planning": requirement,
        "design": design,
        "implementation": code,
    }

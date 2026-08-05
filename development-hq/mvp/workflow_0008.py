"""MVP-0008: Development HQ가 Development HQ의 실제 Issue 하나를
Planning -> Design -> Implementation -> Validation까지 처리한다.

Issue는 이 저장소 자신의 실제 백로그 항목이다 — MVP-0007 Observation
(`docs/01_mvp/MVP-0007-observation.md`)에서 실측으로 발견한 문제
("Design/Implementation Stage가 상위 Artifact를 요약 없이 그대로
이어붙여, Project Intelligence가 Planning에서 수집한 Relevant
Context가 의도치 않게 Design/Implementation까지 전달된다")를 다루는
"Project Intelligence 개선" Issue를 그대로 입력으로 사용한다.

Pipeline은 Planning -> Design -> Implementation -> Validation까지
유지한다(MVP-0004 `workflow_hello_sdlc.py`와 동일한 4단계). Project
Intelligence(`collect_relevant_context`, MVP-0005/0006)는 Planning
호출 직전에서만 사용한다 — Design에는 원본(Context 없는) Issue를
그대로 넘긴다(MVP-0007과 동일).

새 Capability를 추가하지 않는다 — `agents.py`의 기존 5개 함수
(requirement_analysis, design, code_generation, code_review,
test_execution)만 그대로 순서대로 호출한다. Task Dispatcher, Runtime,
Stage Runner, Pipeline Runner는 구현하지 않는다.
"""

from .agents import (
    backend_agent_code_generation,
    backend_agent_code_review,
    design_agent_design,
    qa_agent_test_execution,
    requirements_agent_requirement_analysis,
)
from .project_intelligence import collect_relevant_context
from .workflow_project_intelligence import _enrich_issue

REAL_ISSUE = {
    "title": "Project Intelligence 개선",
    "description": (
        "MVP-0007 Observation에서 실측으로 확인됨: design_agent_design과 "
        "backend_agent_code_generation은 상위 Stage의 Artifact(Requirement, "
        "Design) 전체를 요약 없이 그대로 이어붙인다. 그 결과 Project "
        "Intelligence가 Planning에서만 수집한 Relevant Context가 Design과 "
        "Implementation 산출물에도 의도치 않게 그대로 나타난다. Project "
        "Intelligence(collect_relevant_context)가 이 문제를 완화할 수 있는 "
        "방향으로 개선될 수 있는지 검토가 필요하다."
    ),
    "status": "Open",
}


def run_pipeline(issue: dict) -> dict:
    """Issue를 Planning(PI 포함) -> Design -> Implementation ->
    Validation까지 순서대로 통과시킨다."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    requirement = requirements_agent_requirement_analysis(enriched_issue)
    design = design_agent_design(issue, requirement)
    code = backend_agent_code_generation(design)
    review = backend_agent_code_review(code)
    test_cases = qa_agent_test_execution(code, review)

    return {
        "context": context,
        "planning": requirement,
        "design": design,
        "implementation": code,
        "validation": {"code_review": review, "test_execution": test_cases},
    }

"""MVP-0008: Planning -> Design -> Implementation -> Validation.
Project Intelligence는 Planning 직전에만 사용한다 — Design에는 원본 Issue를 그대로 넘긴다.
"""

from .agents.backend import backend_agent_code_generation, backend_agent_code_review
from .agents.design import design_agent_design
from .agents.qa import qa_agent_test_execution
from .agents.requirements import requirements_agent_requirement_analysis
from .project_intelligence import collect_relevant_context
from .workflow import _engine_failure_message
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
    """Engine 호출 실패 시에도 기존 반환 계약(5개 키)을 유지하며,
    `context`는 실패 시에도 그대로 유지한다."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    try:
        requirement = requirements_agent_requirement_analysis(enriched_issue)
        design = design_agent_design(issue, requirement)
        code = backend_agent_code_generation(design)
        review = backend_agent_code_review(code)
        test_cases = qa_agent_test_execution(code, review)
    except Exception as exc:
        error_message = _engine_failure_message(exc)
        return {
            "context": context,
            "planning": error_message,
            "design": error_message,
            "implementation": error_message,
            "validation": {"code_review": error_message, "test_execution": error_message},
        }

    return {
        "context": context,
        "planning": requirement,
        "design": design,
        "implementation": code,
        "validation": {"code_review": review, "test_execution": test_cases},
    }

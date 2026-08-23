"""MVP-0007: Artifact Flow 관찰 — Issue -> Planning -> Design -> Implementation.
Project Intelligence는 Planning에서만 쓰고, Design/Implementation에는 원본 Issue를 그대로 넘긴다(MVP-0006과의 차이)."""

from .agents.backend import backend_agent_code_generation
from .agents.design import design_agent_design
from .agents.requirements import requirements_agent_requirement_analysis
from .project_intelligence import collect_relevant_context
from .workflow import _engine_failure_message
from .workflow_project_intelligence import _enrich_issue


def run_issue_to_implementation(issue: dict) -> dict:
    """Engine 호출 실패 시에도 기존 반환 계약(4개 키)을 유지하며,
    `context`는 실패 시에도 그대로 유지한다."""
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

"""MVP-0005/0006: Issue -> Project Intelligence -> Relevant Context -> Planning(-> Design).
Relevant Context는 기존 함수 시그니처를 바꾸지 않고 Issue `description`에 덧붙여 전달한다."""

from .agents.design import design_agent_design
from .agents.requirements import requirements_agent_requirement_analysis
from .project_intelligence import collect_relevant_context
from .workflow import _engine_failure_message


def _summarize_context(context: dict) -> str:
    lines = [f"{category}: {', '.join(files)}" for category, files in context.items() if files and category != "directory_structure"]
    return "\n".join(lines) if lines else "(관련 자료 없음)"


def _enrich_issue(issue: dict, context: dict) -> dict:
    enriched_issue = dict(issue)
    enriched_issue["description"] = (
        f"{issue['description']}\n\n[Relevant Context]\n{_summarize_context(context)}"
    )
    return enriched_issue


def run_issue_to_planning(issue: dict) -> dict:
    """Engine 호출 실패 시에도 기존 반환 계약(2개 키)을 유지한다.
    `workflow_0009.run_comparison()`의 flat-context 절반이 이 함수를 재사용한다."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    try:
        requirement = requirements_agent_requirement_analysis(enriched_issue)
    except Exception as exc:
        return {
            "context": context,
            "planning": _engine_failure_message(exc),
        }

    return {
        "context": context,
        "planning": requirement,
    }


def run_issue_to_design(issue: dict) -> dict:
    """동일 Context를 Planning/Design 양쪽에 재사용한다(Stage마다 재수집하지 않음).
    Engine 호출 실패 시에도 기존 반환 계약(3개 키)을 유지한다."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    try:
        requirement = requirements_agent_requirement_analysis(enriched_issue)
        design = design_agent_design(enriched_issue, requirement)
    except Exception as exc:
        error_message = _engine_failure_message(exc)
        return {
            "context": context,
            "planning": error_message,
            "design": error_message,
        }

    return {
        "context": context,
        "planning": requirement,
        "design": design,
    }

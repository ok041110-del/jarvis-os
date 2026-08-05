"""MVP-0005: Issue -> Project Intelligence -> Relevant Context -> Planning.

기존 Task Dispatcher 패턴(하드코딩된 순차 함수 호출, ADC-0002/0004에서
Keep in MVP로 유지됨)을 그대로 재사용한다. 새로운 Dispatcher/Runtime/
Stage Runner/Pipeline Runner를 만들지 않는다.

Planning Capability(`requirements_agent_requirement_analysis`, MVP-0004)
는 수정하지 않는다. Relevant Context는 Issue의 `description`에 덧붙여
전달한다 — 기존 함수 시그니처를 바꾸지 않고 Context가 Planning에
도달하는 것만 보인다.
"""

from .agents import requirements_agent_requirement_analysis
from .project_intelligence import collect_relevant_context


def _summarize_context(context: dict) -> str:
    lines = [f"{category}: {', '.join(files)}" for category, files in context.items() if files and category != "directory_structure"]
    return "\n".join(lines) if lines else "(관련 자료 없음)"


def run_issue_to_planning(issue: dict) -> dict:
    """Issue를 받아 Project Intelligence로 Relevant Context를 수집하고,
    Planning(requirement_analysis)에 그대로 전달한다."""
    context = collect_relevant_context(issue)

    enriched_issue = dict(issue)
    enriched_issue["description"] = (
        f"{issue['description']}\n\n[Relevant Context]\n{_summarize_context(context)}"
    )

    requirement = requirements_agent_requirement_analysis(enriched_issue)

    return {
        "context": context,
        "planning": requirement,
    }

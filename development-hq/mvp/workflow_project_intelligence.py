"""MVP-0005/0006: Issue -> Project Intelligence -> Relevant Context ->
Planning(-> Design).

기존 Task Dispatcher 패턴(하드코딩된 순차 함수 호출, ADC-0002/0004에서
Keep in MVP로 유지됨)을 그대로 재사용한다. 새로운 Dispatcher/Runtime/
Stage Runner/Pipeline Runner를 만들지 않는다.

Planning Capability(`requirements_agent_requirement_analysis`, MVP-0004)와
Design Capability(`design_agent_design`, MVP-0004)는 수정하지 않는다.
Relevant Context는 Issue의 `description`에 덧붙여 전달한다 — 기존 함수
시그니처를 바꾸지 않고 Context가 각 Stage에 도달하는 것만 보인다.

MVP-0005는 `run_issue_to_planning`(Planning까지)을 추가했다. MVP-0006은
새 Capability를 추가하지 않고, 같은 `collect_relevant_context()` 결과를
Design Stage까지 그대로 재사용하는 `run_issue_to_design`을 추가한다.
"""

from .agents import design_agent_design, requirements_agent_requirement_analysis
from .project_intelligence import collect_relevant_context


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
    """Issue를 받아 Project Intelligence로 Relevant Context를 수집하고,
    Planning(requirement_analysis)에 그대로 전달한다."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    requirement = requirements_agent_requirement_analysis(enriched_issue)

    return {
        "context": context,
        "planning": requirement,
    }


def run_issue_to_design(issue: dict) -> dict:
    """Issue를 받아 Project Intelligence로 Relevant Context를 한 번
    수집하고, 동일한 Context가 담긴 Issue를 Planning과 Design 양쪽에
    그대로 전달한다 — `collect_relevant_context()`를 Stage마다 다시
    호출하지 않고 재사용하는지를 관찰하기 위함이다."""
    context = collect_relevant_context(issue)
    enriched_issue = _enrich_issue(issue, context)

    requirement = requirements_agent_requirement_analysis(enriched_issue)
    design = design_agent_design(enriched_issue, requirement)

    return {
        "context": context,
        "planning": requirement,
        "design": design,
    }

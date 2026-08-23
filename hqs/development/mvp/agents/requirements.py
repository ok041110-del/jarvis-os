"""Requirements Agent — requirement_analysis Capability(Agent Package
Refactoring, `DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` §2)."""

from ..engine import call_engine


def requirements_agent_requirement_analysis(issue: dict) -> str:
    """리터럴 마커만으로는 Engine이 의도를 놓치고 코드를 바로 작성하는 등의
    사례가 있어 한 문장짜리 지시를 앞에 붙인다."""
    instruction = (
        "Analyze the following feature request and describe the "
        "requirement in prose (goal, scope, risks) — do not write code."
    )
    payload = f"{issue['title']}|||{issue['description']}"
    return call_engine(f"REQUIREMENT_ANALYSIS:{instruction}\n\n{payload}")

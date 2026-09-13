"""Design Agent — design Capability(Agent Package Refactoring,
`DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` §2). Multi-Engine Architecture
3번째 Engine인 OpenRouter Free Model Selection(`ADR-0027`)을 사용한다."""

from ..openrouter_engine import call_engine_via_openrouter as call_engine


def design_agent_design(issue: dict, requirement: str) -> str:
    """Design Agent가 design Capability를 수행한다. 지시 문장의 목적은
    `requirements_agent_requirement_analysis`와 같다."""
    instruction = (
        "Based on the following requirement, describe a design in prose "
        "(approach, responsibilities, risks) — do not write code yet."
    )
    payload = f"{issue['title']}\n---REQUIREMENT---\n{requirement}"
    return call_engine(f"DESIGN:{instruction}\n\n{payload}")

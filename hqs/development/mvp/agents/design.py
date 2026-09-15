from ..openrouter_engine import call_engine_via_openrouter as call_engine


def design_agent_design(issue: dict, requirement: str) -> str:
    instruction = (
        "Based on the following requirement, describe a design in prose "
        "(approach, responsibilities, risks) — do not write code yet."
    )
    payload = f"{issue['title']}\n---REQUIREMENT---\n{requirement}"
    return call_engine(f"DESIGN:{instruction}\n\n{payload}")

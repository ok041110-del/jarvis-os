"""MVP-0004: Hello SDLC — 가장 작은 End-to-End Pipeline. `workflow.py`/
`workflow_0002.py`와 별개의 순차 호출 체인이며 Issue 하나를 끝까지 통과시키는 것이 목적."""

from .agents.backend import backend_agent_code_generation, backend_agent_code_review
from .agents.design import design_agent_design
from .agents.qa import qa_agent_test_execution
from .agents.requirements import requirements_agent_requirement_analysis


def run_hello_sdlc(issue: dict) -> dict:
    try:
        requirement = requirements_agent_requirement_analysis(issue)
        design = design_agent_design(issue, requirement)
        code = backend_agent_code_generation(design)
        review = backend_agent_code_review(code)
        test_cases = qa_agent_test_execution(code, review)
    except Exception as exc:
        return {
            "planning": None,
            "design": None,
            "implementation": None,
            "validation": None,
            "status": "Failed",
            "error": str(exc),
        }

    return {
        "planning": requirement,
        "design": design,
        "implementation": code,
        "validation": {"code_review": review, "test_execution": test_cases},
        "status": "Complete",
    }

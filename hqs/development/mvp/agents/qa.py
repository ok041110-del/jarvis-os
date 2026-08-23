"""QA Agent — test_execution Capability(Agent Package Refactoring,
`DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` §2)."""

from ..engine import call_engine


def qa_agent_test_execution(code: str, review: str) -> str:
    """QA Agent의 test_execution Capability(테스트 케이스 제안, MVP-0025)."""
    instruction = (
        "Based on the following code and its review, propose a list of "
        "test cases to add — do not review the code again."
    )
    payload = f"{code}\n---REVIEW---\n{review}"
    return call_engine(f"TEST_EXECUTION:{instruction}\n\n{payload}")

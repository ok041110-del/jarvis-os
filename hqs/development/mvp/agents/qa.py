"""QA Agent — test_execution Capability(`DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` §2). Claude Code Engine을 쓴다 — repository test 실행과 개념적으로 가장 가까운 Capability이기 때문이며, Contract는 여전히 텍스트 제안 반환만 한다(실제 test 실행 권한은 없음, `ADR-0024` §Non-goal)."""

from ..engine import call_engine


def qa_agent_test_execution(code: str, review: str) -> str:
    instruction = (
        "Based on the following code and its review, propose a list of "
        "test cases to add — do not review the code again."
    )
    payload = f"{code}\n---REVIEW---\n{review}"
    return call_engine(f"TEST_EXECUTION:{instruction}\n\n{payload}")

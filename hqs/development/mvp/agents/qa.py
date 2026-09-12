"""QA Agent — test_execution Capability(Agent Package Refactoring,
`DEV-HQ-V2.0-AGENT-DEFINITION-0001.md` §2).

Multi-Engine Architecture(`ADR-0024` Stage Mapping) 이후 test_execution은
Claude Code Engine을 쓴다 — repository test 실행과 개념적으로 가장
가까운 Capability이기 때문(Contract는 여전히 텍스트 제안 반환만 하며,
실제 repository test 실행 권한을 이 함수가 갖는 것은 아니다 — `ADR-0024`
§Non-goal)."""

from ..engine import call_engine


def qa_agent_test_execution(code: str, review: str) -> str:
    """QA Agent의 test_execution Capability(테스트 케이스 제안, MVP-0025)."""
    instruction = (
        "Based on the following code and its review, propose a list of "
        "test cases to add — do not review the code again."
    )
    payload = f"{code}\n---REVIEW---\n{review}"
    return call_engine(f"TEST_EXECUTION:{instruction}\n\n{payload}")

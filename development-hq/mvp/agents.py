"""Agent-Capability 매핑과 Agent 함수.

IMPLEMENTATION_RULES.md: "Registry 구현 금지 — Agent-Capability 매핑은
리터럴 딕셔너리 이상으로 발전시키지 않는다." AGENT_CAPABILITY_MAP은 그 리터럴
딕셔너리이며, 조회 함수/클래스로 감싸지 않는다.

Stop Trigger 감시 지점: 이 딕셔너리가 동적 등록 API나 클래스로 바뀌려는 순간
Registry 일반화이므로 즉시 중단하고 RFC로 넘긴다 (HANDOVER.md 참조).
"""

from .engine import call_engine

AGENT_CAPABILITY_MAP = {
    "code_review": "Backend Agent",
    "test_execution": "QA Agent",
}


def backend_agent_code_review(code: str) -> str:
    """Backend Agent가 code_review Capability를 수행한다."""
    return call_engine(f"CODE_REVIEW:{code}")


def qa_agent_test_execution(code: str, review: str) -> str:
    """QA Agent가 test_execution Capability(테스트 케이스 제안)를 수행한다."""
    payload = f"{code}\n---REVIEW---\n{review}"
    return call_engine(f"TEST_EXECUTION:{payload}")

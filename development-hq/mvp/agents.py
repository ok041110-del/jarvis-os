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

# MVP-0004(Hello SDLC)가 추가하는 Capability만 담는 별도 리터럴 딕셔너리.
# AGENT_CAPABILITY_MAP(MVP-0001)을 확장하지 않는다 — 그 딕셔너리를 정확히
# 2개 항목으로 고정해 검증하는 기존 테스트(test_mvp_0001.py)를 그대로
# 유지하기 위함이다. 이 분리 자체가 Registry 중복 관리(RT-0001 Trigger)로
# 이어지는지는 MVP-0004-observation.md에서 관찰만 하고 판단하지 않는다.
HELLO_SDLC_CAPABILITY_MAP = {
    "requirement_analysis": "Requirements Agent",
    "design": "Design Agent",
    "code_generation": "Backend Agent",
}


def backend_agent_code_review(code: str) -> str:
    """Backend Agent가 code_review Capability를 수행한다."""
    return call_engine(f"CODE_REVIEW:{code}")


def qa_agent_test_execution(code: str, review: str) -> str:
    """QA Agent가 test_execution Capability(테스트 케이스 제안)를 수행한다."""
    payload = f"{code}\n---REVIEW---\n{review}"
    return call_engine(f"TEST_EXECUTION:{payload}")


def requirements_agent_requirement_analysis(issue: dict) -> str:
    """Requirements Agent가 requirement_analysis Capability를 수행한다."""
    payload = f"{issue['title']}|||{issue['description']}"
    return call_engine(f"REQUIREMENT_ANALYSIS:{payload}")


def design_agent_design(issue: dict, requirement: str) -> str:
    """Design Agent가 design Capability를 수행한다."""
    payload = f"{issue['title']}\n---REQUIREMENT---\n{requirement}"
    return call_engine(f"DESIGN:{payload}")


def backend_agent_code_generation(design: str) -> str:
    """Backend Agent가 code_generation Capability를 수행한다."""
    return call_engine(f"CODE_GENERATION:{design}")

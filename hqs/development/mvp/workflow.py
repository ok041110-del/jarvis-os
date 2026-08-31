"""MVP-0001 Workflow: Task 1(code_review) -> Task 2(test_execution), 직접
함수 호출로 하드코딩(MVP.md/IMPLEMENTATION_RULES.md, Kernel Extraction Candidate는 HANDOVER.md)."""

from .agents.backend import backend_agent_code_review
from .agents.qa import qa_agent_test_execution


_ENGINE_FAILURE_PREFIX = "Engine call failed:"


def _engine_failure_message(exc: Exception) -> str:
    """`workflow_0002/0008/0009/artifact_flow/project_intelligence.py`가
    공유하는 오류 메시지 포맷 (`workflow_hello_sdlc.py`는 제외)."""
    return f"{_ENGINE_FAILURE_PREFIX} {exc}"


def is_engine_failure(text: str) -> bool:
    """`_engine_failure_message()`가 만든 값인지 판정 — Stage 05가 접두사
    리터럴을 직접 중복 보유하지 않고 이 판정을 그대로 사용한다."""
    return text.startswith(_ENGINE_FAILURE_PREFIX)


def run_mvp_0001(code: str) -> dict:
    """Engine 호출 실패를 잡아 MVP.md의 반환 계약(2개 키)을 유지한 채
    오류 메시지로 반환한다."""
    try:
        review = backend_agent_code_review(code)
        test_cases = qa_agent_test_execution(code, review)
    except Exception as exc:
        error_message = _engine_failure_message(exc)
        return {
            "code_review": error_message,
            "test_execution": error_message,
        }

    return {
        "code_review": review,
        "test_execution": test_cases,
    }

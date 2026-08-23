"""MVP-0001 Workflow: Task 1(code_review) -> Task 2(test_execution), 직접
함수 호출로 하드코딩(MVP.md/IMPLEMENTATION_RULES.md, Kernel Extraction Candidate는 HANDOVER.md)."""

from .agents import backend_agent_code_review, qa_agent_test_execution


def _engine_failure_message(exc: Exception) -> str:
    """`workflow_0002/0008/0009/artifact_flow/project_intelligence.py`가
    공유하는 오류 메시지 포맷 (`workflow_hello_sdlc.py`는 제외)."""
    return f"Engine call failed: {exc}"


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

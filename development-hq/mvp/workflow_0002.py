"""MVP-0002: `NO_ISSUES_MARKER`로 code review 결과를 분기하며,
이슈가 없으면 test execution을 생략한다."""

from .agents import NO_ISSUES_MARKER, backend_agent_code_review, qa_agent_test_execution
from .workflow import _engine_failure_message


def _strip_trailing_marker(review: str, marker: str) -> str:
    """`backend_agent_code_review`의 지시가 요구하는 정확한 형태
    (마지막 줄이 정확히 `marker`)일 때만 제거한다."""
    lines = review.rstrip().splitlines()
    if lines and lines[-1].strip() == marker:
        return "\n".join(lines[:-1]).rstrip()
    return review


def run_mvp_0002(code: str) -> dict:
    """Engine 호출 실패 시에도 기존 반환 계약(2개 키)을 유지한다."""
    try:
        review = backend_agent_code_review(code)

        if NO_ISSUES_MARKER in review:
            test_cases = "(생략됨: code_review에서 이슈가 발견되지 않아 test_execution을 건너뜀)"
            review = _strip_trailing_marker(review, NO_ISSUES_MARKER)
        else:
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

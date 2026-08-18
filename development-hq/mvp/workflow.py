"""MVP-0001 Workflow: Task 1 (code_review) -> Task 2 (test_execution).

MVP.md: "Task 1의 출력(리뷰 코멘트)이 Task 2의 입력 컨텍스트로 전달된다.
2단계, 단일 선형 체인. 분기·재시도·병렬 실행 없음."

IMPLEMENTATION_RULES.md: "Workflow Parser 구현 금지 — Task 1->Task 2는 직접
함수 호출로 충분." run_mvp_0001()이 그 직접 호출이다. 조건문/설정 파일로
Task 순서를 표현하지 않는다.

Kernel Extraction Candidate:
- Task Dispatcher: 아래 두 줄의 순차 함수 호출이 이를 대신한다.
- Context 전달 메커니즘: `review` 지역 변수가 Task 1 -> Task 2 컨텍스트 전달을
  대신한다 (in-memory, 영속화 없음).
"""

from .agents import backend_agent_code_review, qa_agent_test_execution


def _engine_failure_message(exc: Exception) -> str:
    """Engine 호출 실패(예: timeout) 시 반환 dict에 채워 넣는 공통 오류
    메시지 포맷. P1-1: `workflow_0002/0008/0009/artifact_flow/
    project_intelligence.py`에 반복되던 동일한 `f"Engine call failed:
    {exc}"` 포맷 한 줄만 추출한 것이며, 각 호출부의 반환 dict shape·
    Task 순서·Agent-Capability 매핑·Prompt는 전혀 바꾸지 않는다
    (`workflow_hello_sdlc.py`는 이 포맷을 쓰지 않으므로 제외됨)."""
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

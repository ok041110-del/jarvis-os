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


def run_mvp_0001(code: str) -> dict:
    """입력 코드에 대해 code_review -> test_execution을 순서대로 실행한다.

    MVP-0036: `call_engine()`은 Engine 호출 실패(예: timeout)를 별도로
    처리하지 않고 그대로 전파한다 — 이전에는 이 함수가 그 예외를 그대로
    다시 전파해 `cli.py`가 raw traceback으로 죽었다(실제 timeout으로
    재현). `workflow_hello_sdlc.run_hello_sdlc()`가 이미 쓰는 것과 같은
    `try/except`로, MVP.md의 반환 계약(`code_review`/`test_execution`
    두 키)을 그대로 유지한 채 오류 메시지를 담아 반환한다."""
    try:
        review = backend_agent_code_review(code)
        test_cases = qa_agent_test_execution(code, review)
    except Exception as exc:
        error_message = f"Engine call failed: {exc}"
        return {
            "code_review": error_message,
            "test_execution": error_message,
        }

    return {
        "code_review": review,
        "test_execution": test_cases,
    }

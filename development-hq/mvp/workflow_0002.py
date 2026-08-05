"""MVP-0002: RT-0001 Task Dispatcher Trigger("Workflow Branch 발생") 관찰용
최소 구현.

`docs/01_mvp/MVP-0002-plan.md` 범위: 기존 두 줄의 순차 호출(`workflow.py`
`run_mvp_0001`)에 조건 분기 1개만 추가한다. MVP-0001의 `workflow.py`는
수정하지 않는다(그 문서·테스트가 "분기 없음"을 그대로 검증하고 있으므로).

분기는 정확히 1개다: code_review 결과에 이슈가 없으면 test_execution을
건너뛴다. 새 Capability/Agent/Engine을 추가하지 않으며, 분기 이후 다시
동일한 반환 형태로 합류한다.
"""

from .agents import backend_agent_code_review, qa_agent_test_execution

NO_ISSUE_MARKER = "뚜렷한 이슈가 발견되지 않았습니다."


def run_mvp_0002(code: str) -> dict:
    """code_review -> (조건 분기) -> test_execution 또는 생략."""
    review = backend_agent_code_review(code)

    if NO_ISSUE_MARKER in review:
        test_cases = "(생략됨: code_review에서 이슈가 발견되지 않아 test_execution을 건너뜀)"
    else:
        test_cases = qa_agent_test_execution(code, review)

    return {
        "code_review": review,
        "test_execution": test_cases,
    }

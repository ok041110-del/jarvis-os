"""MVP-0002: RT-0001 Task Dispatcher Trigger("Workflow Branch 발생") 관찰용
최소 구현.

`docs/01_mvp/MVP-0002-plan.md` 범위: 기존 두 줄의 순차 호출(`workflow.py`
`run_mvp_0001`)에 조건 분기 1개만 추가한다. MVP-0001의 `workflow.py`는
수정하지 않는다(그 문서·테스트가 "분기 없음"을 그대로 검증하고 있으므로).

분기는 정확히 1개다: code_review 결과에 이슈가 없으면 test_execution을
건너뛴다. 새 Capability/Agent/Engine을 추가하지 않으며, 분기 이후 다시
동일한 반환 형태로 합류한다.

MVP-0027: 분기 판단 마커를 rule-based Engine의 고정 문자열("뚜렷한
이슈가 발견되지 않았습니다.")에서 `agents.NO_ISSUES_MARKER`로
바꿨다 — ENGINE-CONNECT-0001 이후 `call_engine()`이 실제 Engine을
호출하면서 그 고정 문자열이 더 이상 나오지 않아 분기가 항상
test_execution을 실행하는 쪽으로만 동작하는 것을 실제 실행으로
확인했다(MVP-0027 Observation). 마커 자체는 `agents.py`의
`backend_agent_code_review` 지시 문장에서 요청한다 — 이 파일은
그 마커를 그대로 재사용해 분기만 판단한다.

MVP-0040: 실제 Engine으로 재확인함 — 이슈가 없는 코드를 실제로
실행하면 `code_review`에 분기 판단용 마커(`NO_ISSUES_FOUND`)가 그대로
남아 사람이 읽는 리뷰 텍스트 마지막 줄에 노출됐다("... 코드가 좋다는
설명 ...\n\nNO_ISSUES_FOUND\n"). 마커는 이 파일이 분기를 판단하기
위한 신호일 뿐 `code_review` 결과 자체의 일부가 아니므로, 판단에 쓴
뒤에는 반환 전에 제거한다 — `_strip_code_fence`(MVP-0039,
`agents.py`)와 같은 종류의 "Capability 출력에서 그 결과의 일부가
아닌 신호만 제거하는" 최소 후처리다.
"""

from .agents import NO_ISSUES_MARKER, backend_agent_code_review, qa_agent_test_execution
from .workflow import _engine_failure_message


def _strip_trailing_marker(review: str, marker: str) -> str:
    """`review`의 마지막 줄이 정확히 `marker`이면 그 줄(과 그 앞의
    공백 줄)만 제거한다. 마커가 다른 위치에 있거나 없으면 원문을
    그대로 반환한다 — `backend_agent_code_review`의 지시("이슈가
    없을 때만 응답 마지막 줄에 정확히 NO_ISSUES_FOUND를 적으라",
    MVP-0027)가 요구하는 형태만 제거 대상으로 삼는다."""
    lines = review.rstrip().splitlines()
    if lines and lines[-1].strip() == marker:
        return "\n".join(lines[:-1]).rstrip()
    return review


def run_mvp_0002(code: str) -> dict:
    """code_review -> (조건 분기) -> test_execution 또는 생략.

    MVP-0037: `run_mvp_0001`(MVP-0036)과 동일한 이유로 Engine 호출
    실패(예: timeout)를 잡아 기존 반환 계약(2개 키)을 유지한 채
    반환한다."""
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

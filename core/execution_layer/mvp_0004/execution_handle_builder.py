"""Execution Layer MVP-0004: ExecutionHandleBuilder.

Model Request(Execution Layer MVP-0003의 Artifact)를 Execution Handle
(Execution Layer의 네 번째 공식 Artifact)로 변환한다.

Contract (요청 원문 기준):
- Input: Model Request (`str`, MVP-0003 `build_model_request()`가 생성하는
  형태).
- Output: Execution Handle (`str`).
- Execution Handle은 Model Request를 그대로 참조한다(수정하지 않는다).
  추가되는 것은 실행 상태 메타데이터뿐이다(handle_id, request_id, status,
  submitted_at, artifact_version).
- status는 이번 MVP에서 `"PENDING"` 고정값 하나만 사용한다. RUNNING/
  COMPLETED/FAILED/CANCELLED는 다루지 않는다.
- Execution Handle은 실행 상태를 표현할 뿐 실행 자체를 수행하지 않는다.
  AI/LLM/Model 호출 없음. HTTP 없음. Session/Runtime/Retry/Scheduler
  구현 없음. 시스템 시계 접근 없음. Handle ID 생성 없음.

## handle_id / submitted_at을 이 모듈이 생성하지 않는 이유

MVP-0003의 `request_id`/`created_at`과 동일한 이유다: 고유 ID를 발급하고
시각을 기록하는 행위는 "무엇이 언제 제출되었는가"를 추적하는 Session/
Runtime의 책임 영역과 겹친다. 그래서 `build_execution_handle()`은
`handle_id`와 `submitted_at`을 내부에서 생성하지 않고, 호출자가 주입한
값을 그대로 담기만 한다. `request_id`는 새로 주입받지 않는다 — Model
Request의 `## Metadata` 절에 이미 있는 값을 그대로 읽어서 재사용한다
(Model Request를 Canonical한 참조 대상으로 유지하기 위해, 같은 정보를
두 번 입력받아 서로 어긋날 위험을 만들지 않는다).
"""

import re

ARTIFACT_VERSION = "execution-layer-mvp-0004"
STATUS_PENDING = "PENDING"

EXECUTION_HANDLE_HEADER = "# Execution Handle\n\n"

_REQUEST_ID_LINE_PATTERN = re.compile(r"^- request_id: (?P<value>.+)$", re.MULTILINE)


def _extract_request_id(model_request: str) -> str:
    """Model Request의 `## Metadata` 절에 이미 기록된 `request_id` 값을
    그대로 읽는다. 새 값을 만들지 않는다 — 단순 텍스트 추출이다.
    """
    match = _REQUEST_ID_LINE_PATTERN.search(model_request)
    if not match:
        raise ValueError("model_request에서 request_id를 찾을 수 없다")
    return match.group("value")


def build_execution_handle(model_request: str, *, handle_id: str, submitted_at: str) -> str:
    """Model Request를 Execution Handle로 변환한다.

    Model Request의 텍스트를 한 글자도 바꾸지 않고, 그 앞에 실행 상태
    메타데이터 절(``## Handle``)만 추가한다. ``handle_id``와
    ``submitted_at``은 호출자가 제공해야 한다(이 함수는 둘 다 생성하지
    않는다). ``request_id``는 Model Request에서 그대로 읽어온다.
    ``status``는 항상 ``"PENDING"``, ``artifact_version``은 항상 모듈
    상수다 — 둘 다 입력에 따라 달라지지 않는다.
    """
    request_id = _extract_request_id(model_request)

    handle_lines = "\n".join(
        [
            f"- handle_id: {handle_id}",
            f"- request_id: {request_id}",
            f"- status: {STATUS_PENDING}",
            f"- submitted_at: {submitted_at}",
            f"- artifact_version: {ARTIFACT_VERSION}",
        ]
    )

    return (
        f"{EXECUTION_HANDLE_HEADER}"
        f"## Handle\n{handle_lines}\n\n"
        f"## Model Request\n{model_request}"
    )

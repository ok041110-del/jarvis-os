"""Execution Layer MVP-0004: ExecutionHandleBuilder.

Model Request를 Execution Handle로 변환한다. Model Request는 수정하지
않고 실행 상태 메타데이터만 추가한다(handle_id, request_id, status,
submitted_at, artifact_version). status는 `"PENDING"` 고정값만 다룬다.

`handle_id`/`submitted_at`은 Session/Runtime 책임 영역이므로 호출자가
주입한다. `request_id`는 새로 받지 않고 Model Request의 `## Metadata`
절에서 그대로 읽어 재사용한다(Canonical 참조 유지, 값 불일치 방지).
"""

import re

ARTIFACT_VERSION = "execution-layer-mvp-0004"
STATUS_PENDING = "PENDING"

EXECUTION_HANDLE_HEADER = "# Execution Handle\n\n"

_REQUEST_ID_LINE_PATTERN = re.compile(r"^- request_id: (?P<value>.+)$", re.MULTILINE)


def _extract_request_id(model_request: str) -> str:
    """Model Request의 `## Metadata` 절에서 `request_id` 값을 그대로 읽는다."""
    match = _REQUEST_ID_LINE_PATTERN.search(model_request)
    if not match:
        raise ValueError("model_request에서 request_id를 찾을 수 없다")
    return match.group("value")


def build_execution_handle(model_request: str, *, handle_id: str, submitted_at: str) -> str:
    """Model Request를 Execution Handle로 변환한다.

    텍스트는 그대로 두고 앞에 상태 메타데이터 절(``## Handle``)만
    추가한다. ``handle_id``/``submitted_at``은 호출자가 제공해야 한다.
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

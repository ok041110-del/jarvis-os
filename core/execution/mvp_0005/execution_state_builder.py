"""Execution Layer MVP-0005: ExecutionStateBuilder.

Execution Handle에 대한 Execution State를 만든다. Execution Handle은
수정하지 않고 상태 메타데이터만 추가한다(handle_id, request_id, state,
changed_at, artifact_version). State Machine/Transition 규칙은
다루지 않는다 — `state`가 5개 허용값 중 하나인지만 검증한다.

`handle_id`/`state`/`changed_at`은 Runtime/Scheduler 책임 영역이므로
호출자가 주입한다. `request_id`만 예외로, Execution Handle의
`## Handle` 절에서 그대로 읽어 재사용한다(Canonical 참조 유지).
"""

import re

ARTIFACT_VERSION = "execution-layer-mvp-0005"

ALLOWED_STATES = ("PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED")

EXECUTION_STATE_HEADER = "# Execution State\n\n"

_REQUEST_ID_LINE_PATTERN = re.compile(r"^- request_id: (?P<value>.+)$", re.MULTILINE)


class InvalidExecutionStateError(ValueError):
    """`state`가 `ALLOWED_STATES`에 없을 때 발생한다."""


def _extract_request_id(execution_handle: str) -> str:
    """Execution Handle의 `## Handle` 절에서 `request_id` 값을 그대로 읽는다."""
    match = _REQUEST_ID_LINE_PATTERN.search(execution_handle)
    if not match:
        raise ValueError("execution_handle에서 request_id를 찾을 수 없다")
    return match.group("value")


def build_execution_state(
    execution_handle: str, *, handle_id: str, state: str, changed_at: str
) -> str:
    """Execution Handle에 대한 Execution State를 만든다.

    텍스트는 그대로 두고 앞에 상태 메타데이터 절(``## State``)만 추가한
    새 Artifact를 반환한다. ``state``는 `ALLOWED_STATES` 소속 여부만
    검증한다(전이 규칙 검증 없음).
    """
    if state not in ALLOWED_STATES:
        raise InvalidExecutionStateError(
            f"state={state!r}는 허용된 상태가 아니다. 허용된 상태: {ALLOWED_STATES}"
        )

    request_id = _extract_request_id(execution_handle)

    state_lines = "\n".join(
        [
            f"- handle_id: {handle_id}",
            f"- request_id: {request_id}",
            f"- state: {state}",
            f"- changed_at: {changed_at}",
            f"- artifact_version: {ARTIFACT_VERSION}",
        ]
    )

    return (
        f"{EXECUTION_STATE_HEADER}"
        f"## State\n{state_lines}\n\n"
        f"## Execution Handle\n{execution_handle}"
    )

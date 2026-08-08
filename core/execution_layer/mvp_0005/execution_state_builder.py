"""Execution Layer MVP-0005: ExecutionStateBuilder.

Execution Handle(Execution Layer MVP-0004의 Artifact)에 대한 Execution
State(Execution Layer의 다섯 번째 공식 Artifact)를 만든다.

Contract (요청 원문 기준):
- Input: Execution Handle (`str`, MVP-0004 `build_execution_handle()`이
  생성하는 형태).
- Output: Execution State (`str`) — Execution Handle을 그대로 참조하는
  독립 Artifact. Execution Handle 자체는 수정하지 않는다(새 Artifact를
  생성할 뿐).
- Execution State에는 상태 정보만 추가된다(handle_id, request_id, state,
  changed_at, artifact_version).
- 이번 MVP는 State Machine이나 Runtime을 구현하지 않는다. State
  Transition(어떤 상태에서 어떤 상태로 옮겨갈 수 있는가)도 다루지 않는다
  — ExecutionStateBuilder는 호출자가 전달한 `state` 값이 5개 허용된
  이름(PENDING/RUNNING/COMPLETED/FAILED/CANCELLED) 중 하나인지만
  검증한다. 상태를 스스로 바꾸거나 결정하지 않는다.
- AI/LLM/Model 호출 없음. Runtime/Scheduler/Retry 없음. 시스템 시계
  접근 없음. State 생성(자동 전이·자동 결정) 없음.

## handle_id / state / changed_at을 이 모듈이 생성하지 않는 이유

MVP-0003(request_id/created_at), MVP-0004(handle_id/submitted_at)와
같은 이유다: 실행 상태가 "언제, 무엇으로" 바뀌었는지를 판단·기록하는
행위는 Runtime/Scheduler의 책임 영역과 겹친다. 그래서
`build_execution_state()`는 `handle_id`, `state`, `changed_at` 셋 다
호출자가 전달한 값을 그대로 사용하며, 내부에서 시계를 읽거나 상태를
스스로 결정하지 않는다. `request_id`만 예외다 — 이 값은 Execution
Handle의 `## Handle` 절에 이미 있으므로, MVP-0004가 Model Request에서
request_id를 재사용했던 것과 동일하게 그대로 읽어서 재사용한다(Execution
Handle을 Canonical 참조로 유지하기 위함).
"""

import re

ARTIFACT_VERSION = "execution-layer-mvp-0005"

ALLOWED_STATES = ("PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED")

EXECUTION_STATE_HEADER = "# Execution State\n\n"

_REQUEST_ID_LINE_PATTERN = re.compile(r"^- request_id: (?P<value>.+)$", re.MULTILINE)


class InvalidExecutionStateError(ValueError):
    """`state`가 `ALLOWED_STATES`에 없을 때 발생한다."""


def _extract_request_id(execution_handle: str) -> str:
    """Execution Handle의 `## Handle` 절에 이미 기록된 `request_id` 값을
    그대로 읽는다. 새 값을 만들지 않는다 — 단순 텍스트 추출이다.
    """
    match = _REQUEST_ID_LINE_PATTERN.search(execution_handle)
    if not match:
        raise ValueError("execution_handle에서 request_id를 찾을 수 없다")
    return match.group("value")


def build_execution_state(
    execution_handle: str, *, handle_id: str, state: str, changed_at: str
) -> str:
    """Execution Handle에 대한 Execution State를 만든다.

    Execution Handle의 텍스트를 한 글자도 바꾸지 않고, 그 앞에 상태
    메타데이터 절(``## State``)만 추가한 새 Artifact를 반환한다.
    ``handle_id``, ``state``, ``changed_at``은 호출자가 제공해야 한다
    (이 함수는 셋 다 생성하지 않는다). ``state``는 `ALLOWED_STATES`에
    속하는지만 검증한다 — 상태 전이 규칙(어떤 상태에서 어떤 상태로 갈 수
    있는지)은 검증하지 않는다. ``request_id``는 Execution Handle에서
    그대로 읽어온다. ``artifact_version``은 항상 모듈 상수다.
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

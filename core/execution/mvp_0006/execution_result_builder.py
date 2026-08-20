"""Execution Layer MVP-0006: ExecutionResultBuilder.

Execution State에 대한 Execution Result를 만든다. Execution State는
수정하지 않고 산출물 목록(``results``, `list[str]`)과 식별 메타데이터만
추가한다(handle_id, request_id, produced_at, artifact_version).
``results``의 각 항목은 opaque 문자열로만 다루며 해석하지 않는다 —
개수(빈 목록 포함) 검증도 하지 않는다(`ADC-0003-execution-result-item-schema.md`
Decision).

`handle_id`/`produced_at`/`results`는 Runtime/Scheduler/Engine 책임
영역이므로 호출자가 주입한다. `request_id`만 예외로, Execution State의
`## State` 절에서 그대로 읽어 재사용한다(Canonical 참조 유지).
"""

import re

ARTIFACT_VERSION = "execution-layer-mvp-0006"

EXECUTION_RESULT_HEADER = "# Execution Result\n\n"

_REQUEST_ID_LINE_PATTERN = re.compile(r"^- request_id: (?P<value>.+)$", re.MULTILINE)


def _extract_request_id(execution_state: str) -> str:
    """Execution State의 `## State` 절에서 `request_id` 값을 그대로 읽는다."""
    match = _REQUEST_ID_LINE_PATTERN.search(execution_state)
    if not match:
        raise ValueError("execution_state에서 request_id를 찾을 수 없다")
    return match.group("value")


def build_execution_result(
    execution_state: str,
    *,
    handle_id: str,
    produced_at: str,
    results: list[str],
) -> str:
    """Execution State에 대한 Execution Result를 만든다.

    텍스트는 그대로 두고 앞에 결과 메타데이터 절(``## Result``)과
    산출물 목록 절(``## Results``)만 추가한 새 Artifact를 반환한다.
    """
    request_id = _extract_request_id(execution_state)

    result_lines = "\n".join(
        [
            f"- handle_id: {handle_id}",
            f"- request_id: {request_id}",
            f"- produced_at: {produced_at}",
            f"- artifact_version: {ARTIFACT_VERSION}",
        ]
    )

    results_lines = "\n".join(f"- {item}" for item in results)

    return (
        f"{EXECUTION_RESULT_HEADER}"
        f"## Result\n{result_lines}\n\n"
        f"## Results\n{results_lines}\n\n"
        f"## Execution State\n{execution_state}"
    )

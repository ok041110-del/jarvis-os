"""Execution Layer MVP-0006: ExecutionResultBuilder.

Execution State에 대한 Execution Result를 만든다 — `results`(list[str])는 opaque 문자열로만 다루고 개수 검증도 하지 않는다(`ADC-0003-execution-result-item-schema.md`). `handle_id`/`produced_at`/`results`는 호출자가 주입하고, `request_id`만 Execution State의 `## State` 절에서 그대로 읽어 재사용한다.
"""

import re

ARTIFACT_VERSION = "execution-layer-mvp-0006"

EXECUTION_RESULT_HEADER = "# Execution Result\n\n"

_REQUEST_ID_LINE_PATTERN = re.compile(r"^- request_id: (?P<value>.+)$", re.MULTILINE)


def _extract_request_id(execution_state: str) -> str:
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

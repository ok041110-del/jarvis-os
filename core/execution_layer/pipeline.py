"""Execution Layer Pipeline — 6개 Builder(MVP-0001~0006)를 하나의 함수로 묶는다.

Task 순서는 함수 본문에 하드코딩된다(설정/파서/조건문 없음) —
Runtime/Scheduler가 아니다. 상태를 보관하지 않고 호출마다 독립
실행되며, 시스템 시계·난수를 쓰지 않는다(`development-hq/IMPLEMENTATION_RULES.md`).
"""

import hashlib
import re

from execution_layer.mvp_0001.execution_request_builder import (
    build_execution_request,
)
from execution_layer.mvp_0002.prompt_specification_builder import (
    build_prompt_specification,
)
from execution_layer.mvp_0003.model_request_builder import build_model_request
from execution_layer.mvp_0004.execution_handle_builder import (
    build_execution_handle,
)
from execution_layer.mvp_0005.execution_state_builder import build_execution_state
from execution_layer.mvp_0006.execution_result_builder import (
    build_execution_result,
)

_HANDLE_ID_LINE_PATTERN = re.compile(r"^- handle_id: (?P<value>.+)$", re.MULTILINE)


def _derive_id(content: str) -> str:
    """내용 기반 결정론적 ID(SHA-256 해시 앞 16자). 무작위 발급이 아니다."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _extract_handle_id(execution_handle: str) -> str:
    match = _HANDLE_ID_LINE_PATTERN.search(execution_handle)
    if not match:
        raise ValueError("execution_handle에서 handle_id를 찾을 수 없다")
    return match.group("value")


def run_execution_layer_pipeline(
    implementation_specification: str,
    *,
    created_at: str,
    submitted_at: str,
    state: str,
    changed_at: str,
    produced_at: str,
    results: list[str],
) -> str:
    """Implementation Specification에서 Execution Result까지 6개 Builder를
    순서대로 호출한다. `request_id`/`handle_id`는 이 함수가 결정론적으로
    유도하고, 그 외 caller-supplied 값은 해석·검증 없이 그대로 전달한다
    (각 Builder 자신의 검증만 적용된다). 중간 Artifact는 반환하지 않는다.
    """
    execution_request = build_execution_request(implementation_specification)
    prompt_specification = build_prompt_specification(execution_request)

    request_id = _derive_id(prompt_specification)
    model_request = build_model_request(
        prompt_specification, request_id=request_id, created_at=created_at
    )

    handle_id = _derive_id(model_request)
    execution_handle = build_execution_handle(
        model_request, handle_id=handle_id, submitted_at=submitted_at
    )

    handle_id_from_handle = _extract_handle_id(execution_handle)
    execution_state = build_execution_state(
        execution_handle,
        handle_id=handle_id_from_handle,
        state=state,
        changed_at=changed_at,
    )

    return build_execution_result(
        execution_state,
        handle_id=handle_id_from_handle,
        produced_at=produced_at,
        results=results,
    )

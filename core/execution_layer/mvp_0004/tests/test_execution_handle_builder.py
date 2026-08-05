"""Execution Layer MVP-0004 Exit Criteria 검증.

Success Criteria(요청 원문):
- Model Request 100% 보존.
- Execution Handle 메타데이터만 추가.
- status=PENDING.
- 동일 입력 -> 동일 Handle (Deterministic Transformation).
- AI 호출 없음.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from execution_layer.mvp_0001.execution_request_builder import (  # noqa: E402
    build_execution_request,
)
from execution_layer.mvp_0002.prompt_specification_builder import (  # noqa: E402
    build_prompt_specification,
)
from execution_layer.mvp_0003.model_request_builder import (  # noqa: E402
    build_model_request,
)
from execution_layer.mvp_0004.execution_handle_builder import (  # noqa: E402
    ARTIFACT_VERSION,
    STATUS_PENDING,
    build_execution_handle,
)

SAMPLE_IMPLEMENTATION_SPECIFICATION = (
    "## Target File\n"
    "development-hq/mvp/generated/reverse_string.py\n\n"
    "## Public Interface\n"
    "`def reverse_string(*args, **kwargs)`\n\n"
    "## Functions\n"
    "- `def reverse_string(*args, **kwargs)` (Public Interface): 문자열을 뒤집는다\n\n"
    "## Classes\n"
    "- (필요 없음: Design이 단일 함수형 Component만 제안했다)\n\n"
    "## Dependencies\n"
    "- (Reference Context에서 식별된 의존 대상 없음)\n\n"
    "## Algorithm Outline\n"
    "1. 입력 문자열을 받는다\n"
    "2. 문자열을 뒤집는다\n\n"
    "## Edge Cases\n"
    "- (Constraints에서 식별된 Edge Case 없음)\n\n"
    "## Validation Notes\n"
    "- (Open Questions 없음)\n\n"
    "## Reference Design\n"
    "## Component\n문자열을 뒤집는 함수\n"
)

SAMPLE_EXECUTION_REQUEST = build_execution_request(SAMPLE_IMPLEMENTATION_SPECIFICATION)
SAMPLE_PROMPT_SPECIFICATION = build_prompt_specification(SAMPLE_EXECUTION_REQUEST)
SAMPLE_MODEL_REQUEST = build_model_request(
    SAMPLE_PROMPT_SPECIFICATION,
    request_id="test-request-id-0001",
    created_at="unresolved",
)

SAMPLE_HANDLE_ID = "test-handle-id-0001"
SAMPLE_SUBMITTED_AT = "unresolved"


def test_model_request_preserved_verbatim():
    handle = build_execution_handle(
        SAMPLE_MODEL_REQUEST,
        handle_id=SAMPLE_HANDLE_ID,
        submitted_at=SAMPLE_SUBMITTED_AT,
    )

    assert SAMPLE_MODEL_REQUEST in handle


def test_only_handle_metadata_is_added_no_other_change():
    handle = build_execution_handle(
        SAMPLE_MODEL_REQUEST,
        handle_id=SAMPLE_HANDLE_ID,
        submitted_at=SAMPLE_SUBMITTED_AT,
    )

    expected_metadata = (
        "# Execution Handle\n\n"
        "## Handle\n"
        f"- handle_id: {SAMPLE_HANDLE_ID}\n"
        "- request_id: test-request-id-0001\n"
        f"- status: {STATUS_PENDING}\n"
        f"- submitted_at: {SAMPLE_SUBMITTED_AT}\n"
        f"- artifact_version: {ARTIFACT_VERSION}\n\n"
        "## Model Request\n"
    )

    assert handle == expected_metadata + SAMPLE_MODEL_REQUEST


def test_status_is_always_pending():
    handle = build_execution_handle(
        SAMPLE_MODEL_REQUEST,
        handle_id=SAMPLE_HANDLE_ID,
        submitted_at=SAMPLE_SUBMITTED_AT,
    )

    assert "- status: PENDING" in handle
    for forbidden in ("RUNNING", "COMPLETED", "FAILED", "CANCELLED"):
        assert forbidden not in handle


def test_request_id_is_read_from_model_request_not_reinjected():
    handle = build_execution_handle(
        SAMPLE_MODEL_REQUEST,
        handle_id=SAMPLE_HANDLE_ID,
        submitted_at=SAMPLE_SUBMITTED_AT,
    )

    assert "- request_id: test-request-id-0001" in handle


def test_transformation_is_deterministic():
    first = build_execution_handle(
        SAMPLE_MODEL_REQUEST,
        handle_id=SAMPLE_HANDLE_ID,
        submitted_at=SAMPLE_SUBMITTED_AT,
    )
    second = build_execution_handle(
        SAMPLE_MODEL_REQUEST,
        handle_id=SAMPLE_HANDLE_ID,
        submitted_at=SAMPLE_SUBMITTED_AT,
    )

    assert first == second


def test_model_request_itself_is_unchanged_by_wrapping():
    before = SAMPLE_MODEL_REQUEST
    build_execution_handle(
        SAMPLE_MODEL_REQUEST,
        handle_id=SAMPLE_HANDLE_ID,
        submitted_at=SAMPLE_SUBMITTED_AT,
    )

    assert SAMPLE_MODEL_REQUEST == before


def test_no_ai_or_model_call_symbols_present_in_module():
    import inspect

    from execution_layer.mvp_0004 import execution_handle_builder

    source = inspect.getsource(execution_handle_builder)

    for forbidden in (
        "call_engine",
        "requests.",
        "openai",
        "anthropic",
        "subprocess",
        "urllib",
        "http.client",
        "datetime.now",
        "uuid.uuid4",
        "time.time",
    ):
        assert forbidden not in source

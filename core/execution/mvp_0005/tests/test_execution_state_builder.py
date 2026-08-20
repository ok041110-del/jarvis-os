"""Execution Layer MVP-0005 Exit Criteria 검증."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from execution.mvp_0001.execution_request_builder import (  # noqa: E402
    build_execution_request,
)
from execution.mvp_0002.prompt_specification_builder import (  # noqa: E402
    build_prompt_specification,
)
from execution.mvp_0003.model_request_builder import (  # noqa: E402
    build_model_request,
)
from execution.mvp_0004.execution_handle_builder import (  # noqa: E402
    build_execution_handle,
)
from execution.mvp_0005.execution_state_builder import (  # noqa: E402
    ALLOWED_STATES,
    ARTIFACT_VERSION,
    InvalidExecutionStateError,
    build_execution_state,
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
SAMPLE_EXECUTION_HANDLE = build_execution_handle(
    SAMPLE_MODEL_REQUEST,
    handle_id="test-handle-id-0001",
    submitted_at="unresolved",
)

SAMPLE_STATE = "PENDING"
SAMPLE_CHANGED_AT = "unresolved"


def test_execution_handle_preserved_verbatim():
    execution_state = build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state=SAMPLE_STATE,
        changed_at=SAMPLE_CHANGED_AT,
    )

    assert SAMPLE_EXECUTION_HANDLE in execution_state


def test_only_state_metadata_is_added_no_other_change():
    execution_state = build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state=SAMPLE_STATE,
        changed_at=SAMPLE_CHANGED_AT,
    )

    expected_metadata = (
        "# Execution State\n\n"
        "## State\n"
        "- handle_id: test-handle-id-0001\n"
        "- request_id: test-request-id-0001\n"
        f"- state: {SAMPLE_STATE}\n"
        f"- changed_at: {SAMPLE_CHANGED_AT}\n"
        f"- artifact_version: {ARTIFACT_VERSION}\n\n"
        "## Execution Handle\n"
    )

    assert execution_state == expected_metadata + SAMPLE_EXECUTION_HANDLE


def test_request_id_is_read_from_execution_handle_not_reinjected():
    execution_state = build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state=SAMPLE_STATE,
        changed_at=SAMPLE_CHANGED_AT,
    )

    assert "- request_id: test-request-id-0001" in execution_state


@pytest.mark.parametrize("state", ALLOWED_STATES)
def test_all_five_allowed_states_are_accepted(state):
    execution_state = build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state=state,
        changed_at=SAMPLE_CHANGED_AT,
    )

    assert f"- state: {state}" in execution_state


def test_unknown_state_is_rejected():
    with pytest.raises(InvalidExecutionStateError):
        build_execution_state(
            SAMPLE_EXECUTION_HANDLE,
            handle_id="test-handle-id-0001",
            state="UNKNOWN_STATE",
            changed_at=SAMPLE_CHANGED_AT,
        )


def test_state_validation_does_not_check_transition_rules():
    build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state="COMPLETED",
        changed_at=SAMPLE_CHANGED_AT,
    )
    second = build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state="PENDING",
        changed_at=SAMPLE_CHANGED_AT,
    )

    assert "- state: PENDING" in second


def test_transformation_is_deterministic():
    first = build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state=SAMPLE_STATE,
        changed_at=SAMPLE_CHANGED_AT,
    )
    second = build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state=SAMPLE_STATE,
        changed_at=SAMPLE_CHANGED_AT,
    )

    assert first == second


def test_execution_handle_itself_is_unchanged_by_state_creation():
    before = SAMPLE_EXECUTION_HANDLE
    build_execution_state(
        SAMPLE_EXECUTION_HANDLE,
        handle_id="test-handle-id-0001",
        state=SAMPLE_STATE,
        changed_at=SAMPLE_CHANGED_AT,
    )

    assert SAMPLE_EXECUTION_HANDLE == before


def test_no_ai_or_runtime_symbols_present_in_module():
    import inspect

    from execution.mvp_0005 import execution_state_builder

    source = inspect.getsource(execution_state_builder)

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

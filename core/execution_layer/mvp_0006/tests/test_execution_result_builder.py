"""Execution Layer MVP-0006 Exit Criteria 검증(RFC-0002/ADC-0002/ADR-0001, RFC-0003/ADC-0003/ADR-0002)."""

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
    build_execution_handle,
)
from execution_layer.mvp_0005.execution_state_builder import (  # noqa: E402
    build_execution_state,
)
from execution_layer.mvp_0006.execution_result_builder import (  # noqa: E402
    ARTIFACT_VERSION,
    build_execution_result,
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
SAMPLE_EXECUTION_STATE = build_execution_state(
    SAMPLE_EXECUTION_HANDLE,
    handle_id="test-handle-id-0001",
    state="COMPLETED",
    changed_at="unresolved",
)

SAMPLE_PRODUCED_AT = "unresolved"
SAMPLE_RESULTS = ["diff: reverse_string.py 생성됨", "test log: 3 passed"]


def test_execution_state_preserved_verbatim():
    execution_result = build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=SAMPLE_RESULTS,
    )

    assert SAMPLE_EXECUTION_STATE in execution_result


def test_only_result_metadata_and_results_are_added_no_other_change():
    execution_result = build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=SAMPLE_RESULTS,
    )

    expected_prefix = (
        "# Execution Result\n\n"
        "## Result\n"
        "- handle_id: test-handle-id-0001\n"
        "- request_id: test-request-id-0001\n"
        f"- produced_at: {SAMPLE_PRODUCED_AT}\n"
        f"- artifact_version: {ARTIFACT_VERSION}\n\n"
        "## Results\n"
        f"- {SAMPLE_RESULTS[0]}\n"
        f"- {SAMPLE_RESULTS[1]}\n\n"
        "## Execution State\n"
    )

    assert execution_result == expected_prefix + SAMPLE_EXECUTION_STATE


def test_request_id_is_read_from_execution_state_not_reinjected():
    execution_result = build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=SAMPLE_RESULTS,
    )

    assert "- request_id: test-request-id-0001" in execution_result


def test_results_items_are_embedded_verbatim_and_unopened():
    execution_result = build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=SAMPLE_RESULTS,
    )

    for item in SAMPLE_RESULTS:
        assert f"- {item}" in execution_result


def test_empty_results_list_is_accepted():
    execution_result = build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=[],
    )

    assert "## Results\n\n" in execution_result


def test_single_item_results_list_is_accepted():
    execution_result = build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=["only one item"],
    )

    assert "- only one item" in execution_result


def test_transformation_is_deterministic():
    first = build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=SAMPLE_RESULTS,
    )
    second = build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=SAMPLE_RESULTS,
    )

    assert first == second


def test_execution_state_itself_is_unchanged_by_result_creation():
    before = SAMPLE_EXECUTION_STATE
    build_execution_result(
        SAMPLE_EXECUTION_STATE,
        handle_id="test-handle-id-0001",
        produced_at=SAMPLE_PRODUCED_AT,
        results=SAMPLE_RESULTS,
    )

    assert SAMPLE_EXECUTION_STATE == before


def test_no_ai_or_runtime_symbols_present_in_module():
    import inspect

    from execution_layer.mvp_0006 import execution_result_builder

    source = inspect.getsource(execution_result_builder)

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

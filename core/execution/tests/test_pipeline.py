"""Execution Layer Pipeline 검증."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

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
    InvalidExecutionStateError,
    build_execution_state,
)
from execution.mvp_0006.execution_result_builder import (  # noqa: E402
    build_execution_result,
)
from execution.pipeline import (  # noqa: E402
    _derive_id,
    _extract_handle_id,
    run_execution_layer_pipeline,
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

SAMPLE_KWARGS = dict(
    created_at="unresolved",
    submitted_at="unresolved",
    state="COMPLETED",
    changed_at="unresolved",
    produced_at="unresolved",
    results=["diff: reverse_string.py 생성됨", "test log: 3 passed"],
)


def _manual_chain(implementation_specification: str, **kwargs) -> str:
    """6개 Builder를 개별 호출한 결과 — Pipeline과 대조할 기준값."""
    execution_request = build_execution_request(implementation_specification)
    prompt_specification = build_prompt_specification(execution_request)
    request_id = _derive_id(prompt_specification)
    model_request = build_model_request(
        prompt_specification, request_id=request_id, created_at=kwargs["created_at"]
    )
    handle_id = _derive_id(model_request)
    execution_handle = build_execution_handle(
        model_request, handle_id=handle_id, submitted_at=kwargs["submitted_at"]
    )
    handle_id_from_handle = _extract_handle_id(execution_handle)
    execution_state = build_execution_state(
        execution_handle,
        handle_id=handle_id_from_handle,
        state=kwargs["state"],
        changed_at=kwargs["changed_at"],
    )
    return build_execution_result(
        execution_state,
        handle_id=handle_id_from_handle,
        produced_at=kwargs["produced_at"],
        results=kwargs["results"],
    )


def test_pipeline_output_matches_manual_builder_chain_exactly():
    pipeline_result = run_execution_layer_pipeline(
        SAMPLE_IMPLEMENTATION_SPECIFICATION, **SAMPLE_KWARGS
    )
    manual_result = _manual_chain(SAMPLE_IMPLEMENTATION_SPECIFICATION, **SAMPLE_KWARGS)

    assert pipeline_result == manual_result


def test_execution_request_preserved_verbatim_through_full_chain():
    execution_request = build_execution_request(SAMPLE_IMPLEMENTATION_SPECIFICATION)
    execution_result = run_execution_layer_pipeline(
        SAMPLE_IMPLEMENTATION_SPECIFICATION, **SAMPLE_KWARGS
    )

    assert SAMPLE_IMPLEMENTATION_SPECIFICATION in execution_request
    assert "reverse_string" in execution_result
    assert "문자열을 뒤집는다" in execution_result


def test_results_items_preserved_verbatim_in_final_output():
    execution_result = run_execution_layer_pipeline(
        SAMPLE_IMPLEMENTATION_SPECIFICATION, **SAMPLE_KWARGS
    )

    for item in SAMPLE_KWARGS["results"]:
        assert f"- {item}" in execution_result


def test_transformation_is_deterministic():
    first = run_execution_layer_pipeline(
        SAMPLE_IMPLEMENTATION_SPECIFICATION, **SAMPLE_KWARGS
    )
    second = run_execution_layer_pipeline(
        SAMPLE_IMPLEMENTATION_SPECIFICATION, **SAMPLE_KWARGS
    )

    assert first == second


def test_invalid_state_is_rejected_by_underlying_builder():
    kwargs = dict(SAMPLE_KWARGS)
    kwargs["state"] = "UNKNOWN_STATE"

    with pytest.raises(InvalidExecutionStateError):
        run_execution_layer_pipeline(SAMPLE_IMPLEMENTATION_SPECIFICATION, **kwargs)


def test_empty_results_list_is_accepted_by_underlying_builder():
    kwargs = dict(SAMPLE_KWARGS)
    kwargs["results"] = []

    execution_result = run_execution_layer_pipeline(
        SAMPLE_IMPLEMENTATION_SPECIFICATION, **kwargs
    )

    assert "## Results\n\n" in execution_result


def test_no_ai_or_runtime_symbols_present_in_module():
    import inspect

    from execution import pipeline

    source = inspect.getsource(pipeline)

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

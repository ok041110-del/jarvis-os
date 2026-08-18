"""Execution Layer MVP-0003 Exit Criteria 검증."""

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
    ARTIFACT_VERSION,
    TARGET_ENGINE_PLACEHOLDER,
    build_model_request,
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

SAMPLE_REQUEST_ID = "test-request-id-0001"
SAMPLE_CREATED_AT = "unresolved"


def test_prompt_specification_preserved_verbatim():
    model_request = build_model_request(
        SAMPLE_PROMPT_SPECIFICATION,
        request_id=SAMPLE_REQUEST_ID,
        created_at=SAMPLE_CREATED_AT,
    )

    assert SAMPLE_PROMPT_SPECIFICATION in model_request


def test_only_metadata_is_added_no_other_change():
    model_request = build_model_request(
        SAMPLE_PROMPT_SPECIFICATION,
        request_id=SAMPLE_REQUEST_ID,
        created_at=SAMPLE_CREATED_AT,
    )

    expected_metadata = (
        "# Model Request\n\n"
        "## Metadata\n"
        f"- request_id: {SAMPLE_REQUEST_ID}\n"
        f"- artifact_version: {ARTIFACT_VERSION}\n"
        f"- created_at: {SAMPLE_CREATED_AT}\n"
        f"- target_engine: {TARGET_ENGINE_PLACEHOLDER}\n\n"
        "## Prompt Specification\n"
    )

    assert model_request == expected_metadata + SAMPLE_PROMPT_SPECIFICATION


def test_transformation_is_deterministic():
    first = build_model_request(
        SAMPLE_PROMPT_SPECIFICATION,
        request_id=SAMPLE_REQUEST_ID,
        created_at=SAMPLE_CREATED_AT,
    )
    second = build_model_request(
        SAMPLE_PROMPT_SPECIFICATION,
        request_id=SAMPLE_REQUEST_ID,
        created_at=SAMPLE_CREATED_AT,
    )

    assert first == second


def test_target_engine_is_a_placeholder_not_a_real_model_name():
    model_request = build_model_request(
        SAMPLE_PROMPT_SPECIFICATION,
        request_id=SAMPLE_REQUEST_ID,
        created_at=SAMPLE_CREATED_AT,
    )

    assert f"target_engine: {TARGET_ENGINE_PLACEHOLDER}" in model_request

    forbidden_model_names = (
        "claude",
        "gpt",
        "codex",
        "qwen",
        "openai",
        "anthropic",
    )
    metadata_section = model_request.split("## Prompt Specification", 1)[0]
    lowered = metadata_section.lower()
    for name in forbidden_model_names:
        assert name not in lowered, f"metadata section unexpectedly mentions {name!r}"


def test_prompt_specification_itself_is_unchanged_by_wrapping():
    before = SAMPLE_PROMPT_SPECIFICATION
    build_model_request(
        SAMPLE_PROMPT_SPECIFICATION,
        request_id=SAMPLE_REQUEST_ID,
        created_at=SAMPLE_CREATED_AT,
    )

    assert SAMPLE_PROMPT_SPECIFICATION == before


def test_no_ai_or_model_call_symbols_present_in_module():
    import inspect

    from execution_layer.mvp_0003 import model_request_builder

    source = inspect.getsource(model_request_builder)

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
    ):
        assert forbidden not in source

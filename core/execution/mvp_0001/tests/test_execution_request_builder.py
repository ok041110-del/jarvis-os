"""Execution Layer MVP-0001 Exit Criteria 검증. See docs/core/execution-layer/MVP-0001-plan.md"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from execution.mvp_0001.execution_request_builder import (
    KNOWN_SECTIONS,
    build_execution_request,
    find_known_sections,
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


def test_execution_request_preserves_input_verbatim():
    request = build_execution_request(SAMPLE_IMPLEMENTATION_SPECIFICATION)

    assert SAMPLE_IMPLEMENTATION_SPECIFICATION in request


def test_execution_request_adds_only_a_header_no_other_change():
    request = build_execution_request(SAMPLE_IMPLEMENTATION_SPECIFICATION)

    assert request == f"# Execution Request\n\n{SAMPLE_IMPLEMENTATION_SPECIFICATION}"


def test_execution_request_is_distinguishable_from_input():
    request = build_execution_request(SAMPLE_IMPLEMENTATION_SPECIFICATION)

    assert request != SAMPLE_IMPLEMENTATION_SPECIFICATION
    assert request.startswith("# Execution Request")


def test_transformation_is_deterministic():
    first = build_execution_request(SAMPLE_IMPLEMENTATION_SPECIFICATION)
    second = build_execution_request(SAMPLE_IMPLEMENTATION_SPECIFICATION)

    assert first == second


def test_all_eight_known_sections_survive_transformation():
    request = build_execution_request(SAMPLE_IMPLEMENTATION_SPECIFICATION)

    before = find_known_sections(SAMPLE_IMPLEMENTATION_SPECIFICATION)
    after = find_known_sections(request)

    assert len(KNOWN_SECTIONS) == 8
    assert before == after
    assert all(after.values())


def test_no_ai_or_model_call_symbols_present_in_module():
    import inspect

    from execution.mvp_0001 import execution_request_builder

    source = inspect.getsource(execution_request_builder)

    for forbidden in ("call_engine", "requests.", "openai", "anthropic", "subprocess"):
        assert forbidden not in source

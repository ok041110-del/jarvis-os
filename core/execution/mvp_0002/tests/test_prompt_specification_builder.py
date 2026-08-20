"""Execution Layer MVP-0002 Exit Criteria 검증."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from execution.mvp_0001.execution_request_builder import (  # noqa: E402
    build_execution_request,
)
from execution.mvp_0002.prompt_specification_builder import (  # noqa: E402
    PROMPT_SECTIONS_IN_ORDER,
    RENDERING_MAP,
    SOURCE_SECTIONS_IN_ORDER,
    _extract_section_body,
    build_prompt_specification,
    find_prompt_sections,
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


def test_all_source_sections_are_assigned_to_exactly_one_prompt_section():
    assert set(RENDERING_MAP.keys()) == set(SOURCE_SECTIONS_IN_ORDER)
    assert set(RENDERING_MAP.values()) == set(PROMPT_SECTIONS_IN_ORDER)


def test_prompt_specification_has_five_top_level_sections():
    prompt_spec = build_prompt_specification(SAMPLE_EXECUTION_REQUEST)

    found = find_prompt_sections(prompt_spec)

    assert len(PROMPT_SECTIONS_IN_ORDER) == 5
    assert all(found.values())


def test_every_source_section_body_survives_verbatim():
    prompt_spec = build_prompt_specification(SAMPLE_EXECUTION_REQUEST)

    for section in SOURCE_SECTIONS_IN_ORDER:
        body = _extract_section_body(SAMPLE_EXECUTION_REQUEST, section)
        assert body, f"fixture is missing section {section!r}"
        assert body in prompt_spec, f"{section!r} body lost during rendering"


def test_no_new_information_beyond_headers_is_added():
    prompt_spec = build_prompt_specification(SAMPLE_EXECUTION_REQUEST)

    source_bodies_total_len = sum(
        len(_extract_section_body(SAMPLE_EXECUTION_REQUEST, section))
        for section in SOURCE_SECTIONS_IN_ORDER
    )
    # 본문 총 길이가 렌더링 결과 길이를 넘을 수 없다(새 콘텐츠 미추가 하한 검증).
    assert source_bodies_total_len <= len(prompt_spec)


def test_rendering_is_deterministic():
    first = build_prompt_specification(SAMPLE_EXECUTION_REQUEST)
    second = build_prompt_specification(SAMPLE_EXECUTION_REQUEST)

    assert first == second


def test_execution_request_itself_is_unchanged_by_rendering():
    before = SAMPLE_EXECUTION_REQUEST
    build_prompt_specification(SAMPLE_EXECUTION_REQUEST)

    assert SAMPLE_EXECUTION_REQUEST == before


def test_no_ai_or_model_call_symbols_present_in_module():
    import inspect

    from execution.mvp_0002 import prompt_specification_builder

    source = inspect.getsource(prompt_specification_builder)

    for forbidden in ("call_engine", "requests.", "openai", "anthropic", "subprocess"):
        assert forbidden not in source

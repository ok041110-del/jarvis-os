"""Experiment A/B 공통 입력 — 동일한 Stage 04 Implementation을 모든
실행(Single/Parallel, Review Case A/B/C)에서 재사용한다(사용자 지시).

대상은 이전 세션(`OPENROUTER-STAGE-MODEL-SELECTION-0001.md`)이 이미
Stage 05 실제 검증 기준(structural/design_scope/test_execution)으로
PASS를 확인한 것과 동일한 실제 대상(`backend_agent_code_review`,
`hqs/development/mvp/agents/backend.py`)을 재사용한다 — 이 모듈은
원본 파일을 **읽기만** 한다(쓰지 않음). Implementation은 원본을 읽어
그 자리에서 문자열 치환으로 구성한다 — 하드코딩된 사본을 별도로
관리하지 않아 원본과 드리프트하지 않는다."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

TARGET_RELATIVE_PATH = "hqs/development/mvp/agents/backend.py"
TARGET_FUNCTION_NAME = "backend_agent_code_review"
TESTS_RELATIVE_DIR = "hqs/development/mvp/tests"

# Stage 02가 이미 확정했다고 가정하는 Scope Context(RFC-0039 §1 전제 —
# Fan-out 이전에 이미 준비된 값).
FIXED_SCOPE_CANDIDATES = (TARGET_RELATIVE_PATH,)

_ORIGINAL_DOCSTRING_MARKER = (
    '    """`NO_ISSUES_MARKER`는 `workflow_0002.py`의 분기 판단 신호로 쓰인다 —\n'
    "    실이슈가 없을 때만 응답 끝에 정확히 적도록 지시한다.\"\"\"\n"
)

_VALIDATED_DOCSTRING_AND_GUARD = (
    '    """`code`가 공백 제거 후 비어 있지 않은 문자열인지 검증한 뒤 리뷰한다 —\n'
    '    `NO_ISSUES_MARKER`는 `workflow_0002.py`의 분기 판단 신호로 쓰인다 —\n'
    "    실이슈가 없을 때만 응답 끝에 정확히 적도록 지시한다.\"\"\"\n"
    "    if not isinstance(code, str) or not code.strip():\n"
    '        raise ValueError("code must be a non-empty string.")\n'
)

# Stage 03 Design — 이 Fixture가 흉내 내는 요구사항(입력 검증 추가)에 대한
# 고정 Design 텍스트. 실제 Stage 03 Engine을 호출하지 않는다 — 이전 세션
# (`OPENROUTER-STAGE-MODEL-SELECTION-0001.md` §3.3)이 동일 시나리오로
# 실제 Design Agent를 호출해 검증한 것과 같은 요구사항을 고정 텍스트로 재사용.
FIXED_DESIGN_CONTEXT = (
    "Design: Add input validation to backend_agent_code_review.\n\n"
    "Approach: at the top of the function body, check that `code` is a "
    "non-empty string (after stripping whitespace) and raise `ValueError` "
    "with a clear, non-leaky message before calling the Engine. Keep the "
    "existing review instruction and Engine delegation unchanged otherwise.\n\n"
    "Constraints: must not change the function's external contract "
    "(str -> str), must not add filesystem/network access, must not modify "
    "call_engine_review's signature, must not touch any other function in "
    "this file.\n\n"
    "Risks: overly strict validation could reject valid code containing only "
    "whitespace/comments; the error message must not leak internal details."
)


@dataclass
class Stage04ImplementationFixture:
    original_source: str
    implementation: str
    target_relative_path: str = TARGET_RELATIVE_PATH
    target_function_name: str = TARGET_FUNCTION_NAME
    tests_relative_dir: str = TESTS_RELATIVE_DIR
    scope_candidates: tuple = FIXED_SCOPE_CANDIDATES


def build_fixture(repo_root: Path) -> Stage04ImplementationFixture:
    """원본 파일을 읽고(쓰지 않음), 검증 로직을 추가한 Implementation을
    문자열 치환으로 구성한다. 원본에 마커 문자열이 없으면(파일이 바뀌었다면)
    조용히 넘어가지 않고 즉시 실패한다(Evidence 왜곡 방지)."""
    target_path = Path(repo_root) / TARGET_RELATIVE_PATH
    original = target_path.read_text(encoding="utf-8")
    if _ORIGINAL_DOCSTRING_MARKER not in original:
        raise RuntimeError(
            f"{TARGET_RELATIVE_PATH}의 예상 원본 마커를 찾지 못했다 — "
            "Production 파일이 바뀌었을 수 있다(고정 fixture 재검토 필요)"
        )
    implementation = original.replace(_ORIGINAL_DOCSTRING_MARKER, _VALIDATED_DOCSTRING_AND_GUARD, 1)
    return Stage04ImplementationFixture(original_source=original, implementation=implementation)


def build_validation_context(fixture: Stage04ImplementationFixture):
    """`Stage04ImplementationFixture` -> `ValidationContext`(Structure/Scope/
    AST/Dependency가 공유하는 불변 Context, RFC-0039 §5 수정 1)."""
    from .validators import ValidationContext, _import_lines  # noqa: E402 - 순환 참조 방지용 지연 import

    return ValidationContext(
        target_relative_path=fixture.target_relative_path,
        target_function_name=fixture.target_function_name,
        implementation=fixture.implementation,
        original_source_snapshot=fixture.original_source,
        scope_candidates=fixture.scope_candidates,
        original_import_lines=_import_lines(fixture.original_source),
        design_context=FIXED_DESIGN_CONTEXT,
    )

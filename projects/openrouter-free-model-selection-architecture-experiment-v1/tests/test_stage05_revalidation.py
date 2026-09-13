"""Stage 05 Actual Implementation Revalidation 전용 offline 테스트.
네트워크 호출 없이 검증 가능한 것만 확인한다."""

from __future__ import annotations

import sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))

from domain.stage05_actual_implementation_fixture import (  # noqa: E402
    ACTUAL_STAGE04_IMPLEMENTATION,
    ACTUAL_STAGE04_IMPLEMENTATION_PROVENANCE,
    ACTUAL_STAGE04_TARGET_FUNCTION,
)
from domain.stage05_deterministic_comparison import run_deterministic_comparison  # noqa: E402
from run_stage05_revalidation import _build_review_prompt_with_actual_implementation, _classify_error_detail  # noqa: E402


# ---- 1. 실제 Implementation 고정성(placeholder 아님) 확인 --------------------


def test_actual_implementation_is_not_placeholder():
    assert "same implementation validated in the Stage 04 run" not in ACTUAL_STAGE04_IMPLEMENTATION
    assert ACTUAL_STAGE04_IMPLEMENTATION.strip()
    assert len(ACTUAL_STAGE04_IMPLEMENTATION) > 1000  # placeholder 문자열보다 훨씬 김(placeholder는 40여 자)


def test_actual_implementation_contains_target_function():
    assert f"def {ACTUAL_STAGE04_TARGET_FUNCTION}" in ACTUAL_STAGE04_IMPLEMENTATION


def test_actual_implementation_is_valid_python():
    import ast

    ast.parse(ACTUAL_STAGE04_IMPLEMENTATION)  # SyntaxError면 테스트 실패


def test_provenance_is_documented_not_silent():
    assert "OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001" in ACTUAL_STAGE04_IMPLEMENTATION_PROVENANCE
    assert "재실행" in ACTUAL_STAGE04_IMPLEMENTATION_PROVENANCE


# ---- 2. Review Prompt에 실제 Implementation이 포함되는지 -----------------------


def test_review_prompt_actually_contains_implementation_not_placeholder():
    prompt = _build_review_prompt_with_actual_implementation("def backend_agent_code_review(code): pass")
    assert ACTUAL_STAGE04_IMPLEMENTATION in prompt
    assert "same implementation validated in the Stage 04 run" not in prompt


def test_review_prompt_preserves_input_boundary_sections():
    """ADR-0025/RFC-0039 §9 Input 경계(Design/Contract/Scope/Immutable
    Source Snapshot)가 전부 유지되는지 확인 — 이전 구조를 임의로
    바꾸지 않았음을 보증."""
    prompt = _build_review_prompt_with_actual_implementation("ORIGINAL_SOURCE_MARKER")
    for marker in ("---STAGE 03 DESIGN---", "---CONTRACT---", "---SCOPE CONTEXT---", "---IMMUTABLE SOURCE SNAPSHOT---", "ORIGINAL_SOURCE_MARKER"):
        assert marker in prompt


# ---- 3. Deterministic 비교 기준선 ---------------------------------------------


def test_deterministic_comparison_passes_when_only_target_function_changed():
    original = (
        "def helper():\n    return 1\n\n\n"
        "def backend_agent_code_review(code):\n    return code\n"
    )
    implementation = (
        "def helper():\n    return 1\n\n\n"
        "def backend_agent_code_review(code):\n"
        "    if not code:\n        raise ValueError('x')\n    return code\n"
    )
    result = run_deterministic_comparison(
        original_source_snapshot=original,
        implementation=implementation,
        target_function_name="backend_agent_code_review",
        target_relative_path="fake/path.py",
        original_import_lines=frozenset(),
    )
    assert result.ast_status == "PASS"
    assert result.dependency_status == "PASS"


def test_deterministic_comparison_fails_when_other_function_changed():
    original = "def helper():\n    return 1\n\n\ndef backend_agent_code_review(code):\n    return code\n"
    implementation = "def helper():\n    return 2\n\n\ndef backend_agent_code_review(code):\n    return code\n"
    result = run_deterministic_comparison(
        original_source_snapshot=original,
        implementation=implementation,
        target_function_name="backend_agent_code_review",
        target_relative_path="fake/path.py",
        original_import_lines=frozenset(),
    )
    assert result.ast_status == "FAIL"
    assert "helper" in result.ast_detail["changed_names"]


# ---- 4. 실패 분류(429/5xx/timeout/malformed) ----------------------------------


def test_failure_classification_separates_quota_from_other_errors():
    assert _classify_error_detail(None, 429) == "429_quota"
    assert _classify_error_detail(None, 503) == "5xx"
    assert _classify_error_detail("connection failed: timeout after 90s", None) == "timeout"
    assert _classify_error_detail("connection failed: refused", None) == "connection_error"
    assert _classify_error_detail(None, 400) == "malformed_response"


def test_quota_failure_is_never_classified_as_malformed_or_contract():
    """429는 반드시 별도 category — Contract/malformed로 오분류되면 안 됨
    (사용자 지시: "quota failure를 모델 품질 실패로 판정하지 않는다")."""
    category = _classify_error_detail("some detail", 429)
    assert category == "429_quota"
    assert category not in ("malformed_response", "contract_failure")

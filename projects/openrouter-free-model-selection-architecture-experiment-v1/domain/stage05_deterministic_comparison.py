"""Stage 05 Review(LLM) 결과와 비교할 "기존 deterministic validation 결과"를 만든다(사용자 지시 §Review 품질 — "가능하면 기존 deterministic validation 결과와 비교"). 새 판정 기준을 발명하지 않는다 — 이미 `stage05-parallel-validation-harness-v1`이 RFC-0039 §2.3/§2.4로 구현해둔 `ast_validator`/`dependency_validator`(순수 함수, Engine 호출 없음)를 읽기 전용으로 그대로 재사용한다."""

from __future__ import annotations

from dataclasses import dataclass

from ._sibling_import_stage05_harness import load_sibling_stage05_harness_domain

_sibling = load_sibling_stage05_harness_domain()
ValidationContext = _sibling.validators.ValidationContext
ast_validator = _sibling.validators.ast_validator
dependency_validator = _sibling.validators.dependency_validator


@dataclass
class DeterministicComparisonResult:
    ast_status: str
    ast_detail: dict
    dependency_status: str
    dependency_detail: dict


def run_deterministic_comparison(
    *,
    original_source_snapshot: str,
    implementation: str,
    target_function_name: str,
    target_relative_path: str,
    original_import_lines: frozenset[str],
) -> DeterministicComparisonResult:
    """AST(다른 top-level 정의 미변경) + Dependency(새 import 미추가) 검사 — LLM Review 품질을 판단할 비교 기준선이 된다."""
    ctx = ValidationContext(
        target_relative_path=target_relative_path,
        target_function_name=target_function_name,
        implementation=implementation,
        original_source_snapshot=original_source_snapshot,
        scope_candidates=(target_relative_path,),
        original_import_lines=original_import_lines,
    )
    ast_result = ast_validator(ctx)
    dependency_result = dependency_validator(ctx)
    return DeterministicComparisonResult(
        ast_status=ast_result.status,
        ast_detail=ast_result.detail,
        dependency_status=dependency_result.status,
        dependency_detail=dependency_result.detail,
    )

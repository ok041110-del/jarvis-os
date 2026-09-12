"""Structure/Scope/AST/Dependency — 4개 결정적 Validator(RFC-0039 §2.1
§2.2 §2.3 §2.4의 "책임의 본질" 정의를 그대로 구현). 전부 순수 함수다
— 파일 시스템 접근·Engine 호출 없음, 입력은 미리 준비된 Context
객체뿐(RFC-0039 §1 "Context가 준비된 상태" 전제와 동일)."""

from __future__ import annotations

import ast
import time
from dataclasses import dataclass
from typing import Sequence

from .results import ValidatorResult

_ENGINE_FAILURE_PREFIX = "Engine call failed:"


@dataclass
class ValidationContext:
    """Fan-out 이전에 준비되는 불변 Context(RFC-0039 §5 수정 1) — 6개
    Validator 전부가 이 객체의 필드만 읽고, 서로의 결과를 읽지 않는다."""

    target_relative_path: str
    target_function_name: str
    implementation: str
    original_source_snapshot: str  # AST/Review가 쓰는 읽기 전용 원본(Test Workspace와는 별개 자원, RFC-0039 §5)
    scope_candidates: Sequence[str]
    original_import_lines: frozenset[str]  # Dependency Context — Implementation 이전 시점에 이미 확정된 값


def _timed(fn):
    start = time.perf_counter()
    value = fn()
    elapsed_ms = (time.perf_counter() - start) * 1000
    return value, elapsed_ms


def structure_validator(ctx: ValidationContext) -> ValidatorResult:
    """Implementation이 기대하는 형태(비어있지 않은 문자열, Engine 실패
    신호가 아님)를 갖췄는가(RFC-0039 §2.1)."""

    def _check():
        impl = ctx.implementation
        valid = isinstance(impl, str) and len(impl.strip()) > 0
        engine_failed = impl.strip().startswith(_ENGINE_FAILURE_PREFIX) if isinstance(impl, str) else False
        return {"valid": valid, "engine_failed": engine_failed}

    detail, elapsed_ms = _timed(_check)
    status = "PASS" if detail["valid"] and not detail["engine_failed"] else "FAIL"
    return ValidatorResult("structure", status, elapsed_ms, detail)


def scope_validator(ctx: ValidationContext) -> ValidatorResult:
    """Target이 이미 확정된 Scope Context 안에 있는가(RFC-0039 §2.2) —
    Scope Validator의 '결과'가 아니라 '정의/Context'만 소비한다."""

    def _check():
        in_scope = ctx.target_relative_path in ctx.scope_candidates
        return {"target_in_scope": in_scope}

    detail, elapsed_ms = _timed(_check)
    status = "PASS" if detail["target_in_scope"] else "FAIL"
    return ValidatorResult("scope", status, elapsed_ms, detail)


def _top_level_defs(source: str) -> dict[str, str]:
    tree = ast.parse(source)
    defs = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[node.name] = ast.get_source_segment(source, node)
    return defs


def ast_validator(ctx: ValidationContext) -> ValidatorResult:
    """Implementation이 Target 함수 외의 다른 top-level 정의를 바꾸지
    않았는가(RFC-0039 §2.3) — 원본은 Context의 읽기 전용 스냅샷에서만
    읽는다(Test Workspace를 절대 참조하지 않음)."""

    def _check():
        try:
            original_defs = _top_level_defs(ctx.original_source_snapshot)
        except SyntaxError as exc:
            return {"scope_ok": False, "changed_names": [], "parse_error": f"original: {exc}"}
        try:
            new_defs = _top_level_defs(ctx.implementation)
        except SyntaxError as exc:
            return {"scope_ok": False, "changed_names": [], "parse_error": f"implementation: {exc}"}
        changed = [
            name
            for name in original_defs.keys() | new_defs.keys()
            if name != ctx.target_function_name and original_defs.get(name) != new_defs.get(name)
        ]
        return {"scope_ok": len(changed) == 0, "changed_names": changed}

    detail, elapsed_ms = _timed(_check)
    status = "PASS" if detail["scope_ok"] else "FAIL"
    return ValidatorResult("ast", status, elapsed_ms, detail)


def _import_lines(source: str) -> frozenset[str]:
    tree = ast.parse(source)
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            lines.add(ast.unparse(node))
    return frozenset(lines)


def dependency_validator(ctx: ValidationContext) -> ValidatorResult:
    """Implementation이 참조하는 것(import)이 사전에 확정된 Dependency
    Context(원본 import 집합) 밖으로 새로 추가되지 않았는가(RFC-0039 §2.4)
    — 새 import 추가 금지는 Stage 04 Ponytail policy(`check_no_new_imports`)
    와 동일한 성격의 결정적 검사다."""

    def _check():
        try:
            new_imports = _import_lines(ctx.implementation)
        except SyntaxError as exc:
            return {"dependency_ok": False, "added_imports": [], "parse_error": str(exc)}
        added = sorted(new_imports - ctx.original_import_lines)
        return {"dependency_ok": len(added) == 0, "added_imports": added}

    detail, elapsed_ms = _timed(_check)
    status = "PASS" if detail["dependency_ok"] else "FAIL"
    return ValidatorResult("dependency", status, elapsed_ms, detail)

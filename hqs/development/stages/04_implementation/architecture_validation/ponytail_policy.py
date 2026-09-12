"""Stage 04 Architecture Validation — Ponytail Policy Guardrails. 이번
작업이 지정한 Ponytail 정책 7개 중 코드로 결정적으로 검증 가능한 항목을
다룬다:

1. Architect가 아니다 — 코드 검사 대상 아님(역할 제약, README 참고).
2. Design/Contract/Scope를 변경하지 않는다 — `check_scope_unchanged`.
3. Target을 변경하지 않는다 — `check_target_unchanged`.
4. 새로운 기능/의존성을 추가하지 않는다 — `check_no_new_imports`.
5. 다른 파일을 수정하지 않는다 — 이 Harness는 애초에 파일을 쓰지 않으므로
   구조적으로 항상 만족(코드 검사 대상 아님).
6/7. 충분히 좋은 candidate가 있으면 그대로 선택하고, 필요한 경우에만
   제한적 refinement를 한다 — `check_no_op_when_gate_passed`.

`ponytail_adapter.select_final_candidate()`는 현재 순수 선택만 하고
코드를 전혀 수정하지 않는다(0% refinement) — 그 경우 이 정책은 항상
공허하게(vacuously) 만족된다. 실제 refinement가 도입되면 이 모듈의
체크가 그 refinement를 검증하는 역할을 한다."""

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from deterministic_checks import CheckResult  # noqa: E402


def check_target_unchanged(target_before, target_after) -> CheckResult:
    if target_before != target_after:
        return CheckResult(False, f"target changed: {target_before!r} -> {target_after!r}")
    return CheckResult(True)


def _imported_names(code: str) -> set:
    tree = ast.parse(code)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names.update(f"{module}.{alias.name}" for alias in node.names)
    return names


def check_no_new_imports(code_before: str, code_after: str) -> CheckResult:
    """refinement 이후 코드가 이전에 없던 import를 추가하지 않았는지
    확인한다 — "새로운 기능/의존성을 추가하지 않는다" 정책."""
    try:
        added = _imported_names(code_after) - _imported_names(code_before)
    except SyntaxError as exc:
        return CheckResult(False, f"SyntaxError: {exc}")
    if added:
        return CheckResult(False, f"new imports introduced: {sorted(added)}")
    return CheckResult(True)


def check_scope_unchanged(code_before: str, code_after: str) -> CheckResult:
    """refinement 전후로 정의된 최상위 함수 집합이 동일한지 확인한다 —
    "Design/Contract/Scope를 변경하지 않는다" 정책."""
    try:
        before_defs = {n.name for n in ast.walk(ast.parse(code_before)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        after_defs = {n.name for n in ast.walk(ast.parse(code_after)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    except SyntaxError as exc:
        return CheckResult(False, f"SyntaxError: {exc}")
    if before_defs != after_defs:
        return CheckResult(False, f"scope changed: {before_defs} -> {after_defs}")
    return CheckResult(True)


def check_no_op_when_gate_passed(code_before: str, code_after: str, gate_passed_before: bool) -> CheckResult:
    """이미 Deterministic Gate를 통과한("충분히 좋은") 후보는 수정 없이
    그대로 선택돼야 한다 — 정책 6/7."""
    if gate_passed_before and code_before != code_after:
        return CheckResult(False, "candidate already passed the gate but was modified")
    return CheckResult(True)


def verify_policy(*, target_before, target_after, code_before: str, code_after: str, gate_passed_before: bool) -> dict:
    checks = {
        "target_unchanged": check_target_unchanged(target_before, target_after),
        "no_new_imports": check_no_new_imports(code_before, code_after),
        "scope_unchanged": check_scope_unchanged(code_before, code_after),
        "no_op_when_gate_passed": check_no_op_when_gate_passed(code_before, code_after, gate_passed_before),
    }
    return {"passed": all(bool(result) for result in checks.values()), "checks": checks}

"""Stage 05: Validation 실행 진입점(ADR-0008 §4) — Stage 04 Output을 검증만
하고 수정하지 않는다. PASS/FAIL/PARTIAL은 전부 결정적 규칙으로 계산한다(Policy 구현 금지, IMPLEMENTATION_RULES.md)."""

import ast
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.agents import backend_agent_code_review
from mvp.ast_context import ROOT, module_source_path
from mvp.workflow import _engine_failure_message

_TESTS_DIR = ROOT / "hqs" / "development" / "mvp" / "tests"
_PYTEST_TIMEOUT_SECONDS = 300


def _check_structural(stage_04_output: dict) -> dict:
    valid = all(key in stage_04_output for key in ("target", "implementation", "expose_target"))
    implementation = stage_04_output.get("implementation", "")
    engine_failed = implementation.startswith("Engine call failed:")
    return {"valid": valid, "engine_failed": engine_failed}


def _check_specification_scope(target, stage_02_output: dict) -> dict:
    if target is None:
        return {"target_in_scope": None}

    module_name, _ = target
    target_path = str(module_source_path(module_name).relative_to(ROOT))
    scope_candidates = stage_02_output["skeleton"]["scope_candidates"]
    return {"target_in_scope": target_path in scope_candidates}


def _top_level_defs(source: str) -> dict:
    tree = ast.parse(source)
    defs = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[node.name] = ast.get_source_segment(source, node)
    return defs


def _check_design_scope(target, expose_target: bool, implementation: str) -> dict:
    if target is None or not expose_target:
        return {"scope_ok": None, "changed_names": []}

    module_name, function_name = target
    original_source = module_source_path(module_name).read_text(encoding="utf-8")

    original_defs = _top_level_defs(original_source)
    new_defs = _top_level_defs(implementation)

    changed_names = [
        name
        for name in original_defs.keys() | new_defs.keys()
        if name != function_name and original_defs.get(name) != new_defs.get(name)
    ]
    return {"scope_ok": len(changed_names) == 0, "changed_names": changed_names}


def _run_pytest_with_applied_implementation(target, expose_target: bool, implementation: str) -> dict:
    if target is None or not expose_target:
        return {"executed": False, "returncode": None, "output": ""}

    module_name, _ = target
    path = module_source_path(module_name)
    original = path.read_text(encoding="utf-8")

    try:
        path.write_text(implementation, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(_TESTS_DIR), "-q"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=_PYTEST_TIMEOUT_SECONDS,
        )
        return {
            "executed": True,
            "returncode": result.returncode,
            "output": result.stdout + result.stderr,
        }
    finally:
        path.write_text(original, encoding="utf-8")


def _determine_verdict(structural_check, specification_check, design_scope_check, test_execution) -> str:
    if structural_check["engine_failed"]:
        return "FAIL"
    if test_execution["executed"] and test_execution["returncode"] != 0:
        return "FAIL"
    if design_scope_check["scope_ok"] is False:
        return "FAIL"

    incomplete = (
        not structural_check["valid"]
        or not test_execution["executed"]
        or specification_check["target_in_scope"] is not True
        or design_scope_check["scope_ok"] is not True
    )
    return "PARTIAL" if incomplete else "PASS"


def run_stage_05(issue: dict, stage_02_output: dict, stage_03_output: dict, stage_04_output: dict) -> dict:
    """Structural/Specification/Design Scope 검사 -> Test Execution -> Code
    Review Evidence -> Validation Result. `stage_03_output`은 시그니처 통일용, 미사용(VALIDATION.md)."""
    target = stage_04_output.get("target")
    expose_target = stage_04_output.get("expose_target", False)
    implementation = stage_04_output.get("implementation", "")

    structural_check = _check_structural(stage_04_output)
    specification_check = _check_specification_scope(target, stage_02_output)
    design_scope_check = _check_design_scope(target, expose_target, implementation)
    test_execution = _run_pytest_with_applied_implementation(target, expose_target, implementation)

    if structural_check["engine_failed"]:
        code_review = "(Stage 04 Engine 실패로 Code Review를 건너뜀)"
    else:
        try:
            code_review = backend_agent_code_review(implementation)
        except Exception as exc:
            code_review = _engine_failure_message(exc)

    verdict = _determine_verdict(structural_check, specification_check, design_scope_check, test_execution)

    return {
        "structural_check": structural_check,
        "specification_check": specification_check,
        "design_scope_check": design_scope_check,
        "test_execution": test_execution,
        "code_review": code_review,
        "verdict": verdict,
    }

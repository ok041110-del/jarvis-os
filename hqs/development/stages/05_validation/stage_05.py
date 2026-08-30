"""Stage 05: Validation 실행 진입점(ADR-0008 §4) — Stage 04 Output을 검증만
하고 수정하지 않는다. PASS/FAIL/PARTIAL은 전부 결정적 규칙으로 계산한다(Policy 구현 금지, IMPLEMENTATION_RULES.md)."""

import ast
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import contracts
from mvp.agents import backend_agent_code_review
from mvp.ast_context import ROOT, module_source_path
from mvp.workflow import _engine_failure_message

_TESTS_DIR = ROOT / "hqs" / "development" / "mvp" / "tests"
_PYTEST_TIMEOUT_SECONDS = 300

# VerificationRequirement — 이 Stage가 실행할 수 있는 결정적 검증 항목의
# 전체 이름 집합(`contracts.KNOWN_CHECK_NAMES`와 동일, Single Source of
# Truth). `run_stage_05()`가 받는 `required_checks`는 이 중 실제로 이번
# 실행에서 실행·판정에 반영할 부분집합이며, 여기 없는 항목은 SKIPPED로
# 표시되고 실행되지도 Verdict에 반영되지도 않는다. BLOCKING 항목의 FAIL은
# Verdict를 FAIL로 만들고, 나머지는 미충족 시 PARTIAL만 유발한다.
REQUIRED_CHECKS = contracts.KNOWN_CHECK_NAMES
_BLOCKING_CHECKS = frozenset({"structural", "design_scope", "test_execution"})


def _evaluate_structural(check: dict) -> tuple:
    """(blocking_fail, incomplete) — Engine 실패는 차단, 구조 이상은 미완결."""
    return check["engine_failed"], not check["valid"]


def _evaluate_specification_scope(check: dict) -> tuple:
    """Specification Scope는 항상 non-blocking(기존 동작과 동일)."""
    return False, check["target_in_scope"] is not True


def _evaluate_design_scope(check: dict) -> tuple:
    return check["scope_ok"] is False, check["scope_ok"] is not True


def _evaluate_test_execution(check: dict) -> tuple:
    blocking_fail = check["executed"] and check["returncode"] != 0
    return blocking_fail, not check["executed"]


# name -> raw check dict를 (blocking_fail, incomplete)로 평가하는 함수.
# `_determine_verdict()`와 `_build_check_results()`가 이 하나의 표를
# 공유해 두 곳의 판정 규칙이 서로 다른 값으로 갈라지지 않게 한다(이전
# 감사에서 지적된 "따로 계산되어 우연히 일치할 뿐"이라는 문제의 해소).
_CHECK_EVALUATORS = {
    "structural": _evaluate_structural,
    "specification_scope": _evaluate_specification_scope,
    "design_scope": _evaluate_design_scope,
    "test_execution": _evaluate_test_execution,
}


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


def _determine_verdict(
    structural_check, specification_check, design_scope_check, test_execution, required_checks=None
) -> str:
    """`required_checks`에 포함된 항목만 판정에 반영한다(기본값은 4개
    전부 — 이전 동작과 완전히 동일). 포함되지 않은 항목의 raw dict는
    `None`으로 넘겨 "실행하지 않았다"를 표현할 수 있다."""
    if required_checks is None:
        required_checks = REQUIRED_CHECKS

    raw_checks = {
        "structural": structural_check,
        "specification_scope": specification_check,
        "design_scope": design_scope_check,
        "test_execution": test_execution,
    }

    any_blocking_fail = False
    any_incomplete = False
    for name in required_checks:
        check = raw_checks.get(name)
        if check is None:
            any_incomplete = True
            continue
        blocking_fail, incomplete = _CHECK_EVALUATORS[name](check)
        any_blocking_fail = any_blocking_fail or blocking_fail
        any_incomplete = any_incomplete or incomplete

    if any_blocking_fail:
        return "FAIL"
    return "PARTIAL" if any_incomplete else "PASS"


def _check_result(name: str, raw_check, required_checks) -> dict:
    """`name`이 `required_checks`에 없으면 실행하지 않았다는 의미로
    `SKIPPED`를 반환한다(이 경우 raw_check는 `None`이어야 한다) —
    required_checks 값이 실제로 실행 집합을 바꾼다는 것을 결과에도
    드러낸다."""
    if name not in required_checks:
        return {"name": name, "status": "SKIPPED", "blocking": False, "detail": {}}

    blocking_fail, incomplete = _CHECK_EVALUATORS[name](raw_check)
    status = "FAIL" if blocking_fail else ("INCONCLUSIVE" if incomplete else "PASS")
    return {"name": name, "status": status, "blocking": name in _BLOCKING_CHECKS, "detail": raw_check}


def _build_check_results(structural_check, specification_check, design_scope_check, test_execution, required_checks=None) -> list:
    """4개 결정적 Capability 결과를 CheckResult 목록(VerificationResult
    Contract)으로 구조화한다. `_determine_verdict()`와 동일한
    `_CHECK_EVALUATORS`를 공유하므로 두 결과가 서로 다른 값으로 갈라질
    수 없다."""
    if required_checks is None:
        required_checks = REQUIRED_CHECKS

    raw_checks = {
        "structural": structural_check,
        "specification_scope": specification_check,
        "design_scope": design_scope_check,
        "test_execution": test_execution,
    }
    return [_check_result(name, raw_checks[name], required_checks) for name in contracts.KNOWN_CHECK_NAMES]


def run_stage_05(stage_02_output: dict, stage_04_output: dict, required_checks=None) -> dict:
    """Structural/Specification/Design Scope 검사 -> Test Execution -> Code
    Review Evidence -> Validation Result. `issue`/`stage_03_output`은 이
    Stage가 실제로 쓰지 않아 Input에서 제거했다(ImplementationResult/
    SpecificationResult Contract만 Consume).

    `required_checks`(생략 시 4개 전부)에 없는 항목은 실행 자체를
    건너뛰고(SKIPPED) Verdict에도 반영하지 않는다 — required_checks가
    실행 집합과 Verdict 둘 다에 실제로 인과적인 영향을 준다. 비어 있거나
    알 수 없는 이름이 섞이면 조용히 넘어가지 않고 즉시 실패한다
    (`contracts.validate_verification_requirement`)."""
    if required_checks is None:
        required_checks = REQUIRED_CHECKS
    contracts.validate_verification_requirement(required_checks)

    target = stage_04_output.get("target")
    expose_target = stage_04_output.get("expose_target", False)
    implementation = stage_04_output.get("implementation", "")

    structural_check = _check_structural(stage_04_output) if "structural" in required_checks else None
    specification_check = (
        _check_specification_scope(target, stage_02_output) if "specification_scope" in required_checks else None
    )
    design_scope_check = (
        _check_design_scope(target, expose_target, implementation) if "design_scope" in required_checks else None
    )
    test_execution = (
        _run_pytest_with_applied_implementation(target, expose_target, implementation)
        if "test_execution" in required_checks
        else None
    )

    # Code Review 실행 여부는 "structural이 required인지"와 무관하게,
    # Stage 04 Output 자체의 Engine 실패 여부로만 판단한다(구 동작과 동일
    # — structural을 skip해도 이 게이팅은 깨지지 않는다).
    if implementation.startswith("Engine call failed:"):
        code_review = "(Stage 04 Engine 실패로 Code Review를 건너뜀)"
    else:
        try:
            code_review = backend_agent_code_review(implementation)
        except Exception as exc:
            code_review = _engine_failure_message(exc)

    verdict = _determine_verdict(
        structural_check, specification_check, design_scope_check, test_execution, required_checks
    )
    check_results = _build_check_results(
        structural_check, specification_check, design_scope_check, test_execution, required_checks
    )

    return {
        "structural_check": structural_check,
        "specification_check": specification_check,
        "design_scope_check": design_scope_check,
        "test_execution": test_execution,
        "code_review": code_review,
        "required_checks": tuple(required_checks),
        "check_results": check_results,
        "verdict": verdict,
    }

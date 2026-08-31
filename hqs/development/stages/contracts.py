"""Stage 01~05 Data Contract — Stage 간 주고받는 데이터의 의미와 필수 필드를
정의한다. 새 Architecture Concept이 아니라, 각 Stage README/RESPONSIBILITY/
VALIDATION.md가 이미 문서로 정의한 Input/Output을 코드로 명시하고 검증
가능하게 만드는 것뿐이다(RFC-0007/ADC-0005/ADR-0008 Stage 구조 위에 추가,
Stage 순서·개수·Capability는 무변경).

Producer/Consumer:
- CandidateIndex — Producer: Stage 01. Consumer: Stage 03(component_candidates
  재배치), Stage 04(target 식별, 재계산 없이 재사용).
- DependencyClosure — Producer: Stage 01(target이 이미 있을 때만) 또는
  Stage 04(target을 그때 식별한 경우). Target이 Design 이후에야 식별되는
  현재 Static Workflow에서는 사실상 Stage 04가 Producer다(아래 Stage 04
  Responsibility 참고).
- SpecificationResult — Producer: Stage 02. Consumer: Stage 03(skeleton 재배치),
  Stage 05(specification_check).
- DesignResult — Producer: Stage 03. Consumer: Stage 04.
- ImplementationResult — Producer: Stage 04. Consumer: Stage 05.
- VerificationResult — Producer: Stage 05. Consumer 없음(최종 산출물,
  CLI가 재해석 없이 그대로 출력).

Contract validation 책임: 각 Stage는 자신이 반환하는 dict의 형태에 책임을
지고, Stage 간 Handover 시점의 필수 키 존재 여부는 `workflow.py`가 명시적으로
검증한다(키/구조 확인만 — 값의 의미 재해석은 하지 않는다. 재해석은 여전히
각 Stage의 책임이다)."""

from typing import TypedDict

# CandidateIndex/DependencyClosure는 Stage 01의 순수 정적 분석 결과값(문자열)
# 그 자체이며, 별도 필드를 감싸는 새 자료구조를 만들지 않는다(Wrapper 금지 —
# Registry/Gateway와 같은 일반화를 피한다).
CandidateIndex = str
DependencyClosure = str


class ContractViolation(Exception):
    """Stage Output이 Contract가 요구하는 필드를 채우지 않았을 때 발생한다."""


def require_keys(data: dict, keys: tuple, contract_name: str) -> None:
    """`data`에 `keys`가 전부 있는지만 확인한다(값의 타입/의미는 검사하지
    않음 — Stage 내부 로직의 재해석이 아니라 Handover 시점 존재 확인)."""
    missing = [key for key in keys if key not in data]
    if missing:
        raise ContractViolation(f"{contract_name} contract violated — missing keys: {missing}")


class ContextAnalysisResult(TypedDict):
    """Stage 01 Output(CONTEXT.md) — Producer: Stage 01."""

    directory_structure: object
    context_bundle: dict
    candidate_index: CandidateIndex
    target: object
    dependency_closure: object


class SpecificationResult(TypedDict):
    """Stage 02 Output(SPECIFICATION.md) — Producer: Stage 02."""

    skeleton: dict
    specification: str


class DesignResult(TypedDict):
    """Stage 03 Output(DESIGN.md) — Producer: Stage 03."""

    skeleton: dict
    design: str


class ImplementationResult(TypedDict):
    """Stage 04 Output(IMPLEMENTATION.md) — Producer: Stage 04."""

    target: object
    implementation: str
    expose_target: bool


# VerificationRequirement — Stage 05가 실행할 수 있는 검증 항목의 전체
# 이름 집합(고정 4개, 새 검사 종류 추가 아님). `required_checks`는 이
# 집합의 부분집합이어야 하며, 이 값이 실제 실행 여부(SKIPPED 여부)와
# Verdict 반영 여부를 결정한다(Producer: 호출자 — 현재 Static Workflow는
# 항상 전체 집합을 기본값으로 쓴다, Consumer: Stage 05 자기 자신).
KNOWN_CHECK_NAMES = ("structural", "specification_scope", "design_scope", "test_execution")


class CheckResult(TypedDict):
    """Stage 05가 산출하는 단일 검증 항목 결과(VerificationRequirement 한 건에 대응)."""

    name: str
    status: str  # "PASS" | "FAIL" | "INCONCLUSIVE" | "SKIPPED"
    blocking: bool
    detail: dict


class VerificationResult(TypedDict):
    """Stage 05 Output(VALIDATION.md) — Producer: Stage 05, 최종 산출물."""

    required_checks: tuple
    check_results: list
    structural_check: dict
    specification_check: dict
    design_scope_check: dict
    test_execution: dict
    code_review: str
    verdict: str


CONTEXT_ANALYSIS_REQUIRED_KEYS = (
    "directory_structure",
    "context_bundle",
    "candidate_index",
    "target",
    "dependency_closure",
)
SPECIFICATION_REQUIRED_KEYS = ("skeleton", "specification")
DESIGN_REQUIRED_KEYS = ("skeleton", "design")
IMPLEMENTATION_REQUIRED_KEYS = ("target", "implementation", "expose_target")
VERIFICATION_REQUIRED_KEYS = ("required_checks", "check_results", "verdict")


def validate_context_analysis_result(data: dict) -> None:
    require_keys(data, CONTEXT_ANALYSIS_REQUIRED_KEYS, "ContextAnalysisResult")


def validate_specification_result(data: dict) -> None:
    require_keys(data, SPECIFICATION_REQUIRED_KEYS, "SpecificationResult")


def validate_design_result(data: dict) -> None:
    require_keys(data, DESIGN_REQUIRED_KEYS, "DesignResult")


def validate_implementation_result(data: dict) -> None:
    require_keys(data, IMPLEMENTATION_REQUIRED_KEYS, "ImplementationResult")


def validate_verification_requirement(required_checks) -> None:
    """`required_checks`가 비어 있거나 알 수 없는 이름을 포함하면 조용히
    통과시키지 않고 즉시 실패시킨다(빈 목록은 "아무 것도 요구하지 않음"이
    아니라 계약 위반이다 — required_checks가 존재해도 무시되던 이전
    결함의 재발을 막는 방어선)."""
    if not required_checks:
        raise ContractViolation("VerificationRequirement contract violated — required_checks must not be empty")
    unknown = [name for name in required_checks if name not in KNOWN_CHECK_NAMES]
    if unknown:
        raise ContractViolation(f"VerificationRequirement contract violated — unknown check names: {unknown}")


def validate_verification_result(data: dict) -> None:
    """필수 키 존재뿐 아니라, `required_checks`에 선언된 항목이 실제로
    `check_results`에서 실행됐는지(SKIPPED가 아닌지)까지 확인한다 —
    required_checks가 선언만 되고 실행/판정과 연결되지 않는 상태(decorative
    mirror)를 Contract 층에서도 차단한다."""
    require_keys(data, VERIFICATION_REQUIRED_KEYS, "VerificationResult")
    required_checks = data["required_checks"]
    validate_verification_requirement(required_checks)

    results_by_name = {check["name"]: check for check in data["check_results"]}
    missing = [name for name in required_checks if name not in results_by_name]
    if missing:
        raise ContractViolation(
            f"VerificationResult contract violated — required_checks missing from check_results: {missing}"
        )

    not_executed = [name for name in required_checks if results_by_name[name]["status"] == "SKIPPED"]
    if not_executed:
        raise ContractViolation(
            f"VerificationResult contract violated — required check(s) declared but not executed: {not_executed}"
        )

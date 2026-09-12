"""Stage Contract Validation — 가능하면 기존 Production parser/validator를
그대로 재사용한다(사용자 지시 §5). 새 LLM judge를 추가하지 않는다 — 전부
결정적 파싱/구조 검사다."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[3]

# --- 기존 Production 모듈 재사용(읽기 전용 import, 수정 없음) -----------------

_REASONING_PATH = REPO_ROOT / "hqs" / "development" / "stages" / "01_context_analysis" / "reasoning.py"
_spec = importlib.util.spec_from_file_location("stage01_reasoning", _REASONING_PATH)
_reasoning = importlib.util.module_from_spec(_spec)
sys.modules["stage01_reasoning"] = _reasoning
_spec.loader.exec_module(_reasoning)

parse_structured_output = _reasoning.parse_structured_output  # 실제 Production 함수
AgentOutputError = _reasoning.AgentOutputError
REQUIREMENT_REQUIRED_KEYS = _reasoning.REQUIREMENT_REQUIRED_KEYS


class ContractResult:
    def __init__(self, passed: bool, detail: dict):
        self.passed = passed
        self.detail = detail

    def __bool__(self) -> bool:
        return self.passed

    def __repr__(self) -> str:
        return f"ContractResult(passed={self.passed!r}, detail={self.detail!r})"


def stage01_contract(raw_response: str) -> ContractResult:
    """Stage 01 Requirement Agent Contract — 기존 `reasoning.py::
    parse_structured_output` + `REQUIREMENT_REQUIRED_KEYS`를 그대로
    재사용(재구현 없음)."""
    try:
        parsed = parse_structured_output(raw_response)
    except AgentOutputError as exc:
        return ContractResult(False, {"error": str(exc)})
    missing = [key for key in REQUIREMENT_REQUIRED_KEYS if key not in parsed]
    return ContractResult(not missing, {"parsed_keys": list(parsed.keys()), "missing_keys": missing})


def stage02_contract(raw_response: str) -> ContractResult:
    """Stage 02 Task & Dependency Agent Contract — 동일 production
    파서(`parse_structured_output`) 재사용, `tasks`/`dependencies` 키
    존재만 확인(Deterministic Layer 책임, `task_dependency_agent.py`
    docstring과 동일 원칙 — 스키마 세부 검증은 Contract 밖)."""
    try:
        parsed = parse_structured_output(raw_response)
    except AgentOutputError as exc:
        return ContractResult(False, {"error": str(exc)})
    has_tasks = isinstance(parsed.get("tasks"), list)
    has_deps = isinstance(parsed.get("dependencies"), list)
    return ContractResult(has_tasks and has_deps, {"has_tasks": has_tasks, "has_dependencies": has_deps})


_STAGE03_REQUIRED_SECTIONS = (
    "Architecture Definition",
    "Component Identification",
    "Responsibility Allocation",
    "Interface",
    "Data Flow",
    "Implementation Strategy",
)


def stage03_contract(raw_response: str) -> ContractResult:
    """Stage 03 Design Contract — `stages/03_architecture_design/stage_03.py::
    _DESIGN_INSTRUCTION`이 요구하는 6개 항목의 존재 여부(결정적 문자열
    검사, 이전 세션 `OPENROUTER-STAGE-MODEL-SELECTION-0001.md` §3.3이 이미
    쓴 것과 동일 기준 재사용 — 새 판정 기준 발명 아님)."""
    missing = [s for s in _STAGE03_REQUIRED_SECTIONS if s not in raw_response]
    return ContractResult(not missing, {"missing_sections": missing, "response_length": len(raw_response)})


def stage04_contract(raw_response: str, *, target_function_name: str) -> ContractResult:
    """Stage 04 Implementation Contract — AST로 top-level 정의 목록을
    확인(코드 fence 제거 후 유효 Python인지, Target 함수가 실제로
    존재하는지)만 검사한다. 실제 Design Scope(다른 함수 미변경) 비교는
    이 Contract 밖(Stage 05 책임, 사용자 지시 §7 Stage 05 항목과 경계를
    맞춤) — 여기서는 "코드로서 유효하고 Target을 포함하는가"만 본다."""
    import ast

    code = raw_response.strip()
    lines = code.splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
        code = "\n".join(lines[1:-1])
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return ContractResult(False, {"error": f"invalid Python: {exc}"})
    top_level_names = {
        node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    has_target = target_function_name in top_level_names
    return ContractResult(has_target, {"top_level_names": sorted(top_level_names), "has_target": has_target})


def stage05_review_contract(raw_response: str) -> ContractResult:
    """Stage 05 Review(advisory) Contract — 비어있지 않은 prose인지만
    확인한다(Review는 애초에 blocking이 아니므로 Contract도 최소한만,
    사용자 지시 §7 Stage 05 항목: "LLM Review is experimental/advisory
    only")."""
    non_empty = bool(raw_response and raw_response.strip())
    return ContractResult(non_empty, {"response_length": len(raw_response or "")})


STAGE_CONTRACTS: dict[str, Callable] = {
    "stage01": stage01_contract,
    "stage02": stage02_contract,
    "stage03": stage03_contract,
    "stage04": stage04_contract,
    "stage05_review": stage05_review_contract,
}

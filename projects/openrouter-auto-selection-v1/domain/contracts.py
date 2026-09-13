"""Stage Contract Validation — 가능하면 기존 Production parser/validator를 그대로 재사용한다(사용자 지시 §5). 새 LLM judge를 추가하지 않는다 — 전부 결정적 파싱/구조 검사다."""

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
    try:
        parsed = parse_structured_output(raw_response)
    except AgentOutputError as exc:
        return ContractResult(False, {"error": str(exc)})
    missing = [key for key in REQUIREMENT_REQUIRED_KEYS if key not in parsed]
    return ContractResult(not missing, {"parsed_keys": list(parsed.keys()), "missing_keys": missing})


def stage02_contract(raw_response: str) -> ContractResult:
    """`tasks`/`dependencies` 키 존재만 확인한다 — 스키마 세부 검증은 Deterministic Layer 책임으로 Contract 밖에 둔다."""
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
    """`_DESIGN_INSTRUCTION`이 요구하는 6개 항목의 존재 여부를 문자열 검사로 확인한다 — 이전 세션(§3.3)이 쓴 기준 재사용."""
    missing = [s for s in _STAGE03_REQUIRED_SECTIONS if s not in raw_response]
    return ContractResult(not missing, {"missing_sections": missing, "response_length": len(raw_response)})


def stage04_contract(raw_response: str, *, target_function_name: str) -> ContractResult:
    """코드로서 유효하고 Target 함수를 포함하는지만 본다 — Design Scope(다른 함수 미변경) 비교는 Stage 05 책임이라 이 Contract 밖이다."""
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
    """비어있지 않은 prose인지만 확인한다 — Review는 blocking이 아니므로 Contract도 최소한만 둔다."""
    non_empty = bool(raw_response and raw_response.strip())
    return ContractResult(non_empty, {"response_length": len(raw_response or "")})


STAGE_CONTRACTS: dict[str, Callable] = {
    "stage01": stage01_contract,
    "stage02": stage02_contract,
    "stage03": stage03_contract,
    "stage04": stage04_contract,
    "stage05_review": stage05_review_contract,
}

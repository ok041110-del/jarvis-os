"""Review Validator — 3개 Mode(disabled/deterministic/llm, Experiment B).
어떤 Mode든 다른 5개 Validator의 결과를 입력으로 받지 않는다(RFC-0039
§2.6.1 — 5개 각각에 대해 불필요함을 이미 확인). Review는 항상
advisory(비-blocking)로만 Aggregator에 전달된다.

LLM Mode는 기존 Engine Contract(`str -> str`, 실패 시 단일 예외)와
동일한 형태의 `engine_call: Callable[[str], str]`을 주입받는다 — 이
모듈 자신은 어떤 Engine도 소유·선택하지 않는다(새 Gateway/Router 없음,
사용자 지시 Part 2). `engine_call`을 주입하지 않으면 LLM Mode는
`ReviewEngineNotConfigured`로 명시적으로 실패한다 — 조용히 스킵하거나
가짜 결과를 만들지 않는다."""

from __future__ import annotations

import ast
import re
import time
from dataclasses import dataclass
from typing import Callable, Optional

from .results import ValidatorResult
from .validators import ValidationContext

REVIEW_MODES = ("disabled", "deterministic", "llm")


class ReviewEngineNotConfigured(RuntimeError):
    """LLM Review Mode인데 `engine_call`이 주입되지 않았을 때."""


@dataclass
class ReviewConfig:
    mode: str  # "disabled" | "deterministic" | "llm"
    engine_call: Optional[Callable[[str], str]] = None  # LLM Mode 전용, str -> str

    def __post_init__(self) -> None:
        if self.mode not in REVIEW_MODES:
            raise ValueError(f"unknown review mode: {self.mode!r}, expected one of {REVIEW_MODES}")


# ---- Deterministic Review — 결정론적으로 근사 가능한 부분집합만 다룬다.
# (Stage 04 Architecture Validation Harness의 `quality_heuristics.py`와
# 동일한 성격 — 의미적 결함 판단은 하지 않는다, RFC-0039 §8 재확인.)

_BARE_EXCEPT_RE = re.compile(r"^\s*except\s*:\s*$", re.MULTILINE)
_TODO_RE = re.compile(r"#\s*(TODO|FIXME|XXX)\b", re.IGNORECASE)


def _deterministic_findings(implementation: str) -> list[str]:
    findings = []
    if _BARE_EXCEPT_RE.search(implementation):
        findings.append("bare 'except:' clause found (swallows all exceptions)")
    if _TODO_RE.search(implementation):
        findings.append("TODO/FIXME/XXX marker left in code")
    try:
        tree = ast.parse(implementation)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                findings.append(f"function '{node.name}' has no docstring")
    except SyntaxError as exc:
        findings.append(f"implementation does not parse as valid Python: {exc}")
    return findings


def _run_deterministic(ctx: ValidationContext) -> dict:
    findings = _deterministic_findings(ctx.implementation)
    return {"mode": "deterministic", "findings": findings, "finding_count": len(findings)}


def _build_llm_review_prompt(ctx: ValidationContext) -> str:
    """Review Input 경계(사용자 지시)를 그대로 구현한다 — Stage 03
    Design / Stage 04 Implementation / Contract / Scope Context / Immutable
    Source Snapshot **만** 포함한다. Structure/Scope/AST/Dependency/Test의
    ValidatorResult는 이 함수의 인자로 존재하지 않으므로(시그니처가
    `ctx: ValidationContext` 하나뿐) 애초에 여기 들어올 수 없다 — Review
    독립성은 우연이 아니라 함수 시그니처로 구조적으로 강제된다."""
    instruction = (
        "You are the Review capability of a validation pipeline. Review the "
        "following code and describe issues in prose (bugs, risks, style) — "
        "do not rewrite or restate the code as your answer. A real issue is "
        "a concrete defect that would cause wrong output, a crash, or a "
        "violation of the function's own stated behavior — improvement "
        "ideas (add more validation, add tests, add docs, style "
        "preferences) are not real issues by themselves. Respond with a "
        "short list of findings; if you find no real issues, say so "
        "explicitly."
    )
    contract_description = (
        "External Contract: the reviewed function must remain "
        "`str -> str` (single argument in, string out), with failures "
        "surfaced as a single exception type — the same contract every "
        "other capability in this pipeline already assumes."
    )
    scope_description = (
        "Scope Context (files this change is allowed to touch): "
        f"{', '.join(ctx.scope_candidates) or '(none declared)'}"
    )
    return (
        f"{instruction}\n\n"
        f"---STAGE 03 DESIGN---\n{ctx.design_context or '(no design context provided)'}\n\n"
        f"---CONTRACT---\n{contract_description}\n\n"
        f"---SCOPE CONTEXT---\n{scope_description}\n\n"
        f"---IMMUTABLE SOURCE SNAPSHOT (target file, before this change)---\n"
        f"{ctx.original_source_snapshot}\n\n"
        f"---STAGE 04 IMPLEMENTATION (the proposed change to review)---\n"
        f"{ctx.implementation}"
    )


def _run_llm(ctx: ValidationContext, engine_call: Optional[Callable[[str], str]]) -> dict:
    if engine_call is None:
        raise ReviewEngineNotConfigured(
            "Review mode='llm'이지만 engine_call이 주입되지 않았다 — "
            "이 Harness는 임의의 Engine을 대신 선택하지 않는다(실험 설계 원칙)"
        )
    prompt = _build_llm_review_prompt(ctx)
    raw = engine_call(prompt)
    return {"mode": "llm", "raw_response": raw, "prompt_char_count": len(prompt)}


def review_validator(ctx: ValidationContext, config: ReviewConfig) -> ValidatorResult:
    start = time.perf_counter()
    if config.mode == "disabled":
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ValidatorResult("review", "SKIPPED", elapsed_ms, {"mode": "disabled"})

    if config.mode == "deterministic":
        detail = _run_deterministic(ctx)
        elapsed_ms = (time.perf_counter() - start) * 1000
        status = "FAIL" if detail["finding_count"] > 0 else "PASS"
        return ValidatorResult("review", status, elapsed_ms, detail)

    # mode == "llm"
    try:
        detail = _run_llm(ctx, config.engine_call)
    except ReviewEngineNotConfigured as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ValidatorResult("review", "ERROR", elapsed_ms, {"mode": "llm"}, error=str(exc))
    except Exception as exc:  # noqa: BLE001 - Engine 호출 실패를 구조화된 ERROR로 흡수
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ValidatorResult("review", "ERROR", elapsed_ms, {"mode": "llm"}, error=f"engine call failed: {exc}")
    elapsed_ms = (time.perf_counter() - start) * 1000
    # LLM 응답의 PASS/FAIL 자체는 이 Harness가 임의로 파싱해 판정하지 않는다
    # (Policy 구현 금지 원칙 — Review는 항상 advisory, 상태는 응답을 받았는지
    # 여부만 나타낸다).
    return ValidatorResult("review", "PASS", elapsed_ms, detail)

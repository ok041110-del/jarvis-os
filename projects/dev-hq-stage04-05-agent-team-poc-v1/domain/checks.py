"""Stage 05 결정적 검사 + Verdict — Production 구조를 재현한다(원문 복사 아님). Verdict는 review/qa의 자연어 내용을 참조하지 않는다."""
from __future__ import annotations


def check_structural(implementation: dict) -> dict:
    return {"blocking_fail": implementation.get("status") != "ok"}


def check_syntax(code: str) -> dict:
    try:
        compile(code, "<poc>", "exec")
        return {"blocking_fail": False}
    except SyntaxError:
        return {"blocking_fail": True}


def determine_verdict(structural: dict, syntax: dict) -> str:
    """4개 결정적 검사를 2개로 축소 재현 — 시그니처 자체가 review/qa dict를 받지 않음을 증명한다."""
    if structural["blocking_fail"] or syntax["blocking_fail"]:
        return "FAIL"
    return "PASS"

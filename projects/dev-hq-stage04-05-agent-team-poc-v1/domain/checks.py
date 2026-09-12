"""Stage 05 결정적 검사 + Verdict — Production `stage_05.py`의
`_CHECK_EVALUATORS`/`_determine_verdict` **구조**를 재현한다(원문
복사 아님, import 없음). Verdict는 이 모듈이 소유하고 Agent가 아니다
— `review`/`qa`의 자연어 내용을 참조하지 않는다(Phase F-2 확장 §6의
경계 재확인 대상).
"""
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
    """4개 결정적 검사를 2개로 축소 재현(핵심 성질만) — 어느 것도
    `review`/`qa` dict를 인자로 받지 않는다는 것이 이 함수 시그니처
    자체로 증명된다."""
    if structural["blocking_fail"] or syntax["blocking_fail"]:
        return "FAIL"
    return "PASS"

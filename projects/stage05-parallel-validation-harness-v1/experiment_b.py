"""Experiment B — Review Case A(disabled)/B(deterministic)/C(llm) 비교
(사용자 지시 Part 2). LLM Review는 실제 호출 가능한 구조(engine_call
주입)만 만들고, 기본 실행에서는 호출하지 않는다 — OpenRouter 등 실제
호출은 이번 작업의 필수 조건이 아니다(사용자 지시 전문). 호출하지
않은 경우 결과는 "NOT_EXECUTED"로 명시하며, 추정치로 채우지 않는다."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.fixtures import build_fixture, build_validation_context  # noqa: E402
from domain.review import ReviewConfig, review_validator  # noqa: E402


def _run_case(ctx, mode: str, engine_call: Optional[Callable[[str], str]] = None) -> dict:
    config = ReviewConfig(mode=mode, engine_call=engine_call)
    result = review_validator(ctx, config)
    return {
        "case": mode,
        "status": result.status,
        "latency_ms": round(result.latency_ms, 3),
        "detail": result.detail,
        "error": result.error,
    }


def main(engine_call: Optional[Callable[[str], str]] = None) -> dict:
    fixture = build_fixture(REPO_ROOT)
    ctx = build_validation_context(fixture)

    case_a = _run_case(ctx, "disabled")
    case_b = _run_case(ctx, "deterministic")

    if engine_call is None:
        case_c = {
            "case": "llm",
            "status": "NOT_EXECUTED",
            "latency_ms": None,
            "detail": {
                "reason": (
                    "engine_call이 주입되지 않았다 — OpenRouter/실제 Engine 호출은 "
                    "이번 작업의 필수 조건이 아니므로 기본 실행에서는 호출하지 않는다. "
                    "어댑터 구조(str -> str Contract)는 domain/review.py에 존재한다."
                )
            },
            "error": None,
        }
    else:
        case_c = _run_case(ctx, "llm", engine_call=engine_call)

    # deterministic이 발견한 findings와 LLM 응답의 중복 여부는, LLM을
    # 실제로 호출한 경우에만 비교 가능하다 — 호출하지 않았다면 추정하지 않는다.
    overlap_analysis = "NOT_DETERMINED — LLM Review가 실행되지 않아 비교 불가"
    if case_c["status"] not in ("NOT_EXECUTED", "ERROR"):
        overlap_analysis = (
            "NOT_DETERMINED — 이 Harness는 자유 형식 prose(LLM 응답)와 "
            "deterministic findings를 자동으로 비교할 파서를 아직 갖추지 않았다"
        )

    return {
        "case_a_disabled": case_a,
        "case_b_deterministic": case_b,
        "case_c_llm": case_c,
        "deterministic_llm_overlap_analysis": overlap_analysis,
        "final_verdict_change_by_review": (
            "NOT_APPLICABLE — Aggregator 정책상 Review는 Verdict에 절대 반영되지 않는다"
            "(domain/aggregator.py, ADR 초안 §7/§9 재확인)"
        ),
    }


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2, ensure_ascii=False))

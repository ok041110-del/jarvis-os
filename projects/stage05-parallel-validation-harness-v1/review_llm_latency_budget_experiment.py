"""Part 7 — Review LLM latency budget 측정 구조(사용자 지시). 실제 LLM
호출은 이번 세션에서 수행하지 않는다(별도 승인 없이 Production에
추가하지 않음, OpenRouter는 Experimental Validation에만 허용되며 이
스크립트도 기본 실행에서는 호출하지 않는다). `engine_call`을 주입하면
그대로 측정 가능한 구조만 만든다."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.fixtures import build_fixture, build_validation_context  # noqa: E402
from domain.review import ReviewConfig, review_validator  # noqa: E402

# 최적화 후(느린 3개 테스트 제외) 실측된 Stage 05 latency — Evidence 문서 §1 인용.
T_EXISTING_STAGE05_OPTIMIZED_MS = 9_400.0  # Case 4 실측(9.12s) + workspace copy(~0.3s) 근사


def measure_review_llm_latency_budget(engine_call: Optional[Callable[[str], str]] = None) -> dict:
    fixture = build_fixture(REPO_ROOT)
    ctx = build_validation_context(fixture)

    if engine_call is None:
        return {
            "t_review_llm_ms": None,
            "t_existing_stage05_ms": T_EXISTING_STAGE05_OPTIMIZED_MS,
            "t_total_with_review_llm_ms": None,
            "status": "NOT_EXECUTED",
            "reason": (
                "engine_call이 주입되지 않았다 — 실제 LLM 호출은 별도 승인 없이 "
                "수행하지 않는다(사용자 지시). 이 함수에 engine_call을 주입하면 "
                "그대로 실측 가능하다."
            ),
        }

    start = time.perf_counter()
    result = review_validator(ctx, ReviewConfig(mode="llm", engine_call=engine_call))
    t_review_llm_ms = (time.perf_counter() - start) * 1000

    return {
        "t_review_llm_ms": t_review_llm_ms,
        "t_existing_stage05_ms": T_EXISTING_STAGE05_OPTIMIZED_MS,
        "t_total_with_review_llm_ms": T_EXISTING_STAGE05_OPTIMIZED_MS + t_review_llm_ms,
        "relative_increase_pct": (t_review_llm_ms / T_EXISTING_STAGE05_OPTIMIZED_MS) * 100,
        "status": result.status,
        "review_error": result.error,
    }


if __name__ == "__main__":
    print(json.dumps(measure_review_llm_latency_budget(), indent=2, ensure_ascii=False))

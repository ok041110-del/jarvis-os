"""Stage 05 Review Validator LLM — 실제 3회 실행(OpenRouter Experimental
Validation Endpoint). Production Stage Engine Routing과 무관 — Contract
변경 없음, API Key/Credential 탐색·출력 없음(사용자 지시 전문)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from domain.aggregator import aggregate  # noqa: E402
from domain.fixtures import build_fixture, build_validation_context  # noqa: E402
from domain.openrouter_experimental_adapter import (  # noqa: E402
    OpenRouterCallError,
    make_openrouter_engine_call,
    timed_call,
)
from domain.results import ValidatorResult  # noqa: E402
from domain.review import ReviewConfig, review_validator, _deterministic_findings  # noqa: E402
from domain.validators import (  # noqa: E402
    ast_validator,
    dependency_validator,
    scope_validator,
    structure_validator,
)

MODEL = "nex-agi/nex-n2.5-mini:free"
RUN_COUNT = 3
MAX_TOKENS = 1800
MAX_RETRIES_PER_RUN = 2  # 429/502 등 upstream 일시 오류만 재시도(모델 품질 문제 아님, 이전 세션 관례)


def _run_once(ctx, engine_call, run_index: int) -> dict:
    attempts = []
    last_error = None
    for attempt in range(1, MAX_RETRIES_PER_RUN + 2):
        start = time.perf_counter()
        try:
            prompt = None
            from domain.review import _build_llm_review_prompt

            prompt = _build_llm_review_prompt(ctx)
            raw_response, api_latency_ms = timed_call(engine_call, prompt)
            total_latency_ms = (time.perf_counter() - start) * 1000
            attempts.append({"attempt": attempt, "succeeded": True, "error": None})
            return {
                "run": run_index,
                "model": MODEL,
                "success": True,
                "attempts": attempts,
                "total_latency_ms": total_latency_ms,
                "api_latency_ms": api_latency_ms,
                "raw_response": raw_response,
                "prompt_char_count": len(prompt),
            }
        except OpenRouterCallError as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            attempts.append({"attempt": attempt, "succeeded": False, "error": str(exc), "elapsed_ms": elapsed_ms})
            last_error = str(exc)
            if attempt <= MAX_RETRIES_PER_RUN:
                time.sleep(5)
                continue
    return {
        "run": run_index,
        "model": MODEL,
        "success": False,
        "attempts": attempts,
        "total_latency_ms": None,
        "api_latency_ms": None,
        "raw_response": None,
        "error": last_error,
    }


def _count_findings_in_prose(raw_response: str) -> int:
    """LLM 응답(자유 형식 prose)에서 finding 개수를 세는 결정론적 규칙 —
    번호 매김 목록 줄 수를 센다. 파싱 실패 시 0을 반환하지 않고 -1로
    "파싱 불가"를 명시(추정 금지)."""
    if not raw_response:
        return -1
    import re

    numbered = re.findall(r"^\s*\d+[\.\)]\s+\S", raw_response, re.MULTILINE)
    bulleted = re.findall(r"^\s*[-*]\s+\S", raw_response, re.MULTILINE)
    if numbered:
        return len(numbered)
    if bulleted:
        return len(bulleted)
    return -1  # 목록 형식이 아님 — 자동 카운트 불가(사람이 §Quality Analysis에서 직접 확인)


def main() -> dict:
    fixture = build_fixture(REPO_ROOT)
    ctx = build_validation_context(fixture)
    engine_call = make_openrouter_engine_call(MODEL, max_tokens=MAX_TOKENS)

    # Review Input 경계 확인 — Structure/Scope/AST/Dependency/Test 결과는
    # 실제로 계산은 하되(Aggregator/중복 비교용) LLM 프롬프트에는 전달하지
    # 않는다(별도 변수로 격리, review_validator에는 ctx만 전달됨).
    deterministic_results = [
        structure_validator(ctx),
        scope_validator(ctx),
        ast_validator(ctx),
        dependency_validator(ctx),
    ]
    deterministic_review_findings = _deterministic_findings(ctx.implementation)

    runs = []
    for i in range(1, RUN_COUNT + 1):
        result = _run_once(ctx, engine_call, i)
        if result["success"]:
            result["finding_count_auto"] = _count_findings_in_prose(result["raw_response"])
        runs.append(result)

    # Aggregator 재확인 — Review 실행 결과와 무관하게 deterministic Verdict가
    # 동일해야 한다(Test는 이번 실험 범위 밖이므로 PASS로 고정 주입해 Verdict
    # 계산 로직 자체만 검증한다 — 실제 Test 실행은 latency 비교용으로 별도
    # 인용, 이 스크립트가 재실행하지 않음).
    fixed_test_result = ValidatorResult("test", "PASS", 0.0, {"note": "이 실험 범위 밖, 별도 latency 인용"})
    verdicts = []
    for run in runs:
        if run["success"]:
            review_status = "PASS"  # LLM raw response 자체를 PASS/FAIL로 자동 판정하지 않음(Policy 구현 금지)
        else:
            review_status = "ERROR"
        review_result = ValidatorResult("review", review_status, run.get("total_latency_ms") or 0.0, {"mode": "llm"})
        agg = aggregate(deterministic_results + [fixed_test_result, review_result])
        verdicts.append(agg.verdict)

    return {
        "model": MODEL,
        "run_count": RUN_COUNT,
        "deterministic_results": {r.validator_id: r.status for r in deterministic_results},
        "deterministic_review_findings": deterministic_review_findings,
        "runs": runs,
        "final_verdicts_per_run": verdicts,
        "verdict_unchanged_by_review": len(set(verdicts)) == 1,
    }


if __name__ == "__main__":
    output = main()
    # raw_response는 별도 파일로 저장(사람이 읽는 Evidence 본문용), stdout에는 요약만.
    with open("/tmp/review_llm_real_execution_full.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    summary = {k: v for k, v in output.items() if k != "runs"}
    summary["runs_summary"] = [
        {
            "run": r["run"],
            "success": r["success"],
            "total_latency_ms": r.get("total_latency_ms"),
            "api_latency_ms": r.get("api_latency_ms"),
            "finding_count_auto": r.get("finding_count_auto"),
            "attempts": len(r["attempts"]),
        }
        for r in output["runs"]
    ]
    print(json.dumps(summary, indent=2, ensure_ascii=False))

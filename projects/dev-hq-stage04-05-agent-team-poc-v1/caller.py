"""Stage 04/05 Agent Team 격리 재현 — 상위 흐름(caller).

새 Runtime API·Event Bus·Message Contract를 만들지 않는다. Stage 04는
직접 함수 호출 순차 체인(`hqs/development/workflow.py`와 동형), Stage
05의 병렬은 표준 라이브러리 `ThreadPoolExecutor`만 쓴다(`hqs/investment/
teams/stock_team.py`, Phase E `multi-agent-handoff-mvp-v1/caller.py`와
동일 패턴 재사용). 실패는 예외가 아닌 값으로 전파한다.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from domain.agents import (
    implementation_agent,
    qa_agent,
    review_agent,
    target_identification_agent,
)
from domain.checks import check_structural, check_syntax, determine_verdict


# ---- Stage 04: 순차 Handoff ----


def run_stage04_pipeline(
    design: str, candidate_index: str, *, fail_target: bool = False, fail_impl: bool = False
) -> dict:
    """Target Identification -> Implementation. 실패 시 즉시 단축(값 기반)."""
    target_result = target_identification_agent(design, candidate_index, fail=fail_target)
    if target_result["status"] != "ok":
        return {"status": "error", "failed_at": "target_identification", "detail": target_result}

    impl_result = implementation_agent(design, target_result["target"], fail=fail_impl)
    if impl_result["status"] != "ok":
        return {
            "status": "error",
            "failed_at": "implementation",
            "detail": impl_result,
            "target": target_result,  # 부분 재실행을 위해 성공한 상류 결과를 보존
        }

    return {"status": "ok", "target": target_result, "implementation": impl_result}


def retry_stage04_implementation_only(design: str, cached_target_result: dict, *, fail_impl: bool = False) -> dict:
    """부분 재실행 — Target Identification을 다시 실행하지 않고 캐시된
    성공 결과를 재사용해 Implementation만 재시도한다."""
    impl_result = implementation_agent(design, cached_target_result["target"], fail=fail_impl)
    if impl_result["status"] != "ok":
        return {"status": "error", "failed_at": "implementation", "detail": impl_result}
    return {"status": "ok", "target": cached_target_result, "implementation": impl_result}


# ---- Stage 05: 독립 병렬 + 결정적 종합 ----


def run_stage05_pipeline(
    implementation_code: str, *, fail_review: bool = False, fail_qa: bool = False
) -> dict:
    """Review Agent ∥ QA Agent(ThreadPoolExecutor) -> deterministic Aggregator(Verdict).
    두 Agent는 서로의 결과에 의존하지 않으므로 동시 실행한다."""
    impl_dict = {"status": "ok", "code": implementation_code}

    with ThreadPoolExecutor(max_workers=2) as pool:
        review_future = pool.submit(review_agent, implementation_code, fail=fail_review)
        qa_future = pool.submit(qa_agent, implementation_code, fail=fail_qa)
        review_result = review_future.result()
        qa_result = qa_future.result()

    structural = check_structural(impl_dict)
    syntax = check_syntax(implementation_code)
    verdict = determine_verdict(structural, syntax)

    return {
        "verdict": verdict,
        "checks": {"structural": structural, "syntax": syntax},
        "review": review_result,
        "qa": qa_result,
    }


def retry_stage05_agent_only(
    implementation_code: str, cached_result: dict, *, agent: str, fail: bool = False
) -> dict:
    """부분 재실행 — 실패한 Agent 하나만 재시도하고, 성공했던 다른
    Agent의 결과는 캐시에서 재사용한다. Verdict는 재종합한다."""
    if agent == "review":
        review_result = review_agent(implementation_code, fail=fail)
        qa_result = cached_result["qa"]
    elif agent == "qa":
        review_result = cached_result["review"]
        qa_result = qa_agent(implementation_code, fail=fail)
    else:
        raise ValueError(f"unknown agent: {agent}")

    return {
        "verdict": cached_result["verdict"],  # 결정적 검사만 Verdict에 반영 — Agent 재시도가 Verdict를 바꾸지 않음
        "checks": cached_result["checks"],
        "review": review_result,
        "qa": qa_result,
    }

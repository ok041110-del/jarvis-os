"""상위 흐름(caller) — Agent A -> Agent B 전달, 결과를 caller에게 반환.

병렬 시나리오(`run_parallel_independent_agents`)는 `hqs/investment/ teams/stock_team.py`가 이미 쓰는 `ThreadPoolExecutor` 직접 사용 패턴을 그대로 재현한다 — 새 동시성 추상화를 만들지 않는다.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from domain.agents import run_drafter, run_reviewer


def run_sequential_handoff(topic: str, *, fail_drafter: bool = False, fail_reviewer: bool = False) -> dict:
    draft_result = run_drafter(topic, fail=fail_drafter)
    if draft_result["status"] != "ok":
        return {"status": "error", "failed_at": "drafter", "detail": draft_result}

    review_result = run_reviewer(draft_result, fail=fail_reviewer)
    if review_result["status"] != "ok":
        return {"status": "error", "failed_at": "reviewer", "detail": review_result}

    return {
        "status": "ok",
        "draft": draft_result["draft"],
        "review": review_result["review"],
    }


def run_parallel_independent_agents(topics: list[str]) -> list[dict]:
    """독립적인 Drafter 여러 인스턴스를 동시 실행 — Multi-Task 범위 재확인을 위한 관찰용."""
    with ThreadPoolExecutor(max_workers=len(topics)) as pool:
        results = list(pool.map(run_drafter, topics))
    return results

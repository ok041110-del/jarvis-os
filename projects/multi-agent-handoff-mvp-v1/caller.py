"""상위 흐름(caller) — Agent A -> Agent B 전달, 결과를 caller에게 반환.

이 파일은 새 일반화된 Runtime API를 만들지 않는다 — 직접 함수 호출
(`hqs/development/workflow.py`의 Stage 01->05 패턴과 동형)만 쓴다.
Task 배분을 결정하는 코드(Scheduler)나 Agent를 동적으로 선택하는 코드는
없다 — 어느 Agent가 어떤 순서로 실행되는지는 이 파일에 고정되어 있다.

병렬 시나리오(`run_parallel_independent_agents`)는 `hqs/investment/
teams/stock_team.py`가 이미 쓰는 `ThreadPoolExecutor` 직접 사용 패턴을
그대로 재현한다 — 새 동시성 추상화를 만들지 않는다.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from domain.agents import run_drafter, run_reviewer


def run_sequential_handoff(topic: str, *, fail_drafter: bool = False, fail_reviewer: bool = False) -> dict:
    """Agent A(drafter) -> Agent B(reviewer) 순차 전달, 실패 시 즉시 반환(값 기반)."""
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
    """독립적인 Drafter 여러 인스턴스를 동시 실행 — 관찰용(§16.4 Multi-Task
    범위 재확인). 각 결과는 서로 입력 독립·출력 비의존이다."""
    with ThreadPoolExecutor(max_workers=len(topics)) as pool:
        results = list(pool.map(run_drafter, topics))
    return results

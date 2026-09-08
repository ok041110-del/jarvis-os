"""LangGraph Conditional Routing Prototype — MVP-0002 대응 (State/Node/
Conditional Edge만 사용, Loop/Checkpoint는 다루지 않음 — README 참고).

이 파일은 Development HQ v2.0 Baseline을 수정하지 않는다. 실제 프로덕션
Capability(`backend_agent_code_review`/`qa_agent_test_execution`)를
읽기 전용으로 import해 그대로 재사용하며, 그 위의 분기 배선만 LangGraph로
구현한다.
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from hqs.development.mvp.agents.backend import (
    NO_ISSUES_MARKER,
    backend_agent_code_review,
)
from hqs.development.mvp.agents.qa import qa_agent_test_execution


class ReviewState(TypedDict):
    code: str
    review: str
    test_cases: str


def code_review_node(state: ReviewState) -> dict:
    return {"review": backend_agent_code_review(state["code"])}


def route_after_review(state: ReviewState) -> str:
    if NO_ISSUES_MARKER in state["review"]:
        return "finalize"
    return "test_execution"


def test_execution_node(state: ReviewState) -> dict:
    test_cases = qa_agent_test_execution(state["code"], state["review"])
    return {"test_cases": test_cases}


def finalize_node(state: ReviewState) -> dict:
    return {
        "test_cases": (
            "(생략됨: code_review에서 이슈가 발견되지 않아 "
            "test_execution을 건너뜀)"
        )
    }


def _strip_trailing_marker(review: str) -> str:
    """`run_mvp_0002`와 동일한 반환 계약(marker 제거)을 맞춘다 —
    비교 공정성을 위해 baseline과 같은 후처리를 적용한다."""
    lines = review.rstrip().splitlines()
    if lines and lines[-1].strip() == NO_ISSUES_MARKER:
        return "\n".join(lines[:-1]).rstrip()
    return review


def build_graph():
    graph = StateGraph(ReviewState)
    graph.add_node("code_review", code_review_node)
    graph.add_node("test_execution", test_execution_node)
    graph.add_node("finalize", finalize_node)
    graph.add_edge(START, "code_review")
    graph.add_conditional_edges(
        "code_review",
        route_after_review,
        {"test_execution": "test_execution", "finalize": "finalize"},
    )
    graph.add_edge("test_execution", END)
    graph.add_edge("finalize", END)
    return graph.compile()


def run_via_langgraph(code: str) -> dict:
    """`run_mvp_0002(code)`와 동일한 반환 계약(`{code_review, test_execution}`)을
    유지한다 — 비교를 위해 키 이름까지 맞춘다."""
    app = build_graph()
    try:
        result = app.invoke({"code": code, "review": "", "test_cases": ""})
    except Exception as exc:  # noqa: BLE001 — baseline과 동일한 실패 처리 대칭
        error_message = f"Engine call failed: {exc}"
        return {"code_review": error_message, "test_execution": error_message}
    return {
        "code_review": _strip_trailing_marker(result["review"]),
        "test_execution": result["test_cases"],
    }

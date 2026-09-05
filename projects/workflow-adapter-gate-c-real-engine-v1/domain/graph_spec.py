"""HQ가 '정의'하는 그래프 구조 — adapter-agnostic 데이터. langgraph 무의존.

실행 로직은 없다. 두 어댑터(sequential / langgraph)가 이 선언을 읽어
각자의 방식으로 배선한다. phase 경계(PHASE1_END)는 이 PoC의 fixture 선택이며
Governance 선언(ADC-0020 §Q-E-2 Defer)이 아니다.
"""
from __future__ import annotations

from domain import nodes

ENTRY = "dispatch"
PARALLEL_GROUP = (
    "analyst_fundamental",
    "analyst_technical",
    "analyst_industry",
    "analyst_news_event",
    "analyst_sentiment",
)
FAN_IN = "collect"
PHASE1_END = "collect"  # phase 경계: collect fan-in 직후 (E3 §6-a와 동일)

DEBATE_SEQUENCE = ("bull_case", "bear_case", "judge")
TERMINAL = ("final_report", "escalate_data_gap")

REDUCER_KEYS = ("data_flags", "debate_log")

NODE_FUNCS = {
    name: getattr(nodes, name)
    for name in (
        ENTRY,
        *PARALLEL_GROUP,
        FAN_IN,
        *DEBATE_SEQUENCE,
        "trader",
        *TERMINAL,
    )
}


def debate_should_loop(state: dict) -> str:
    return "advance" if state.get("converged") else "loop"


def route_after_decision(state: dict) -> str:
    decision = state.get("decision", {})
    inconsistent = any(str(f).startswith("INCONSISTENT") for f in state.get("data_flags", []))
    if decision.get("action") == "HOLD" and inconsistent:
        return "escalate"
    return "report"


PREDICATES = {
    "debate_should_loop": debate_should_loop,
    "route_after_decision": route_after_decision,
}

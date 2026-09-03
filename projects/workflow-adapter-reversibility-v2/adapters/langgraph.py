"""LangGraph 대조 Adapter — Reversibility 대조 Evidence용.

이것은 LangGraph 채택이 아니다(ADC-0021 §D2). E1/E2/E3와 동일하게 교체
가능한 구현체 후보 하나로만 인용된다. `langgraph` import는 이 저장소에서
이 파일 한 곳에만 존재한다.

노드 예외의 catch-and-encode는 LangGraph의 보장이 아니라 어댑터의 책임이다
(ADC-0020 §Q-D (b), E3 §6-b) — 아래 `_wrap`이 그 책임을 수행한다.
"""
from __future__ import annotations

import copy
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from domain import graph_spec as G

NAME = "langgraph"

# reducer 키만 Annotated[list, operator.add], 나머지는 last-write-wins.
# domain.state.WorkflowState의 미러 — 명시적으로 둬서 stringized annotation 의존 제거.
_SCHEMA = TypedDict(
    "LangGraphWorkflowState",
    {
        "ticker": str,
        "scenario": str,
        "fundamental": dict,
        "technical": dict,
        "industry": dict,
        "news_event": dict,
        "sentiment": dict,
        "bull": dict,
        "bear": dict,
        "debate_round": int,
        "converged": bool,
        "decision": dict,
        "final_report": dict,
        "outcome": str,
        "escalation": dict,
        "data_flags": Annotated[list, operator.add],
        "debate_log": Annotated[list, operator.add],
    },
    total=False,
)


def _wrap(name: str):
    func = G.NODE_FUNCS[name]

    def node(state: dict) -> dict:
        try:
            return func(dict(state))
        except Exception as exc:  # 예외 -> State 값 (어댑터 책임)
            return {"data_flags": [f"NODE_ERROR:{name}:{type(exc).__name__}"]}

    node.__name__ = name
    return node


def _add_nodes(graph: StateGraph, names) -> None:
    for name in names:
        graph.add_node(name, _wrap(name))


def _debate_router(state: dict) -> str:
    return G.PREDICATES["debate_should_loop"](state)


def _decision_router(state: dict) -> str:
    return G.PREDICATES["route_after_decision"](state)


def _wire_debate_and_routing(graph: StateGraph) -> None:
    graph.add_edge("bull_case", "bear_case")
    graph.add_edge("bear_case", "judge")
    graph.add_conditional_edges("judge", _debate_router, {"loop": "bull_case", "advance": "trader"})
    graph.add_conditional_edges(
        "trader", _decision_router, {"escalate": "escalate_data_gap", "report": "final_report"}
    )
    graph.add_edge("final_report", END)
    graph.add_edge("escalate_data_gap", END)


def _compile_full():
    graph = StateGraph(_SCHEMA)
    _add_nodes(graph, [G.ENTRY, *G.PARALLEL_GROUP, G.FAN_IN, *G.DEBATE_SEQUENCE, "trader", *G.TERMINAL])
    graph.add_edge(START, G.ENTRY)
    for name in G.PARALLEL_GROUP:
        graph.add_edge(G.ENTRY, name)
        graph.add_edge(name, G.FAN_IN)
    graph.add_edge(G.FAN_IN, "bull_case")
    _wire_debate_and_routing(graph)
    return graph.compile()


def _compile_phase1():
    graph = StateGraph(_SCHEMA)
    _add_nodes(graph, [G.ENTRY, *G.PARALLEL_GROUP, G.FAN_IN])
    graph.add_edge(START, G.ENTRY)
    for name in G.PARALLEL_GROUP:
        graph.add_edge(G.ENTRY, name)
        graph.add_edge(name, G.FAN_IN)
    graph.add_edge(G.FAN_IN, END)
    return graph.compile()


def _compile_phase2():
    graph = StateGraph(_SCHEMA)
    _add_nodes(graph, [*G.DEBATE_SEQUENCE, "trader", *G.TERMINAL])
    graph.add_edge(START, "bull_case")
    _wire_debate_and_routing(graph)
    return graph.compile()


def _plain(result) -> dict:
    return {k: v for k, v in dict(result).items()}


def run_full(inputs: dict) -> dict:
    return _plain(_compile_full().invoke(copy.deepcopy(inputs)))


def run_phase1(inputs: dict) -> dict:
    return _plain(_compile_phase1().invoke(copy.deepcopy(inputs)))


def run_phase2(checkpoint_value: dict) -> dict:
    return _plain(_compile_phase2().invoke(copy.deepcopy(checkpoint_value)))

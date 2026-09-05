"""Sequential Reference Adapter — §16.6 "최소한으로는 순차 함수 호출"의 지정 형태.

외부 의존 0. 조건부 = if/elif, Loop = while, 병렬 = ThreadPoolExecutor,
reducer = 명시적 merge. 노드 예외의 catch-and-encode는 어댑터 책임
(ADC-0020 §Q-D (b)).
"""
from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor

from domain import graph_spec as G

NAME = "sequential"
_REDUCER_KEYS = G.REDUCER_KEYS


def _merge(base: dict, update: dict) -> None:
    for key, value in update.items():
        if key in _REDUCER_KEYS and isinstance(value, list):
            base[key] = list(base.get(key, [])) + list(value)
        else:
            base[key] = value


def _run_node(name: str, state: dict):
    func = G.NODE_FUNCS[name]
    try:
        return func(copy.deepcopy(state)), None
    except Exception as exc:  # catch-and-encode — 예외를 State 값으로
        return {}, f"NODE_ERROR:{name}:{type(exc).__name__}"


def _apply(state: dict, name: str) -> None:
    update, err = _run_node(name, state)
    _merge(state, update)
    if err:
        state.setdefault("data_flags", []).append(err)


def _phase1(state: dict) -> None:
    _apply(state, G.ENTRY)
    # 병렬 fan-out — 결정론적 병합 순서(노드명 정렬)
    with ThreadPoolExecutor(max_workers=len(G.PARALLEL_GROUP)) as pool:
        futures = {name: pool.submit(_run_node, name, state) for name in G.PARALLEL_GROUP}
        for name in sorted(futures):
            update, err = futures[name].result()
            _merge(state, update)
            if err:
                state.setdefault("data_flags", []).append(err)
    _apply(state, G.FAN_IN)


def _phase2(state: dict) -> None:
    while True:
        for name in G.DEBATE_SEQUENCE:
            _apply(state, name)
        if G.PREDICATES["debate_should_loop"](state) == "advance":
            break
    _apply(state, "trader")
    route = G.PREDICATES["route_after_decision"](state)
    terminal = "escalate_data_gap" if route == "escalate" else "final_report"
    _apply(state, terminal)


def run_full(inputs: dict) -> dict:
    state = copy.deepcopy(inputs)
    _phase1(state)
    _phase2(state)
    return state


def run_phase1(inputs: dict) -> dict:
    state = copy.deepcopy(inputs)
    _phase1(state)
    return state


def run_phase2(checkpoint_value: dict) -> dict:
    state = copy.deepcopy(checkpoint_value)
    _phase2(state)
    return state

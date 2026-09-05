"""L-B — 재귀 조합자(Recursive Combinator) 그래프 실행기 (비-LangGraph 독립 계보, 2번째).

`ADC-0021` §8 Gate **(B)** — `ADC-0024` §D-B4가 완전 완화 후속조건 (i)로
이름 붙인 "2번째 비-LangGraph 독립 계보". `RFC-0020` §8.2 Q-I가 지목한
"직접 구현 최소 그래프 실행기"의 또 다른 형태.

## 실행 모델 (독립성 명문화)

이 어댑터는 `domain.graph_spec` 선언을 **재귀 함수 호출로 직접 걷는다**.
`workflow-adapter-nonlanggraph-lineage-v1/adapters/worklist.py`(L-A)와
자료구조·제어 흐름 층위 모두에서 다르다:

- **L-A(worklist)와 다르다** — L-A는 `_Interpreter` **인스턴스**가
  `collections.deque` 큐 + `completed`/`pending`/`ready` **mutable
  속성**을 하나의 `while` 루프 안에서 계속 바꿔가며 진행한다. 수렴 Loop는
  `completed.discard(...)`로 **기존 집합 객체를 in-place mutate**해
  재실행 대상을 되돌린다. 이 어댑터는 그런 인스턴스도 큐도 **없다** —
  진행은 `_advance()` **순수 재귀 호출**이며, "무엇이 끝났는가"는 매
  호출마다 **새로 만들어지는 `frozenset`**을 인자/반환값으로 주고받는
  것으로 표현한다. 수렴 Loop는 `visited - _DEBATE`로 **새 frozenset을
  만들어 다음 재귀 프레임에 넘기는 것**으로 재현한다 — 어떤 기존 객체도
  mutate하지 않는다. State 자체도 매 노드 적용마다 **새 dict**로 갱신된다
  (`_apply`가 `dict(state)` 복사 후 반환 — 하나의 dict를 계속 mutate하는
  L-A와 다르다).
- **`adapters/langgraph.py`와 다르다** — LangGraph는 `StateGraph.compile()`
  + Pregel 계열 superstep 엔진. 이 어댑터는 컴파일 단계도, superstep도,
  외부 그래프 런타임도 없다.
- **E4 `sequential.py`와 다르다** — sequential은 실행 순서가 소스에
  하드코딩된 절차다. 이 어댑터는 `graph_spec`을 런타임에 읽어 후속 노드를
  계산한다(이 점은 L-A와 같다 — 둘 다 데이터-구동, 그 위에서 스케줄링
  메커니즘만 다르다).

## 의존

표준 라이브러리(`copy`)와 `domain.graph_spec`만 import한다.
`langgraph`/`langchain`/그 외 서드파티 0. `worklist.py`/`sequential.py`도
import하지 않는다(계보 상호 독립 — 공유는 `domain/*`뿐). `class` 정의와
`collections` import가 없다 — 인터프리터 인스턴스·큐 자료구조를 두지
않는다는 것을 소스 구조 자체로 강제한다(IN-6' 검사 대상).

## Adapter 책임

- 노드 예외의 catch-and-encode는 이 어댑터의 책임이다(`ADC-0020` §Q-D (b))
  — 예외를 `NODE_ERROR:{node}:{ExcType}` State 값으로 인코딩하고 경계 밖으로
  전파하지 않는다.
- reducer 키(`data_flags`, `debate_log`)는 명시적 append merge로 재현한다.
- Checkpoint 값은 **생산**만 한다 — 영속화·복원은 caller의 몫(`caller.py`).
  phase2 재개는 이전 재귀 호출 스택을 전혀 복원하지 않고, 순수 도메인
  State 값만으로 **완전히 새로운 재귀 호출**을 시작한다.
"""
from __future__ import annotations

import copy

from domain import graph_spec as G

NAME = "recursive"

_REDUCER_KEYS = frozenset(G.REDUCER_KEYS)

# 정적 edge 표 — graph_spec 선언에서 파생한다(하드코딩된 실행 순서가 아니다).
# L-A(worklist.py)와 동일한 데이터 파생이지만, 이를 걷는 방식(_advance)만 다르다.
_STATIC_SUCC: dict[str, tuple[str, ...]] = {}
_STATIC_SUCC[G.ENTRY] = tuple(G.PARALLEL_GROUP)
for _n in G.PARALLEL_GROUP:
    _STATIC_SUCC[_n] = (G.FAN_IN,)
_STATIC_SUCC[G.FAN_IN] = (G.DEBATE_SEQUENCE[0],)
for _a, _b in zip(G.DEBATE_SEQUENCE, G.DEBATE_SEQUENCE[1:]):
    _STATIC_SUCC[_a] = (_b,)
for _t in G.TERMINAL:
    _STATIC_SUCC[_t] = ()

_PREDS: dict[str, frozenset[str]] = {name: frozenset() for name in G.NODE_FUNCS}
for _src, _dsts in _STATIC_SUCC.items():
    for _d in _dsts:
        _PREDS[_d] = _PREDS.get(_d, frozenset()) | {_src}
# 조건부 도착지(trader, judge의 loop 대상)의 predecessor는 런타임에 직접
# 재귀 호출로만 도달하므로 정적 집합에 넣지 않는다(L-A와 동일 판단).

_DEBATE = frozenset(G.DEBATE_SEQUENCE)
_JUDGE = G.DEBATE_SEQUENCE[-1]


def _merge(base: dict, update: dict) -> dict:
    merged = dict(base)
    for key, value in update.items():
        if key in _REDUCER_KEYS and isinstance(value, list):
            merged[key] = list(merged.get(key, [])) + list(value)
        else:
            merged[key] = value
    return merged


def _apply(name: str, state: dict) -> dict:
    """노드를 적용해 **새 State dict**를 반환한다 — 기존 dict는 mutate하지 않는다."""
    func = G.NODE_FUNCS[name]
    try:
        update = func(copy.deepcopy(state))
    except Exception as exc:  # noqa: BLE001 — 예외 -> State 값 (어댑터 책임)
        new_state = dict(state)
        new_state["data_flags"] = list(new_state.get("data_flags", [])) + [
            f"NODE_ERROR:{name}:{type(exc).__name__}"
        ]
        return new_state
    return _merge(state, update)


def _advance(
    name: str,
    state: dict,
    visited: frozenset,
    depth: int,
    stop_after: str | None,
    starts: frozenset,
) -> tuple[dict, frozenset, int, bool]:
    """`name`을 재귀적으로 실행한다. 반환: (state, visited, max_depth, stopped).

    `starts`는 이 `_run` 호출의 명시적 시작 노드 집합이다 — `name in starts`인
    동안은 predecessor 검사를 생략한다. 이는 **매 호출마다** 적용된다(최초
    진입 1회만이 아니다) — L-A `_Interpreter.self.start`가 인스턴스 생애
    전체에 걸쳐 매 pop마다 검사되는 것과 동일한 의미다. 이게 필요한 이유:
    수렴 Loop의 재진입(`bull_case`로 되돌아가는 매 라운드)이 phase2
    재개처럼 "이 `_run` 호출 안에서 predecessor 없이 재개 가능한 지점"이기
    때문이다 — `visited`가 실제 predecessor(`collect`)를 담고 있는지 여부와
    무관하게, 이 이름이 애초에 시작점으로 지정됐다면 항상 재진입 가능해야
    한다.
    """
    if name in visited:
        return state, visited, depth, False
    preds = _PREDS.get(name, frozenset())
    if name not in starts and not (preds <= visited):
        return state, visited, depth, False  # 아직 실행 불가 — 다른 재귀 경로가 채운다

    state = _apply(name, state)
    visited = visited | {name}

    if name == stop_after:
        return state, visited, depth, True

    if name == _JUDGE:
        route = G.PREDICATES["debate_should_loop"](state)  # "loop" | "advance"
        if route == "loop":
            # 수렴 Loop — 기존 visited를 mutate하지 않고 새 frozenset을 만들어
            # 다음 재귀 프레임(새 토론 라운드)에 넘긴다.
            resumed_visited = visited - _DEBATE
            return _advance(G.DEBATE_SEQUENCE[0], state, resumed_visited, depth + 1, stop_after, starts)
        succ: tuple[str, ...] = ("trader",)
    elif name == "trader":
        route = G.PREDICATES["route_after_decision"](state)  # "escalate" | "report"
        succ = ("escalate_data_gap",) if route == "escalate" else ("final_report",)
    else:
        succ = _STATIC_SUCC.get(name, ())

    max_depth = depth
    for nxt in succ:
        state, visited, sub_depth, stopped = _advance(nxt, state, visited, depth + 1, stop_after, starts)
        max_depth = max(max_depth, sub_depth)
        if stopped:
            return state, visited, max_depth, True
    return state, visited, max_depth, False


def _run(state: dict, start_nodes: tuple[str, ...], stop_after: str | None) -> tuple[dict, int]:
    state = copy.deepcopy(state)
    visited: frozenset = frozenset()
    starts = frozenset(start_nodes)
    max_depth = 0
    for start in start_nodes:
        state, visited, depth, stopped = _advance(start, state, visited, 1, stop_after, starts)
        max_depth = max(max_depth, depth)
        if stopped:
            break
    return state, max_depth


def run_full(inputs: dict) -> dict:
    state, _ = _run(inputs, (G.ENTRY,), None)
    return state


def run_phase1(inputs: dict) -> dict:
    state, _ = _run(inputs, (G.ENTRY,), G.PHASE1_END)
    return state


def run_phase2(checkpoint_value: dict) -> dict:
    state, _ = _run(checkpoint_value, (G.DEBATE_SEQUENCE[0],), None)
    return state


def run_full_with_depth(inputs: dict) -> tuple[dict, int]:
    """계측 전용 — IN-6' 재귀 깊이 실측에서만 쓴다. `caller.py` 계약의 일부가 아니다."""
    return _run(inputs, (G.ENTRY,), None)

"""L-A — Worklist 그래프 인터프리터 (비-LangGraph 독립 계보).

`ADC-0021` §8 Gate **(B)** — `ADC-0019` 재검토 조건 (c)의 "LangGraph와
다른 계보" 관찰. `RFC-0020` §8.2 Q-I가 지목한 "직접 구현 최소 그래프
실행기"의 형태 하나.

## 실행 모델 (독립성 명문화)

이 어댑터는 `domain.graph_spec` 선언을 **데이터로 해석하는 ready-queue
worklist 인터프리터**다. 다음 두 계보와 구조적으로 구분된다:

- **E4 `adapters/sequential.py`와 다르다** — E4 sequential은 `_phase1()`·
  `_phase2()`에 **하드코딩된 절차**(고정된 함수 호출 순서, 명시적 `if/elif`,
  `while`)다. graph_spec의 edge 구조를 해석하지 않고 실행 순서를 소스에
  구워 넣는다. 이 어댑터는 그런 절차가 없다 — ENTRY에서 시작해 각 노드의
  후속 edge(정적 + 조건부 predicate 평가 결과)를 **런타임에** 계산해
  ready-queue에 넣고, 선행 노드가 모두 끝난 노드만 pop해 실행한다. 그래프
  형태가 바뀌면 이 파일은 수정 없이 새 `graph_spec`을 따른다.
- **`adapters/langgraph.py`와 다르다** — LangGraph는 `StateGraph`를
  `compile()`해 Pregel 계열 superstep 엔진으로 돌린다. 이 어댑터는
  컴파일 단계도, superstep 개념도, 외부 그래프 런타임도 없다 — 단일
  스레드 worklist 루프 + 명시적 predecessor 집합만으로 fan-out·fan-in·
  조건부 분기·수렴 Loop를 배선한다.

## 의존

표준 라이브러리(`collections.deque`, `copy`)와 `domain.graph_spec`만
import한다. `langgraph`/`langchain`/그 외 서드파티 0. `sequential.py`도
import하지 않는다(계보 상호 독립 — 공유는 `domain/*`뿐).

## Adapter 책임

- 노드 예외의 catch-and-encode는 이 어댑터의 책임이다(`ADC-0020` §Q-D (b))
  — 예외를 `NODE_ERROR:{node}:{ExcType}` State 값으로 인코딩하고 경계 밖으로
  전파하지 않는다.
- reducer 키(`data_flags`, `debate_log`)는 명시적 append merge로 재현한다.
- Checkpoint 값은 **생산**만 한다 — 영속화·복원은 caller의 몫(`caller.py`).
"""
from __future__ import annotations

import copy
from collections import deque

from domain import graph_spec as G

NAME = "worklist"

_REDUCER_KEYS = frozenset(G.REDUCER_KEYS)

# 정적 edge 표 — graph_spec 선언에서 파생한다(하드코딩된 실행 순서가 아니다).
#   START -> ENTRY
#   ENTRY -> 각 PARALLEL_GROUP 노드
#   각 PARALLEL_GROUP 노드 -> FAN_IN
#   FAN_IN -> DEBATE_SEQUENCE[0]
#   DEBATE_SEQUENCE 체인 (bull -> bear -> judge)
#   judge -> (조건부: debate_should_loop)
#   trader -> (조건부: route_after_decision)
#   TERMINAL -> END
_STATIC_SUCC: dict[str, tuple[str, ...]] = {}
_STATIC_SUCC[G.ENTRY] = tuple(G.PARALLEL_GROUP)
for _n in G.PARALLEL_GROUP:
    _STATIC_SUCC[_n] = (G.FAN_IN,)
_STATIC_SUCC[G.FAN_IN] = (G.DEBATE_SEQUENCE[0],)
for _a, _b in zip(G.DEBATE_SEQUENCE, G.DEBATE_SEQUENCE[1:]):
    _STATIC_SUCC[_a] = (_b,)
# DEBATE_SEQUENCE[-1] (judge) 와 trader 는 조건부 — _STATIC_SUCC 에 두지 않는다.
for _t in G.TERMINAL:
    _STATIC_SUCC[_t] = ()

# predecessor 집합 — 정적 edge 역방향.
_PREDS: dict[str, set[str]] = {name: set() for name in G.NODE_FUNCS}
for _src, _dsts in _STATIC_SUCC.items():
    for _d in _dsts:
        _PREDS.setdefault(_d, set()).add(_src)
# 조건부 도착지의 predecessor 는 런타임 재개용으로만 쓰이므로 정적 집합에
# 넣지 않는다(judge/trader 가 그때그때 enqueue 한다).

_DEBATE = frozenset(G.DEBATE_SEQUENCE)
_JUDGE = G.DEBATE_SEQUENCE[-1]


def _merge(base: dict, update: dict) -> None:
    for key, value in update.items():
        if key in _REDUCER_KEYS and isinstance(value, list):
            base[key] = list(base.get(key, [])) + list(value)
        else:
            base[key] = value


def _run_node(name: str, state: dict) -> tuple[dict, str | None]:
    func = G.NODE_FUNCS[name]
    try:
        return func(copy.deepcopy(state)), None
    except Exception as exc:  # noqa: BLE001 — 예외 -> State 값 (어댑터 책임)
        return {}, f"NODE_ERROR:{name}:{type(exc).__name__}"


class _Interpreter:
    """단일 실행. start_nodes 에서 시작해 stop_after(포함) 에서 멈춘다."""

    def __init__(self, state: dict, start_nodes: tuple[str, ...], stop_after: str | None):
        self.state = state
        self.start = set(start_nodes)
        self.stop_after = stop_after
        self.completed: set[str] = set()
        self.pending: set[str] = set(start_nodes)
        self.ready: deque[str] = deque(start_nodes)

    def _apply(self, name: str) -> None:
        update, err = _run_node(name, self.state)
        _merge(self.state, update)
        if err is not None:
            self.state.setdefault("data_flags", []).append(err)
        self.completed.add(name)

    def _enqueue(self, name: str) -> None:
        if name not in self.completed and name not in self.pending:
            self.pending.add(name)
            self.ready.append(name)

    def _successors(self, name: str) -> tuple[str, ...]:
        if name == _JUDGE:
            route = G.PREDICATES["debate_should_loop"](self.state)  # "loop" | "advance"
            if route == "loop":
                # 토론 하위 영역을 미완료로 되돌려 재실행 (수렴 Loop).
                for n in G.DEBATE_SEQUENCE:
                    self.completed.discard(n)
                return (G.DEBATE_SEQUENCE[0],)
            return ("trader",)
        if name == "trader":
            route = G.PREDICATES["route_after_decision"](self.state)  # "escalate" | "report"
            return ("escalate_data_gap",) if route == "escalate" else ("final_report",)
        return _STATIC_SUCC.get(name, ())

    def _runnable(self, name: str) -> bool:
        if name in self.start:
            return True
        return _PREDS.get(name, set()) <= self.completed

    def run(self) -> dict:
        while self.ready:
            name = self.ready.popleft()
            self.pending.discard(name)
            if name in self.completed:
                continue
            if not self._runnable(name):
                # 마지막 선행 노드가 끝나면 그쪽에서 다시 enqueue 된다.
                continue
            self._apply(name)
            if name == self.stop_after:
                return self.state
            for succ in self._successors(name):
                self._enqueue(succ)
        return self.state


def _run(state: dict, start_nodes: tuple[str, ...], stop_after: str | None) -> dict:
    return _Interpreter(copy.deepcopy(state), start_nodes, stop_after).run()


def run_full(inputs: dict) -> dict:
    return _run(inputs, (G.ENTRY,), None)


def run_phase1(inputs: dict) -> dict:
    return _run(inputs, (G.ENTRY,), G.PHASE1_END)


def run_phase2(checkpoint_value: dict) -> dict:
    return _run(checkpoint_value, (G.DEBATE_SEQUENCE[0],), None)

"""시나리오 fixture — 전부 결정론적. langgraph 무의존.

- clean:      정합 데이터 -> 3라운드 수렴 -> BUY  -> final_report      -> COMPLETED
- data_gap:   sentiment 소스 충돌 -> 3라운드 수렴 -> HOLD -> escalate  -> ESCALATED_DATA_GAP
- node_error: analyst_fundamental 노드가 예외 raise (IN-2 catch-and-encode 검증),
              나머지는 clean과 동일 -> COMPLETED (+ data_flags에 NODE_ERROR 기록)
"""
from __future__ import annotations

SCENARIOS = {
    "clean": {"ticker": "TESTCO", "sentiment_conflict": False, "raise_in": None},
    "data_gap": {"ticker": "TESTCO", "sentiment_conflict": True, "raise_in": None},
    "node_error": {"ticker": "TESTCO", "sentiment_conflict": False, "raise_in": "analyst_fundamental"},
}


def scenario_config(name: str) -> dict:
    return SCENARIOS[name]

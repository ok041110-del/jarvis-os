"""Workflow Adapter Reversibility v2 PoC — 도메인 State 스키마.

이 모듈은 langgraph를 import하지 않는다. State는 평문 dict로 표현되며
JSON round-trip이 가능해야 한다(caller-owned checkpoint 값 소유 모델 검증).
"""
from __future__ import annotations

import json
from typing import TypedDict

# 분석가별 disjoint 섹션 키 — 각 분석가는 자기 섹션만 쓴다.
SECTION_KEYS = ("fundamental", "technical", "industry", "news_event", "sentiment")

# fan-in 시 append 누적되는 키. 순차 어댑터는 명시적 merge로,
# LangGraph 어댑터는 reducer(Annotated[list, operator.add])로 재현한다.
REDUCER_KEYS = ("data_flags", "debate_log")


class WorkflowState(TypedDict, total=False):
    ticker: str
    scenario: str
    fundamental: dict
    technical: dict
    industry: dict
    news_event: dict
    sentiment: dict
    data_flags: list
    debate_log: list
    bull: dict
    bear: dict
    debate_round: int
    converged: bool
    decision: dict
    final_report: dict
    outcome: str
    escalation: dict


def new_state(ticker: str, scenario: str) -> dict:
    return {
        "ticker": ticker,
        "scenario": scenario,
        "data_flags": [],
        "debate_log": [],
        "debate_round": 0,
        "converged": False,
    }


def json_roundtrip_ok(value) -> bool:
    try:
        return json.loads(json.dumps(value)) == value
    except (TypeError, ValueError):
        return False


def only_plain_types(value) -> bool:
    """State 값에 라이브러리 타입이 누출되지 않았는지 확인."""
    if isinstance(value, dict):
        return all(isinstance(k, str) and only_plain_types(v) for k, v in value.items())
    if isinstance(value, list):
        return all(only_plain_types(v) for v in value)
    return value is None or isinstance(value, (str, int, float, bool))

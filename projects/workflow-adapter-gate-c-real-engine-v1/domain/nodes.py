"""도메인 노드 13개 — Gate C(i) 실험 전용. langgraph 무의존.

`analyst_sentiment` **한 노드만** 실제 Engine 호출(engine_cache 경유)로
대체됐다. 나머지 12개 노드는 E4/E5/E6과 동일한 결정론적 fixture다.

의미 출처: hqs/investment/teams/stock_team.py(Wave 병렬 구조),
hqs/investment/trader.py(REPORT/DECISION 분리). 참조만 — import·수정 없음.
각 노드는 partial State 업데이트(dict)를 반환한다.
"""
from __future__ import annotations

from domain import engine_cache
from domain.fixtures import scenario_config


def dispatch(state: dict) -> dict:
    return {"debate_log": [f"DISPATCH {state['ticker']}"]}


def analyst_fundamental(state: dict) -> dict:
    return {"fundamental": {"score": 0.7, "note": "stable margins"}}


def analyst_technical(state: dict) -> dict:
    return {"technical": {"score": 0.6, "note": "uptrend intact"}}


def analyst_industry(state: dict) -> dict:
    return {"industry": {"score": 0.55, "note": "sector neutral"}}


def analyst_news_event(state: dict) -> dict:
    return {"news_event": {"score": 0.5, "note": "no material events"}}


def analyst_sentiment(state: dict) -> dict:
    """Gate C(i) 실험 대상 노드 — 실제 Engine 호출(engine_cache 경유).

    조건부 분기(conflict 여부)는 시나리오 설정이 그대로 결정한다(업무
    분기의 재현성 유지 목적). 실제 Engine 텍스트는 `engine_note` 값으로만
    실려 merge/checkpoint/어댑터 교체 전 구간을 관통한다. `engine_mode ==
    "raise"` 시나리오에서는 engine_cache에 미리 캡처된 **실제** 예외를
    재발생시킨다(catch-and-encode 검증용).
    """
    cfg = scenario_config(state["scenario"])
    if cfg["engine_mode"] == "raise":
        raise engine_cache.get_captured_exception(state["scenario"])
    text = engine_cache.get_captured(state["scenario"])
    conflict = cfg["sentiment_conflict"]
    result: dict = {
        "sentiment": {"score": 0.2 if conflict else 0.6, "sources": 2, "conflict": conflict, "engine_note": text}
    }
    if conflict:
        result["data_flags"] = ["INCONSISTENT:sentiment"]
    return result


def collect(state: dict) -> dict:
    present = sum(1 for k in ("fundamental", "technical", "industry", "news_event", "sentiment") if k in state)
    return {"debate_log": [f"COLLECT sections={present}"]}


def bull_case(state: dict) -> dict:
    r = state["debate_round"]
    return {"bull": {"round": r, "claim": f"bull point r{r}"}, "debate_log": [f"BULL r{r}"]}


def bear_case(state: dict) -> dict:
    r = state["debate_round"]
    new_points = 1 if r < 2 else 0  # bear가 r>=2 에서 새 논점 소진
    return {"bear": {"round": r, "new_points": new_points}, "debate_log": [f"BEAR r{r} new={new_points}"]}


def judge(state: dict) -> dict:
    r = state["debate_round"]
    bear_new = state.get("bear", {}).get("new_points", 1)
    converged = (bear_new == 0) or (r >= 2)
    return {"debate_round": r + 1, "converged": converged, "debate_log": [f"JUDGE r{r} converged={converged}"]}


def trader(state: dict) -> dict:
    inconsistent = any(str(f).startswith("INCONSISTENT") for f in state.get("data_flags", []))
    if inconsistent:
        action, rationale = "HOLD", "sentiment source conflict unresolved"
    else:
        action, rationale = "BUY", "fundamentals and technicals aligned"
    return {
        "decision": {
            "action": action,
            "rationale": rationale,
            "reassessment_trigger": "new sentiment data",
            "warnings": [],
        },
        "debate_log": [f"TRADER {action}"],
    }


def final_report(state: dict) -> dict:
    return {
        "final_report": {
            "ticker": state["ticker"],
            "action": state["decision"]["action"],
            "summary": "report generated",
        },
        "outcome": "COMPLETED",
        "debate_log": ["FINAL_REPORT"],
    }


def escalate_data_gap(state: dict) -> dict:
    return {
        "escalation": {"reason": "data inconsistency", "flags": list(state.get("data_flags", []))},
        "outcome": "ESCALATED_DATA_GAP",
        "debate_log": ["ESCALATE"],
    }

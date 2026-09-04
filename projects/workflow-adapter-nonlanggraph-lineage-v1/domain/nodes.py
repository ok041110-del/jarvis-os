"""도메인 stub 노드 13개 — 결정론적, fixture 기반. langgraph 무의존.

의미 출처: hqs/investment/teams/stock_team.py(Wave 병렬 구조),
hqs/investment/trader.py(REPORT/DECISION 분리). 참조만 — import·수정 없음.
각 노드는 partial State 업데이트(dict)를 반환한다.
"""
from __future__ import annotations

from domain.fixtures import scenario_config


def dispatch(state: dict) -> dict:
    return {"debate_log": [f"DISPATCH {state['ticker']}"]}


def _analyst(section: str, payload: dict, state: dict) -> dict:
    cfg = scenario_config(state["scenario"])
    if cfg["raise_in"] == f"analyst_{section}":
        raise RuntimeError(f"injected failure in analyst_{section}")
    return {section: payload}


def analyst_fundamental(state: dict) -> dict:
    return _analyst("fundamental", {"score": 0.7, "note": "stable margins"}, state)


def analyst_technical(state: dict) -> dict:
    return _analyst("technical", {"score": 0.6, "note": "uptrend intact"}, state)


def analyst_industry(state: dict) -> dict:
    return _analyst("industry", {"score": 0.55, "note": "sector neutral"}, state)


def analyst_news_event(state: dict) -> dict:
    return _analyst("news_event", {"score": 0.5, "note": "no material events"}, state)


def analyst_sentiment(state: dict) -> dict:
    cfg = scenario_config(state["scenario"])
    if cfg["raise_in"] == "analyst_sentiment":
        raise RuntimeError("injected failure in analyst_sentiment")
    if cfg["sentiment_conflict"]:
        return {
            "sentiment": {"score": 0.2, "sources": 2, "conflict": True},
            "data_flags": ["INCONSISTENT:sentiment"],
        }
    return {"sentiment": {"score": 0.6, "sources": 2, "conflict": False}}


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

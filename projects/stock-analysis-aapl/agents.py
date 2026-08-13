"""Stock Analysis Capability 함수 — Development HQ Platform(`development-hq/mvp`)을
수정하지 않고, 그 안의 유일한 Engine 호출 지점인 `call_engine()`만 그대로 import해서
쓴다. Investment 도메인 Capability(fundamental_analysis 등)는 `development-hq/mvp`의
기존 예시 Capability 목록(`STRUCTURE.md`: code_review, test_execution, ...)에
없다 — STRUCTURE.md 자신이 "다른 HQ는 전혀 다른 Capability 집합을 가질 수 있다"고
명시하므로, Platform을 확장하는 대신 이 프로젝트가 `development-hq/mvp/agents.py`와
동일한 패턴(리터럴 dict + 지시문-프리픽스 함수 + call_engine 단일 호출)을
project-local로 재사용한다. `textkit`/`notekeeper`가 이미 이 재사용 방식을
검증했다(README 참고).

Engine(`call_engine`)은 stateless text-in/text-out이며 WebFetch/WebSearch/Bash
등이 전부 차단된다 — 실시간 금융 데이터를 스스로 가져올 수 없다. 그래서 실제
데이터 수집은 이 프로젝트를 실행하는 세션(runner 바깥)이 WebSearch로 직접
수행하고, 그 결과(`issues/0001-aapl-analysis/raw_data.md`)를 각 함수의 입력
Context로 그대로 넘긴다 — `notekeeper`의 `_enrich_with_existing_code`와 같은
위치의 역할이며, 새 Capability나 Architecture가 아니다.
"""

import sys
from pathlib import Path

DEV_HQ_ROOT = Path(__file__).resolve().parents[2] / "development-hq"
sys.path.insert(0, str(DEV_HQ_ROOT))

from mvp.engine import call_engine  # noqa: E402

# Registry 구현 금지(IMPLEMENTATION_RULES.md) 원칙을 그대로 따르는 리터럴 dict.
# 조회 함수/클래스로 감싸지 않는다 — development-hq/mvp/agents.py의
# AGENT_CAPABILITY_MAP과 동일한 성격.
STOCK_CAPABILITY_MAP = {
    "fundamental_analysis": "Fundamental Analyst",
    "technical_analysis": "Technical Analyst",
    "industry_analysis": "Industry/Competition Analyst",
    "news_event_analysis": "News/Event Analyst",
    "sentiment_analysis": "Sentiment Analyst",
    "bull_case": "Bull Researcher",
    "bear_case": "Bear Researcher",
    "synthesis": "Portfolio Synthesis",
    "final_report": "Report Writer",
}

_DATA_LIMITATION_NOTICE = (
    "You are given only the data explicitly provided below (collected via web "
    "search at a specific point in time, not live data). Do not invent numbers, "
    "dates, or facts not present in the provided data. If the data is "
    "insufficient or inconsistent for a judgment, say so explicitly rather than "
    "filling the gap."
)


def _run(capability_marker: str, instruction: str, data: str) -> str:
    prompt = f"{capability_marker}:{instruction} {_DATA_LIMITATION_NOTICE}\n\n{data}"
    return call_engine(prompt)


def fundamental_analyst_fundamental_analysis(data: str) -> str:
    instruction = (
        "You are a Fundamental Analyst. Based on the following company "
        "financial data, write a fundamental analysis in prose: revenue/earnings "
        "trend, margin trend, guidance, and what they imply. Do not give a buy/"
        "sell recommendation — that is not your role."
    )
    return _run("FUNDAMENTAL_ANALYSIS", instruction, data)


def technical_analyst_technical_analysis(data: str) -> str:
    instruction = (
        "You are a Technical Analyst. Based on the following price/indicator "
        "data, write a technical analysis in prose: trend direction, momentum, "
        "support/resistance, and any conflicting signals across sources. Do not "
        "give a buy/sell recommendation."
    )
    return _run("TECHNICAL_ANALYSIS", instruction, data)


def industry_analyst_industry_analysis(data: str) -> str:
    instruction = (
        "You are an Industry/Competition Analyst. Based on the following market "
        "share and competitive data, write an analysis in prose of the "
        "company's competitive position and industry dynamics. Do not give a "
        "buy/sell recommendation."
    )
    return _run("INDUSTRY_ANALYSIS", instruction, data)


def news_analyst_news_event_analysis(data: str) -> str:
    instruction = (
        "You are a News/Event Analyst. Based on the following recent news and "
        "events, write an analysis in prose of their likely business impact. Do "
        "not give a buy/sell recommendation."
    )
    return _run("NEWS_EVENT_ANALYSIS", instruction, data)


def sentiment_analyst_sentiment_analysis(data: str) -> str:
    instruction = (
        "You are a Sentiment Analyst. Based on the following analyst ratings "
        "and price target data, write an analysis in prose of market sentiment "
        "and its reliability (e.g. how wide the target range is). Do not give a "
        "buy/sell recommendation."
    )
    return _run("SENTIMENT_ANALYSIS", instruction, data)


def bull_researcher_bull_case(analyses: str) -> str:
    instruction = (
        "You are a Bull Researcher. Based on the following five analyst "
        "reports (fundamental, technical, industry, news/event, sentiment), "
        "construct the strongest good-faith bull case. You must ground every "
        "point in the analyses provided — do not introduce new facts."
    )
    return _run("BULL_CASE", instruction, analyses)


def bear_researcher_bear_case(analyses: str) -> str:
    instruction = (
        "You are a Bear Researcher. Based on the following five analyst "
        "reports (fundamental, technical, industry, news/event, sentiment), "
        "construct the strongest good-faith bear case. You must ground every "
        "point in the analyses provided — do not introduce new facts."
    )
    return _run("BEAR_CASE", instruction, analyses)


def synthesis_judgment(bull_case: str, bear_case: str) -> str:
    instruction = (
        "You are synthesizing a Bull Case and a Bear Case for the same stock "
        "into a balanced judgment. Identify where they actually conflict on "
        "facts vs. where they interpret the same facts differently, and state "
        "which open questions would most change the conclusion. This is not a "
        "trade order and must not include a buy/sell/hold instruction."
    )
    payload = f"[BULL CASE]\n{bull_case}\n\n[BEAR CASE]\n{bear_case}"
    return _run("SYNTHESIS", instruction, payload)


def report_writer_final_report(
    fundamental: str,
    technical: str,
    industry: str,
    news_event: str,
    sentiment: str,
    bull_case: str,
    bear_case: str,
    synthesis: str,
) -> str:
    instruction = (
        "Write a final research report for AAPL that integrates all sections "
        "below into one coherent document with clear headers (Fundamental, "
        "Technical, Industry, News/Event, Sentiment, Bull Case, Bear Case, "
        "Synthesis). End with an explicit disclaimer that this is an analysis "
        "exercise, not investment advice or a trade recommendation."
    )
    payload = (
        f"[FUNDAMENTAL]\n{fundamental}\n\n[TECHNICAL]\n{technical}\n\n"
        f"[INDUSTRY]\n{industry}\n\n[NEWS/EVENT]\n{news_event}\n\n"
        f"[SENTIMENT]\n{sentiment}\n\n[BULL CASE]\n{bull_case}\n\n"
        f"[BEAR CASE]\n{bear_case}\n\n[SYNTHESIS]\n{synthesis}"
    )
    return _run("FINAL_REPORT", instruction, payload)

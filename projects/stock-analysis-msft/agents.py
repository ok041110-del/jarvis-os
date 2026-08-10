"""Stock Analysis Capability 함수 (MSFT) — `projects/stock-analysis-aapl/agents.py`,
`projects/stock-analysis-nvda/agents.py`와 동일한 패턴의 project-local
재사용(3번째)이다. Development HQ Platform(`development-hq/mvp`)을 수정하지
않고, 그 안의 유일한 Engine 호출 지점인 `call_engine()`만 그대로 import해서
쓴다. 다른 두 프로젝트와 코드를 공유하지 않는다(project-local 원칙).

지시문에 출력 언어를 강제하지 않는다 — AAPL(한국어 출력)과 NVDA(영어 출력)가
동일한 지시문에서 다른 언어로 출력된 것이 관찰됐고(NVDA EVIDENCE.md), 이번
실행에서는 그 비일관성이 3번째로도 재현되는지를 그대로 관찰하기 위해
지시문을 바꾸지 않는다.
"""

import sys
from pathlib import Path

DEV_HQ_ROOT = Path(__file__).resolve().parents[2] / "development-hq"
sys.path.insert(0, str(DEV_HQ_ROOT))

from mvp.engine import call_engine  # noqa: E402

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
        "Write a final research report for MSFT that integrates all sections "
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

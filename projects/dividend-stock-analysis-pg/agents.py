import sys
from pathlib import Path

DEV_HQ_ROOT = Path(__file__).resolve().parents[2] / "development-hq"
sys.path.insert(0, str(DEV_HQ_ROOT))

from mvp.engine import call_engine  # noqa: E402

DIVIDEND_STOCK_CAPABILITY_MAP = {
    "fundamental_analysis": "Fundamental Analyst",
    "dividend_quality_analysis": "Dividend Quality Analyst",
    "valuation_analysis": "Valuation Analyst",
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


def dividend_quality_analyst_dividend_quality_analysis(data: str) -> str:
    instruction = (
        "You are a Dividend Quality Analyst. Based on the following dividend "
        "history, payout ratio, and free-cash-flow data, write an analysis in "
        "prose of the dividend's sustainability, growth track record, and "
        "coverage (i.e. whether earnings/cash flow can support current and "
        "future increases). Do not give a buy/sell recommendation."
    )
    return _run("DIVIDEND_QUALITY_ANALYSIS", instruction, data)


def valuation_analyst_valuation_analysis(data: str) -> str:
    instruction = (
        "You are a Valuation Analyst. Based on the following valuation "
        "multiples and peer/industry comparison data, write an analysis in "
        "prose of whether the stock appears cheap or expensive on the "
        "metrics given, explicitly flagging any contradictions between "
        "different valuation methods or sources. Do not give a buy/sell "
        "recommendation."
    )
    return _run("VALUATION_ANALYSIS", instruction, data)


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
        "and its reliability (e.g. how wide the target range is, or whether it "
        "is consistent with the current price). Do not give a buy/sell "
        "recommendation."
    )
    return _run("SENTIMENT_ANALYSIS", instruction, data)


def bull_researcher_bull_case(analyses: str) -> str:
    instruction = (
        "You are a Bull Researcher. Based on the following seven analyst "
        "reports (fundamental, dividend quality, valuation, technical, "
        "industry, news/event, sentiment), construct the strongest "
        "good-faith bull case. You must ground every point in the analyses "
        "provided — do not introduce new facts."
    )
    return _run("BULL_CASE", instruction, analyses)


def bear_researcher_bear_case(analyses: str) -> str:
    instruction = (
        "You are a Bear Researcher. Based on the following seven analyst "
        "reports (fundamental, dividend quality, valuation, technical, "
        "industry, news/event, sentiment), construct the strongest "
        "good-faith bear case. You must ground every point in the analyses "
        "provided — do not introduce new facts."
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
    dividend_quality: str,
    valuation: str,
    technical: str,
    industry: str,
    news_event: str,
    sentiment: str,
    bull_case: str,
    bear_case: str,
    synthesis: str,
) -> str:
    instruction = (
        "Write a final research report for PG (The Procter & Gamble Company) that "
        "integrates all sections below into one coherent document with clear headers (Fundamental, "
        "Dividend Quality, Valuation, Technical, Industry, News/Event, "
        "Sentiment, Bull Case, Bear Case, Synthesis). End with an explicit "
        "disclaimer that this is an analysis exercise, not investment advice "
        "or a trade recommendation."
    )
    payload = (
        f"[FUNDAMENTAL]\n{fundamental}\n\n[DIVIDEND QUALITY]\n{dividend_quality}\n\n"
        f"[VALUATION]\n{valuation}\n\n[TECHNICAL]\n{technical}\n\n"
        f"[INDUSTRY]\n{industry}\n\n[NEWS/EVENT]\n{news_event}\n\n"
        f"[SENTIMENT]\n{sentiment}\n\n[BULL CASE]\n{bull_case}\n\n"
        f"[BEAR CASE]\n{bear_case}\n\n[SYNTHESIS]\n{synthesis}"
    )
    return _run("FINAL_REPORT", instruction, payload)

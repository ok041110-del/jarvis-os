import sys
from pathlib import Path

DEV_HQ_ROOT = Path(__file__).resolve().parents[2] / "development-hq"
sys.path.insert(0, str(DEV_HQ_ROOT))

from mvp.engine import call_engine  # noqa: E402

ETF_CAPABILITY_MAP = {
    "composition_analysis": "Composition/Index Analyst",
    "holdings_analysis": "Holdings/Concentration Analyst",
    "cost_analysis": "Cost/Tracking Analyst",
    "performance_analysis": "Performance/Volatility Analyst",
    "exposure_analysis": "Sector/Geography Exposure Analyst",
    "distribution_analysis": "Distribution Analyst",
    "macro_analysis": "Market/Macro Analyst",
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


def composition_analyst_composition_analysis(data: str) -> str:
    instruction = (
        "You are a Composition/Index Analyst. Based on the following data on "
        "the ETF's tracked index and selection/weighting methodology, write "
        "an analysis in prose: what index it tracks, how constituents are "
        "selected and weighted, and what recent methodology or "
        "reconstitution changes imply. Do not give a buy/sell recommendation "
        "— that is not your role."
    )
    return _run("COMPOSITION_ANALYSIS", instruction, data)


def holdings_analyst_holdings_analysis(data: str) -> str:
    instruction = (
        "You are a Holdings/Concentration Analyst. Based on the following "
        "top-holdings data, write an analysis in prose of concentration risk "
        "(e.g. top-N weight, single-name dominance) and note any "
        "inconsistencies across sources, including any unexplained changes "
        "in top holdings over time. Do not give a buy/sell recommendation."
    )
    return _run("HOLDINGS_ANALYSIS", instruction, data)


def cost_analyst_cost_analysis(data: str) -> str:
    instruction = (
        "You are a Cost/Tracking Analyst. Based on the following expense "
        "ratio and tracking-related data, write an analysis in prose of the "
        "fund's cost structure and how well it likely tracks its benchmark. "
        "If tracking-error data is missing or only qualitative claims are "
        "given, say so explicitly rather than treating them as verified "
        "numbers. Do not give a buy/sell recommendation."
    )
    return _run("COST_ANALYSIS", instruction, data)


def performance_analyst_performance_analysis(data: str) -> str:
    instruction = (
        "You are a Performance/Volatility Analyst. Based on the following "
        "return and volatility data, write an analysis in prose of the "
        "fund's historical performance across periods and its volatility/"
        "risk-adjusted profile. Note any missing or vague quantitative "
        "claims explicitly. Do not give a buy/sell recommendation."
    )
    return _run("PERFORMANCE_ANALYSIS", instruction, data)


def exposure_analyst_exposure_analysis(data: str) -> str:
    instruction = (
        "You are a Sector/Geography Exposure Analyst. Based on the following "
        "sector and geographic exposure data, write an analysis in prose of "
        "the fund's concentration by sector/industry/region, noting any "
        "discrepancies across sources. Do not give a buy/sell "
        "recommendation."
    )
    return _run("EXPOSURE_ANALYSIS", instruction, data)


def distribution_analyst_distribution_analysis(data: str) -> str:
    instruction = (
        "You are a Distribution Analyst. Based on the following dividend/"
        "distribution data, write an analysis in prose of the fund's income "
        "profile: yield, payment frequency, growth history, and any events "
        "(e.g. reconstitution-driven distributions) that could affect "
        "income predictability. Do not give a buy/sell recommendation."
    )
    return _run("DISTRIBUTION_ANALYSIS", instruction, data)


def macro_analyst_macro_analysis(data: str) -> str:
    instruction = (
        "You are a Market/Macro Analyst. Based on the following macro and "
        "rate-environment data, write an analysis in prose of the "
        "macroeconomic backdrop most relevant to a dividend/value-oriented "
        "fund. If the data contains conflicting reports on rate direction, "
        "state the conflict explicitly rather than resolving it. Do not "
        "give a buy/sell recommendation."
    )
    return _run("MACRO_ANALYSIS", instruction, data)


def bull_researcher_bull_case(analyses: str) -> str:
    instruction = (
        "You are a Bull Researcher. Based on the following seven analyst "
        "reports (composition, holdings, cost, performance, exposure, "
        "distribution, macro), construct the strongest good-faith bull case "
        "for this ETF. You must ground every point in the analyses provided "
        "— do not introduce new facts."
    )
    return _run("BULL_CASE", instruction, analyses)


def bear_researcher_bear_case(analyses: str) -> str:
    instruction = (
        "You are a Bear Researcher. Based on the following seven analyst "
        "reports (composition, holdings, cost, performance, exposure, "
        "distribution, macro), construct the strongest good-faith bear case "
        "for this ETF. You must ground every point in the analyses provided "
        "— do not introduce new facts."
    )
    return _run("BEAR_CASE", instruction, analyses)


def synthesis_judgment(bull_case: str, bear_case: str) -> str:
    instruction = (
        "You are synthesizing a Bull Case and a Bear Case for the same ETF "
        "into a balanced judgment. Identify where they actually conflict on "
        "facts vs. where they interpret the same facts differently, and "
        "state which open questions would most change the conclusion. This "
        "is not a trade order and must not include a buy/sell/hold "
        "instruction."
    )
    payload = f"[BULL CASE]\n{bull_case}\n\n[BEAR CASE]\n{bear_case}"
    return _run("SYNTHESIS", instruction, payload)


def report_writer_final_report(
    composition: str,
    holdings: str,
    cost: str,
    performance: str,
    exposure: str,
    distribution: str,
    macro: str,
    bull_case: str,
    bear_case: str,
    synthesis: str,
) -> str:
    instruction = (
        "Write a final research report for SCHD (Schwab U.S. Dividend "
        "Equity ETF) that integrates all sections below into one coherent "
        "document with clear headers (Composition, Holdings, Cost, "
        "Performance, Exposure, Distribution, Macro, Bull Case, Bear Case, "
        "Synthesis). End with an explicit disclaimer that this is an "
        "analysis exercise, not investment advice or a trade "
        "recommendation."
    )
    payload = (
        f"[COMPOSITION]\n{composition}\n\n[HOLDINGS]\n{holdings}\n\n"
        f"[COST]\n{cost}\n\n[PERFORMANCE]\n{performance}\n\n"
        f"[EXPOSURE]\n{exposure}\n\n[DISTRIBUTION]\n{distribution}\n\n"
        f"[MACRO]\n{macro}\n\n[BULL CASE]\n{bull_case}\n\n"
        f"[BEAR CASE]\n{bear_case}\n\n[SYNTHESIS]\n{synthesis}"
    )
    return _run("FINAL_REPORT", instruction, payload)

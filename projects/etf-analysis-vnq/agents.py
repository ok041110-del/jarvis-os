"""ETF Analysis Capability 함수 — Development HQ Platform(`development-hq/mvp`)을
수정하지 않고, 그 안의 유일한 Engine 호출 지점인 `call_engine()`만 그대로 import해서
쓴다. `projects/etf-analysis-{qqq,schd,agg,gld}`와 코드를 공유하지 않는
project-local 복제(다섯 번째 ETF Dogfooding, 최초의 REIT형 ETF) — ETF Team/Agent를
이 파일에서 선행 설계하지 않는다.

QQQ(주식)/SCHD(주식)/AGG(채권)/GLD(원자재)에 이어 자산군이 다시 다른 VNQ(리츠)
에서도 동일한 6개 역할(Composition/Index, Holdings/Exposure, Cost/Tracking,
Performance/Risk, Distribution, Macro) 구조가 반복되는지 검증하는 것이 목적이다.
`docs/research/ETF-TEAM-DEFINITION-0001.md`의 재평가 조건("원자재/리츠/통화 등
다른 자산군에서도 이 범위가 반복되는지 — 미검증")의 "리츠" 항목을 이번 실행에서
처음 다룬다. GLD와 마찬가지로 역할 개수·이름을 바꾸지 않고 AGG/GLD와 동일한 6개
함수를 그대로 유지한다.
"""

import sys
from pathlib import Path

DEV_HQ_ROOT = Path(__file__).resolve().parents[2] / "development-hq"
sys.path.insert(0, str(DEV_HQ_ROOT))

from mvp.engine import call_engine  # noqa: E402

ETF_CAPABILITY_MAP = {
    "composition_analysis": "Composition/Index Analyst",
    "holdings_exposure_analysis": "Holdings/Exposure Analyst",
    "cost_tracking_analysis": "Cost/Tracking Analyst",
    "performance_risk_analysis": "Performance/Risk Analyst",
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
        "the fund's tracked index and portfolio-construction method (e.g. "
        "full replication vs. sampling, or any concentration caps embedded in "
        "the index methodology), write an analysis in prose of what index it "
        "tracks and how that construction method could affect the fund's "
        "behavior. Do not give a buy/sell recommendation — that is not your "
        "role."
    )
    return _run("COMPOSITION_ANALYSIS", instruction, data)


def holdings_exposure_analyst_holdings_exposure_analysis(data: str) -> str:
    instruction = (
        "You are a Holdings/Exposure Analyst. Based on the following data on "
        "sector/asset-type breakdown, top-holdings concentration, and any "
        "credit-quality or maturity distribution, write an analysis in prose "
        "of the fund's concentration and exposure profile. If a metric is not "
        "meaningful or not present for this fund, say so explicitly rather "
        "than inventing it. Do not give a buy/sell recommendation."
    )
    return _run("HOLDINGS_EXPOSURE_ANALYSIS", instruction, data)


def cost_tracking_analyst_cost_tracking_analysis(data: str) -> str:
    instruction = (
        "You are a Cost/Tracking Analyst. Based on the following expense "
        "ratio and tracking-related data, write an analysis in prose of the "
        "fund's cost structure and how well it likely tracks its benchmark, "
        "including any stated reasons the construction method itself might "
        "cause tracking difference. If a numeric tracking-error figure is "
        "missing, say so explicitly. Do not give a buy/sell recommendation."
    )
    return _run("COST_TRACKING_ANALYSIS", instruction, data)


def performance_risk_analyst_performance_risk_analysis(data: str) -> str:
    instruction = (
        "You are a Performance/Risk Analyst. Based on the following return, "
        "yield, and volatility/risk data, write an analysis in prose of the "
        "fund's historical performance and its risk profile, including "
        "whatever risk factors are actually relevant to this fund's asset "
        "class (e.g. interest-rate sensitivity for rate-sensitive assets). "
        "If standard equity/bond risk metrics (beta, duration) do not apply "
        "or are not present in the data, say so explicitly rather than "
        "forcing them. Note any missing or inconsistent quantitative claims "
        "explicitly. Do not give a buy/sell recommendation."
    )
    return _run("PERFORMANCE_RISK_ANALYSIS", instruction, data)


def distribution_analyst_distribution_analysis(data: str) -> str:
    instruction = (
        "You are a Distribution Analyst. Based on the following dividend/"
        "distribution data, write an analysis in prose of the fund's income "
        "profile: yield, payment frequency, and any inconsistency across "
        "reported yield figures. If the fund pays no distribution at all, "
        "say so explicitly rather than describing a yield or frequency that "
        "does not exist. Do not give a buy/sell recommendation."
    )
    return _run("DISTRIBUTION_ANALYSIS", instruction, data)


def macro_analyst_macro_analysis(data: str) -> str:
    instruction = (
        "You are a Market/Macro Analyst. Based on the following macro and "
        "rate-environment data, write an analysis in prose of the "
        "macroeconomic backdrop most relevant to a fund with this asset "
        "profile. If the data contains conflicting or unverified reports or "
        "forecasts, state the conflict explicitly rather than resolving it. "
        "Do not give a buy/sell recommendation."
    )
    return _run("MACRO_ANALYSIS", instruction, data)


def bull_researcher_bull_case(analyses: str) -> str:
    instruction = (
        "You are a Bull Researcher. Based on the following six analyst "
        "reports (composition, holdings/exposure, cost/tracking, "
        "performance/risk, distribution, macro), construct the strongest "
        "good-faith bull case for this ETF. You must ground every point in "
        "the analyses provided — do not introduce new facts."
    )
    return _run("BULL_CASE", instruction, analyses)


def bear_researcher_bear_case(analyses: str) -> str:
    instruction = (
        "You are a Bear Researcher. Based on the following six analyst "
        "reports (composition, holdings/exposure, cost/tracking, "
        "performance/risk, distribution, macro), construct the strongest "
        "good-faith bear case for this ETF. You must ground every point in "
        "the analyses provided — do not introduce new facts."
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
    holdings_exposure: str,
    cost_tracking: str,
    performance_risk: str,
    distribution: str,
    macro: str,
    bull_case: str,
    bear_case: str,
    synthesis: str,
) -> str:
    instruction = (
        "Write a final research report for VNQ (Vanguard Real Estate ETF, "
        "tracking a broad U.S. equity REIT index) that integrates all "
        "sections below into one coherent document with clear headers "
        "(Composition, Holdings/Exposure, Cost/Tracking, Performance/Risk, "
        "Distribution, Macro, Bull Case, Bear Case, Synthesis). End with an "
        "explicit disclaimer that this is an analysis exercise, not "
        "investment advice or a trade recommendation."
    )
    payload = (
        f"[COMPOSITION]\n{composition}\n\n"
        f"[HOLDINGS/EXPOSURE]\n{holdings_exposure}\n\n"
        f"[COST/TRACKING]\n{cost_tracking}\n\n"
        f"[PERFORMANCE/RISK]\n{performance_risk}\n\n"
        f"[DISTRIBUTION]\n{distribution}\n\n[MACRO]\n{macro}\n\n"
        f"[BULL CASE]\n{bull_case}\n\n[BEAR CASE]\n{bear_case}\n\n"
        f"[SYNTHESIS]\n{synthesis}"
    )
    return _run("FINAL_REPORT", instruction, payload)

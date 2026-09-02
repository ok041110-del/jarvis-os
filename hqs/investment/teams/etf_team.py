"""ETF Team — 지시문 정의는 `docs/research/ETF-TEAM-DEFINITION-0001.md` 참조."""

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from checkpoint import Checkpointer, run_step
from engine_client import call_engine
from trader import TRADER_DECISION_INSTRUCTION, parse_decision, run_trader_decision, split_report_decision

_DATA_LIMITATION_NOTICE = (
    "You are given only the data explicitly provided below (collected via web "
    "search at a specific point in time, not live data). Do not invent numbers, "
    "dates, or facts not present in the provided data. If the data is "
    "insufficient or inconsistent for a judgment, say so explicitly rather than "
    "filling the gap."
)

SECTION_TAGS = [
    "[COMPOSITION]", "[HOLDINGS_EXPOSURE]", "[COST_TRACKING]",
    "[PERFORMANCE_RISK]", "[DISTRIBUTION]", "[MACRO]",
]


def _run(capability_marker: str, instruction: str, data: str) -> str:
    prompt = f"{capability_marker}:{instruction} {_DATA_LIMITATION_NOTICE}\n\n{data}"
    return call_engine(prompt)


def composition_analyst_composition_analysis(data: str) -> str:
    instruction = (
        "You are a Composition/Index Analyst. Based on the following data on "
        "the fund's tracked index and portfolio-construction method (e.g. "
        "full replication vs. sampling vs. a futures-based structure), write "
        "an analysis in prose of what the fund tracks and how that "
        "construction method could affect the fund's behavior. If the source "
        "data itself contains conflicting descriptions of what the fund "
        "tracks, say so explicitly rather than picking one. Do not give a "
        "buy/sell recommendation — that is not your role."
    )
    return _run("COMPOSITION_ANALYSIS", instruction, data)


def holdings_exposure_analyst_holdings_exposure_analysis(data: str) -> str:
    instruction = (
        "You are a Holdings/Exposure Analyst. Based on the following data on "
        "what the fund actually holds (securities, physical assets, or "
        "derivative/futures positions) and its exposure structure, write an "
        "analysis in prose of the fund's concentration and exposure profile. "
        "If a conventional metric (e.g. sector weight, single-name "
        "concentration, credit quality) is not meaningful or not present for "
        "this fund's structure, say so explicitly rather than inventing it. "
        "Do not give a buy/sell recommendation."
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
        "class (e.g. currency/exchange-rate risk, or roll risk for a "
        "futures-based fund). If standard equity/bond risk metrics (beta, "
        "duration) do not apply or are not present in the data, say so "
        "explicitly rather than forcing them. Note any missing or "
        "inconsistent quantitative claims explicitly. Do not give a buy/sell "
        "recommendation."
    )
    return _run("PERFORMANCE_RISK_ANALYSIS", instruction, data)


def distribution_analyst_distribution_analysis(data: str) -> str:
    instruction = (
        "You are a Distribution Analyst. Based on the following dividend/"
        "distribution data, write an analysis in prose of the fund's income "
        "profile: yield, payment frequency, and any inconsistency across "
        "reported yield figures. If the fund pays no distribution at all, "
        "say so explicitly rather than describing a yield or frequency that "
        "does not exist. Note any unusual tax-reporting structure mentioned "
        "in the data (e.g. K-1 vs. 1099) as part of the income profile. Do "
        "not give a buy/sell recommendation."
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


def trader_decision(bull_case: str, bear_case: str) -> str:
    """Synthesis(REPORT) + Trader(DECISION) 단일 호출 — `stock_team.py`와
    동일 원칙(최소 변경, 지시문 재사용)."""
    instruction = (
        "You are synthesizing a Bull Case and a Bear Case for the same ETF "
        "into a balanced judgment. Identify where they actually conflict on "
        "facts vs. where they interpret the same facts differently, and "
        "state which open questions would most change the conclusion."
        + TRADER_DECISION_INSTRUCTION
    )
    payload = f"[BULL CASE]\n{bull_case}\n\n[BEAR CASE]\n{bear_case}"
    return _run("TRADER", instruction, payload)


def report_writer_final_report(fund_label, composition, holdings_exposure, cost_tracking, performance_risk, distribution, macro, bull_case, bear_case, synthesis) -> str:
    instruction = (
        f"Write a final research report for {fund_label} that integrates all sections "
        "below into one coherent document with clear headers (Composition, "
        "Holdings/Exposure, Cost/Tracking, Performance/Risk, Distribution, "
        "Macro, Bull Case, Bear Case, Synthesis). End with an explicit "
        "disclaimer that this is an analysis exercise, not investment advice "
        "or a trade recommendation. Keep the report concise: target roughly "
        "800-1200 words total. Still cover every required section and still "
        "flag every data inconsistency noted in the source sections — just "
        "express each section more tersely (short paragraphs or bullet "
        "points) rather than omitting content."
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


def _extract_section(raw_text: str, tag: str) -> str:
    marker = f"## {tag}"
    start = raw_text.index(marker)
    rest = raw_text[start:]
    next_header = rest.find("\n## ", 1)
    section = rest if next_header == -1 else rest[:next_header]
    return section.strip()


def run(fund_label: str, raw_data_path: Path, issue_dir: Path) -> dict:
    pipeline_t0 = time.monotonic()
    cp = Checkpointer(issue_dir)

    raw_text = raw_data_path.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")
    sections = {tag: f"Fund: {fund_label}\n\n{_extract_section(raw_text, tag)}" for tag in SECTION_TAGS}

    wave1_jobs = {
        "composition_analysis": (composition_analyst_composition_analysis, f"{sections['[COMPOSITION]']}\n\n{limitation}"),
        "holdings_exposure_analysis": (holdings_exposure_analyst_holdings_exposure_analysis, f"{sections['[HOLDINGS_EXPOSURE]']}\n\n{limitation}"),
        "cost_tracking_analysis": (cost_tracking_analyst_cost_tracking_analysis, f"{sections['[COST_TRACKING]']}\n\n{limitation}"),
        "performance_risk_analysis": (performance_risk_analyst_performance_risk_analysis, f"{sections['[PERFORMANCE_RISK]']}\n\n{limitation}"),
        "distribution_analysis": (distribution_analyst_distribution_analysis, f"{sections['[DISTRIBUTION]']}\n\n{limitation}"),
        "macro_analysis": (macro_analyst_macro_analysis, f"{sections['[MACRO]']}\n\n{limitation}"),
    }
    wave1_t0 = time.monotonic()
    wave1_results = {}
    pending = {n: v for n, v in wave1_jobs.items() if not cp.has(n)}
    for n in wave1_jobs:
        if cp.has(n):
            wave1_results[n] = cp.load(n)
    if pending:
        with ThreadPoolExecutor(max_workers=len(pending)) as pool:
            futures = {n: pool.submit(run_step, cp, n, fn, arg) for n, (fn, arg) in pending.items()}
            for n, fut in futures.items():
                wave1_results[n] = fut.result()
    wave1_elapsed = time.monotonic() - wave1_t0

    composition = wave1_results["composition_analysis"]
    holdings_exposure = wave1_results["holdings_exposure_analysis"]
    cost_tracking = wave1_results["cost_tracking_analysis"]
    performance_risk = wave1_results["performance_risk_analysis"]
    distribution = wave1_results["distribution_analysis"]
    macro = wave1_results["macro_analysis"]

    all_analyses = (
        f"[COMPOSITION]\n{composition}\n\n[HOLDINGS/EXPOSURE]\n{holdings_exposure}\n\n"
        f"[COST/TRACKING]\n{cost_tracking}\n\n[PERFORMANCE/RISK]\n{performance_risk}\n\n"
        f"[DISTRIBUTION]\n{distribution}\n\n[MACRO]\n{macro}"
    )

    wave2_t0 = time.monotonic()
    wave2_jobs = {"bull_case": (bull_researcher_bull_case, all_analyses), "bear_case": (bear_researcher_bear_case, all_analyses)}
    wave2_results = {}
    pending2 = {n: v for n, v in wave2_jobs.items() if not cp.has(n)}
    for n in wave2_jobs:
        if cp.has(n):
            wave2_results[n] = cp.load(n)
    if pending2:
        with ThreadPoolExecutor(max_workers=len(pending2)) as pool:
            futures = {n: pool.submit(run_step, cp, n, fn, arg) for n, (fn, arg) in pending2.items()}
            for n, fut in futures.items():
                wave2_results[n] = fut.result()
    wave2_elapsed = time.monotonic() - wave2_t0

    bull_case = wave2_results["bull_case"]
    bear_case = wave2_results["bear_case"]

    wave3_t0 = time.monotonic()
    trader_raw = run_trader_decision(cp, trader_decision, bull_case, bear_case)
    report_text, decision_text = split_report_decision(trader_raw)
    decision_parsed = parse_decision(decision_text)
    wave3_elapsed = time.monotonic() - wave3_t0

    wave4_t0 = time.monotonic()
    final_report = run_step(cp, "final_report", report_writer_final_report, fund_label, composition, holdings_exposure, cost_tracking, performance_risk, distribution, macro, bull_case, bear_case, report_text)
    wave4_elapsed = time.monotonic() - wave4_t0

    pipeline_elapsed = time.monotonic() - pipeline_t0

    results = {
        "composition_analysis.md": composition,
        "holdings_exposure_analysis.md": holdings_exposure,
        "cost_tracking_analysis.md": cost_tracking,
        "performance_risk_analysis.md": performance_risk,
        "distribution_analysis.md": distribution,
        "macro_analysis.md": macro,
        "bull_case.md": bull_case,
        "bear_case.md": bear_case,
        "synthesis.md": report_text,
        "trader_decision.md": decision_text,
        "final_report.md": final_report,
    }
    for filename, content in results.items():
        (issue_dir / filename).write_text(content.rstrip() + "\n", encoding="utf-8")

    wave_summary = {
        "wave1_elapsed_sec": round(wave1_elapsed, 1),
        "wave2_elapsed_sec": round(wave2_elapsed, 1),
        "wave3_elapsed_sec": round(wave3_elapsed, 1),
        "wave4_elapsed_sec": round(wave4_elapsed, 1),
        "pipeline_total_elapsed_sec": round(pipeline_elapsed, 1),
        "trader_decision": decision_parsed,
    }
    (issue_dir / "call_log.json").write_text(
        json.dumps({"calls": cp.manifest["call_log"], "wave_summary": wave_summary}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"results": results, "wave_summary": wave_summary}

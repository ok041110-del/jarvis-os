"""Stock Team — 지시문 정의는 `docs/research/STOCK-TEAM-DEFINITION-0001.md` 참조."""

import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from checkpoint import Checkpointer, run_step
from engine_client import call_engine

_DATA_LIMITATION_NOTICE = (
    "You are given only the data explicitly provided below (collected via web "
    "search at a specific point in time, not live data). Do not invent numbers, "
    "dates, or facts not present in the provided data. If the data is "
    "insufficient or inconsistent for a judgment, say so explicitly rather than "
    "filling the gap."
)

SECTION_TAGS = ["[FUNDAMENTAL]", "[TECHNICAL]", "[INDUSTRY]", "[NEWS/EVENT]", "[SENTIMENT]"]


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


def report_writer_final_report(company_label: str, fundamental, technical, industry, news_event, sentiment, bull_case, bear_case, synthesis) -> str:
    instruction = (
        f"Write a final research report for {company_label} that integrates all sections "
        "below into one coherent document with clear headers (Fundamental, "
        "Technical, Industry, News/Event, Sentiment, Bull Case, Bear Case, "
        "Synthesis). End with an explicit disclaimer that this is an analysis "
        "exercise, not investment advice or a trade recommendation. Keep the "
        "report concise: target roughly 800-1200 words total. Still cover "
        "every required section and still flag every data inconsistency "
        "noted in the source sections — just express each section more "
        "tersely (short paragraphs or bullet points) rather than omitting "
        "content."
    )
    payload = (
        f"[FUNDAMENTAL]\n{fundamental}\n\n[TECHNICAL]\n{technical}\n\n"
        f"[INDUSTRY]\n{industry}\n\n[NEWS/EVENT]\n{news_event}\n\n"
        f"[SENTIMENT]\n{sentiment}\n\n[BULL CASE]\n{bull_case}\n\n"
        f"[BEAR CASE]\n{bear_case}\n\n[SYNTHESIS]\n{synthesis}"
    )
    return _run("FINAL_REPORT", instruction, payload)


def _extract_section(raw_text: str, tag: str) -> str:
    marker = f"## {tag}"
    start = raw_text.index(marker)
    rest = raw_text[start:]
    next_header = rest.find("\n## ", 1)
    section = rest if next_header == -1 else rest[:next_header]
    return section.strip()


def run(company_label: str, raw_data_path: Path, issue_dir: Path) -> dict:
    """Wave 순서는 하드코딩(Workflow Parser 아님) — minimalism 원칙."""
    pipeline_t0 = time.monotonic()
    cp = Checkpointer(issue_dir)

    raw_text = raw_data_path.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")
    sections = {tag: f"Company: {company_label}\n\n{_extract_section(raw_text, tag)}" for tag in SECTION_TAGS}

    wave1_jobs = {
        "fundamental_analysis": (fundamental_analyst_fundamental_analysis, f"{sections['[FUNDAMENTAL]']}\n\n{limitation}"),
        "technical_analysis": (technical_analyst_technical_analysis, f"{sections['[TECHNICAL]']}\n\n{limitation}"),
        "industry_analysis": (industry_analyst_industry_analysis, f"{sections['[INDUSTRY]']}\n\n{limitation}"),
        "news_event_analysis": (news_analyst_news_event_analysis, f"{sections['[NEWS/EVENT]']}\n\n{limitation}"),
        "sentiment_analysis": (sentiment_analyst_sentiment_analysis, f"{sections['[SENTIMENT]']}\n\n{limitation}"),
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

    fundamental = wave1_results["fundamental_analysis"]
    technical = wave1_results["technical_analysis"]
    industry = wave1_results["industry_analysis"]
    news_event = wave1_results["news_event_analysis"]
    sentiment = wave1_results["sentiment_analysis"]

    all_analyses = (
        f"[FUNDAMENTAL ANALYSIS]\n{fundamental}\n\n[TECHNICAL ANALYSIS]\n{technical}\n\n"
        f"[INDUSTRY ANALYSIS]\n{industry}\n\n[NEWS/EVENT ANALYSIS]\n{news_event}\n\n"
        f"[SENTIMENT ANALYSIS]\n{sentiment}"
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
    synthesis = run_step(cp, "synthesis", synthesis_judgment, bull_case, bear_case)
    wave3_elapsed = time.monotonic() - wave3_t0

    wave4_t0 = time.monotonic()
    final_report = run_step(cp, "final_report", report_writer_final_report, company_label, fundamental, technical, industry, news_event, sentiment, bull_case, bear_case, synthesis)
    wave4_elapsed = time.monotonic() - wave4_t0

    pipeline_elapsed = time.monotonic() - pipeline_t0

    results = {
        "fundamental_analysis.md": fundamental,
        "technical_analysis.md": technical,
        "industry_analysis.md": industry,
        "news_event_analysis.md": news_event,
        "sentiment_analysis.md": sentiment,
        "bull_case.md": bull_case,
        "bear_case.md": bear_case,
        "synthesis.md": synthesis,
        "final_report.md": final_report,
    }
    for filename, content in results.items():
        (issue_dir / filename).write_text(content.rstrip() + "\n", encoding="utf-8")

    import json
    wave_summary = {
        "wave1_elapsed_sec": round(wave1_elapsed, 1),
        "wave2_elapsed_sec": round(wave2_elapsed, 1),
        "wave3_elapsed_sec": round(wave3_elapsed, 1),
        "wave4_elapsed_sec": round(wave4_elapsed, 1),
        "pipeline_total_elapsed_sec": round(pipeline_elapsed, 1),
    }
    (issue_dir / "call_log.json").write_text(
        json.dumps({"calls": cp.manifest["call_log"], "wave_summary": wave_summary}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"results": results, "wave_summary": wave_summary}

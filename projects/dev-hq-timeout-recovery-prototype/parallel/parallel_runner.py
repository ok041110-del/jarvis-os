"""Usage: python3 parallel_runner.py <trial_id>"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROTO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROTO_ROOT / "shared"))

import agents  # noqa: E402  (shared/agents.py, 진짜 call_engine을 그대로 씀)

RAW_DATA_PATH = PROTO_ROOT / "shared" / "raw_data.md"

_SECTION_TAGS = [
    "[FUNDAMENTAL]",
    "[DIVIDEND_QUALITY]",
    "[VALUATION]",
    "[TECHNICAL]",
    "[INDUSTRY]",
    "[NEWS/EVENT]",
    "[SENTIMENT]",
]

_COMPANY_HEADER = "Company: Nestlé S.A. (Primary: NESN.SW, ADR: NSRGY)"

_call_log = []


def _extract_section(raw_text: str, tag: str) -> str:
    marker = f"## {tag}"
    start = raw_text.index(marker)
    rest = raw_text[start:]
    next_header = rest.find("\n## ", 1)
    section = rest if next_header == -1 else rest[:next_header]
    return section.strip()


def _timed_call(role: str, fn, *args) -> str:
    # Runs inside a worker thread; list.append is GIL-atomic so no lock needed.
    input_len = sum(len(a) for a in args)
    t0 = time.monotonic()
    output = fn(*args)
    elapsed = time.monotonic() - t0
    _call_log.append(
        {
            "role": role,
            "input_chars": input_len,
            "output_chars": len(output),
            "elapsed_sec": round(elapsed, 1),
            "wall_start_offset_sec": None,  # run()에서 채움
        }
    )
    return output


def run(issue_dir: Path) -> dict:
    pipeline_t0 = time.monotonic()
    raw_text = RAW_DATA_PATH.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")
    sections = {
        tag: f"{_COMPANY_HEADER}\n\n{_extract_section(raw_text, tag)}"
        for tag in _SECTION_TAGS
    }

    wave1_jobs = {
        "fundamental_analysis": (agents.fundamental_analyst_fundamental_analysis, f"{sections['[FUNDAMENTAL]']}\n\n{limitation}"),
        "dividend_quality_analysis": (agents.dividend_quality_analyst_dividend_quality_analysis, f"{sections['[DIVIDEND_QUALITY]']}\n\n{limitation}"),
        "valuation_analysis": (agents.valuation_analyst_valuation_analysis, f"{sections['[VALUATION]']}\n\n{limitation}"),
        "technical_analysis": (agents.technical_analyst_technical_analysis, f"{sections['[TECHNICAL]']}\n\n{limitation}"),
        "industry_analysis": (agents.industry_analyst_industry_analysis, f"{sections['[INDUSTRY]']}\n\n{limitation}"),
        "news_event_analysis": (agents.news_analyst_news_event_analysis, f"{sections['[NEWS/EVENT]']}\n\n{limitation}"),
        "sentiment_analysis": (agents.sentiment_analyst_sentiment_analysis, f"{sections['[SENTIMENT]']}\n\n{limitation}"),
    }
    wave1_t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=7) as pool:
        futures = {name: pool.submit(_timed_call, name, fn, arg) for name, (fn, arg) in wave1_jobs.items()}
        wave1_results = {name: fut.result() for name, fut in futures.items()}
    wave1_elapsed = time.monotonic() - wave1_t0

    fundamental = wave1_results["fundamental_analysis"]
    dividend_quality = wave1_results["dividend_quality_analysis"]
    valuation = wave1_results["valuation_analysis"]
    technical = wave1_results["technical_analysis"]
    industry = wave1_results["industry_analysis"]
    news_event = wave1_results["news_event_analysis"]
    sentiment = wave1_results["sentiment_analysis"]

    all_analyses = (
        f"[FUNDAMENTAL ANALYSIS]\n{fundamental}\n\n"
        f"[DIVIDEND QUALITY ANALYSIS]\n{dividend_quality}\n\n"
        f"[VALUATION ANALYSIS]\n{valuation}\n\n"
        f"[TECHNICAL ANALYSIS]\n{technical}\n\n"
        f"[INDUSTRY ANALYSIS]\n{industry}\n\n"
        f"[NEWS/EVENT ANALYSIS]\n{news_event}\n\n"
        f"[SENTIMENT ANALYSIS]\n{sentiment}"
    )

    wave2_t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_bull = pool.submit(_timed_call, "bull_case", agents.bull_researcher_bull_case, all_analyses)
        f_bear = pool.submit(_timed_call, "bear_case", agents.bear_researcher_bear_case, all_analyses)
        bull_case = f_bull.result()
        bear_case = f_bear.result()
    wave2_elapsed = time.monotonic() - wave2_t0

    wave3_t0 = time.monotonic()
    synthesis = _timed_call("synthesis", agents.synthesis_judgment, bull_case, bear_case)
    wave3_elapsed = time.monotonic() - wave3_t0

    wave4_t0 = time.monotonic()
    final_report = _timed_call(
        "final_report", agents.report_writer_final_report,
        fundamental, dividend_quality, valuation, technical,
        industry, news_event, sentiment, bull_case, bear_case, synthesis,
    )
    wave4_elapsed = time.monotonic() - wave4_t0

    pipeline_elapsed = time.monotonic() - pipeline_t0

    results = {
        "fundamental_analysis.md": fundamental,
        "dividend_quality_analysis.md": dividend_quality,
        "valuation_analysis.md": valuation,
        "technical_analysis.md": technical,
        "industry_analysis.md": industry,
        "news_event_analysis.md": news_event,
        "sentiment_analysis.md": sentiment,
        "bull_case.md": bull_case,
        "bear_case.md": bear_case,
        "synthesis.md": synthesis,
        "final_report.md": final_report,
    }
    issue_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in results.items():
        (issue_dir / filename).write_text(content.rstrip() + "\n", encoding="utf-8")

    wave_summary = {
        "wave1_7_analyses_parallel_elapsed_sec": round(wave1_elapsed, 1),
        "wave1_sum_individual_elapsed_sec": round(sum(e["elapsed_sec"] for e in _call_log if e["role"] in wave1_jobs), 1),
        "wave2_bull_bear_parallel_elapsed_sec": round(wave2_elapsed, 1),
        "wave2_sum_individual_elapsed_sec": round(sum(e["elapsed_sec"] for e in _call_log if e["role"] in ("bull_case", "bear_case")), 1),
        "wave3_synthesis_elapsed_sec": round(wave3_elapsed, 1),
        "wave4_final_report_elapsed_sec": round(wave4_elapsed, 1),
        "pipeline_total_elapsed_sec": round(pipeline_elapsed, 1),
    }

    (issue_dir / "call_log.json").write_text(
        json.dumps({"calls": _call_log, "wave_summary": wave_summary}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return results, wave_summary


if __name__ == "__main__":
    trial_id = sys.argv[1] if len(sys.argv) > 1 else "trial"
    issue_dir = PROTO_ROOT / "trials" / f"parallel_{trial_id}"

    t0 = time.monotonic()
    status = "success"
    wave_summary = {}
    try:
        _, wave_summary = run(issue_dir)
    except Exception as e:
        status = f"failed: {type(e).__name__}: {e}"
        raise
    finally:
        elapsed_total = time.monotonic() - t0
        summary = {
            "variant": "parallel",
            "trial_id": trial_id,
            "status": status,
            "elapsed_total_sec": round(elapsed_total, 1),
            "steps_completed": len(_call_log),
            **wave_summary,
        }
        summary_path = PROTO_ROOT / "trials" / f"parallel_{trial_id}_summary.json"
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))

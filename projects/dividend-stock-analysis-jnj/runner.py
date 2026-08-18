import json
import time
from pathlib import Path

from agents import (
    bear_researcher_bear_case,
    bull_researcher_bull_case,
    dividend_quality_analyst_dividend_quality_analysis,
    fundamental_analyst_fundamental_analysis,
    industry_analyst_industry_analysis,
    news_analyst_news_event_analysis,
    report_writer_final_report,
    sentiment_analyst_sentiment_analysis,
    synthesis_judgment,
    technical_analyst_technical_analysis,
    valuation_analyst_valuation_analysis,
)

PROJECT_ROOT = Path(__file__).resolve().parent
ISSUE_DIR = PROJECT_ROOT / "issues" / "0001-jnj-analysis"
RAW_DATA_PATH = ISSUE_DIR / "raw_data.md"

_SECTION_TAGS = [
    "[FUNDAMENTAL]",
    "[DIVIDEND_QUALITY]",
    "[VALUATION]",
    "[TECHNICAL]",
    "[INDUSTRY]",
    "[NEWS/EVENT]",
    "[SENTIMENT]",
]

_COMPANY_HEADER = "Company: Johnson & Johnson (Ticker: JNJ)"

_call_log = []


def _extract_section(raw_text: str, tag: str) -> str:
    marker = f"## {tag}"
    start = raw_text.index(marker)
    rest = raw_text[start:]
    next_header = rest.find("\n## ", 1)
    section = rest if next_header == -1 else rest[:next_header]
    return section.strip()


def _timed(role: str, fn, *args) -> str:
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
        }
    )
    return output


def run() -> dict:
    raw_text = RAW_DATA_PATH.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")

    sections = {
        tag: f"{_COMPANY_HEADER}\n\n{_extract_section(raw_text, tag)}"
        for tag in _SECTION_TAGS
    }

    fundamental = _timed(
        "fundamental_analyst_fundamental_analysis",
        fundamental_analyst_fundamental_analysis,
        f"{sections['[FUNDAMENTAL]']}\n\n{limitation}",
    )
    dividend_quality = _timed(
        "dividend_quality_analyst_dividend_quality_analysis",
        dividend_quality_analyst_dividend_quality_analysis,
        f"{sections['[DIVIDEND_QUALITY]']}\n\n{limitation}",
    )
    valuation = _timed(
        "valuation_analyst_valuation_analysis",
        valuation_analyst_valuation_analysis,
        f"{sections['[VALUATION]']}\n\n{limitation}",
    )
    technical = _timed(
        "technical_analyst_technical_analysis",
        technical_analyst_technical_analysis,
        f"{sections['[TECHNICAL]']}\n\n{limitation}",
    )
    industry = _timed(
        "industry_analyst_industry_analysis",
        industry_analyst_industry_analysis,
        f"{sections['[INDUSTRY]']}\n\n{limitation}",
    )
    news_event = _timed(
        "news_analyst_news_event_analysis",
        news_analyst_news_event_analysis,
        f"{sections['[NEWS/EVENT]']}\n\n{limitation}",
    )
    sentiment = _timed(
        "sentiment_analyst_sentiment_analysis",
        sentiment_analyst_sentiment_analysis,
        f"{sections['[SENTIMENT]']}\n\n{limitation}",
    )

    all_analyses = (
        f"[FUNDAMENTAL ANALYSIS]\n{fundamental}\n\n"
        f"[DIVIDEND QUALITY ANALYSIS]\n{dividend_quality}\n\n"
        f"[VALUATION ANALYSIS]\n{valuation}\n\n"
        f"[TECHNICAL ANALYSIS]\n{technical}\n\n"
        f"[INDUSTRY ANALYSIS]\n{industry}\n\n"
        f"[NEWS/EVENT ANALYSIS]\n{news_event}\n\n"
        f"[SENTIMENT ANALYSIS]\n{sentiment}"
    )

    bull_case = _timed(
        "bull_researcher_bull_case", bull_researcher_bull_case, all_analyses
    )
    bear_case = _timed(
        "bear_researcher_bear_case", bear_researcher_bear_case, all_analyses
    )
    synthesis = _timed(
        "synthesis_judgment", synthesis_judgment, bull_case, bear_case
    )
    final_report = _timed(
        "report_writer_final_report",
        report_writer_final_report,
        fundamental,
        dividend_quality,
        valuation,
        technical,
        industry,
        news_event,
        sentiment,
        bull_case,
        bear_case,
        synthesis,
    )

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
    for filename, content in results.items():
        (ISSUE_DIR / filename).write_text(content.rstrip() + "\n", encoding="utf-8")

    (ISSUE_DIR / "call_log.json").write_text(
        json.dumps(_call_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    return results


if __name__ == "__main__":
    run()
    print(f"Done. Output written to {ISSUE_DIR}")

"""AAPL Stock Analysis runner.

raw_data.md(이 세션이 WebSearch로 미리 수집한 실제 데이터) -> 5개 전문 분석
(Fundamental/Technical/Industry/News-Event/Sentiment) -> Bull Case/Bear Case ->
Synthesis -> Final Report. 각 단계는 `agents.py`의 함수를 순서대로 직접
호출하는 하드코딩된 흐름이다 — Workflow Parser/Scheduler/Dispatcher를 만들지
않는다(`textkit`/`notekeeper` runner.py와 동일한 성격).

이 파일은 Development HQ(`development-hq/mvp`)를 수정하지 않는다.
"""

from pathlib import Path

from agents import (
    bear_researcher_bear_case,
    bull_researcher_bull_case,
    fundamental_analyst_fundamental_analysis,
    industry_analyst_industry_analysis,
    news_analyst_news_event_analysis,
    report_writer_final_report,
    sentiment_analyst_sentiment_analysis,
    synthesis_judgment,
    technical_analyst_technical_analysis,
)

PROJECT_ROOT = Path(__file__).resolve().parent
ISSUE_DIR = PROJECT_ROOT / "issues" / "0001-aapl-analysis"
RAW_DATA_PATH = ISSUE_DIR / "raw_data.md"

# raw_data.md의 "## [TAG] ..." 섹션 헤더를 그대로 split key로 쓴다 — 별도
# 파서를 만들지 않고 문자열 split만 사용한다(파서를 만들면 Workflow Parser
# 일반화에 근접하므로 의도적으로 가장 단순한 방식을 쓴다).
_SECTION_TAGS = [
    "[FUNDAMENTAL]",
    "[TECHNICAL]",
    "[INDUSTRY]",
    "[NEWS/EVENT]",
    "[SENTIMENT]",
]


def _extract_section(raw_text: str, tag: str) -> str:
    marker = f"## {tag}"
    start = raw_text.index(marker)
    rest = raw_text[start:]
    next_header = rest.find("\n## ", 1)
    section = rest if next_header == -1 else rest[:next_header]
    return section.strip()


# MVP-STOCK-0001 Evidence: raw_data.md의 "## [TAG] ..." 섹션에는 회사/티커명이
# 없다 — 첫 실행에서 모든 5개 Capability가 iPhone/Mac 등 단서로 회사를 "추정"해야
# 했다(각 산출물에 그 추정 문구가 그대로 남았다). Capability 함수 시그니처나
# raw_data.md 포맷을 바꾸지 않고, 각 섹션 앞에 한 줄만 추가해 실제로 발견된
# 문제만 최소 수정한다.
_COMPANY_HEADER = "Company: Apple Inc. (Ticker: AAPL)"


def run() -> dict:
    raw_text = RAW_DATA_PATH.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")

    sections = {
        tag: f"{_COMPANY_HEADER}\n\n{_extract_section(raw_text, tag)}"
        for tag in _SECTION_TAGS
    }

    fundamental = fundamental_analyst_fundamental_analysis(
        f"{sections['[FUNDAMENTAL]']}\n\n{limitation}"
    )
    technical = technical_analyst_technical_analysis(
        f"{sections['[TECHNICAL]']}\n\n{limitation}"
    )
    industry = industry_analyst_industry_analysis(
        f"{sections['[INDUSTRY]']}\n\n{limitation}"
    )
    news_event = news_analyst_news_event_analysis(
        f"{sections['[NEWS/EVENT]']}\n\n{limitation}"
    )
    sentiment = sentiment_analyst_sentiment_analysis(
        f"{sections['[SENTIMENT]']}\n\n{limitation}"
    )

    all_analyses = (
        f"[FUNDAMENTAL ANALYSIS]\n{fundamental}\n\n"
        f"[TECHNICAL ANALYSIS]\n{technical}\n\n"
        f"[INDUSTRY ANALYSIS]\n{industry}\n\n"
        f"[NEWS/EVENT ANALYSIS]\n{news_event}\n\n"
        f"[SENTIMENT ANALYSIS]\n{sentiment}"
    )

    bull_case = bull_researcher_bull_case(all_analyses)
    bear_case = bear_researcher_bear_case(all_analyses)
    synthesis = synthesis_judgment(bull_case, bear_case)
    final_report = report_writer_final_report(
        fundamental,
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

    return results


if __name__ == "__main__":
    run()
    print(f"Done. Output written to {ISSUE_DIR}")

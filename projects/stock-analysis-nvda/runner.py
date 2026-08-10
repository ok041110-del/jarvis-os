"""NVDA Stock Analysis runner.

`projects/stock-analysis-aapl/runner.py`와 동일한 흐름: raw_data.md -> 5개
전문 분석 -> Bull Case/Bear Case -> Synthesis -> Final Report, 하드코딩된
순차 호출. AAPL 1차 실행에서 발견된 "raw_data.md 섹션에 회사명이 없어 Engine이
회사를 추정"하는 문제가 이번에도 재발할 수 있으므로, AAPL에서 검증된 수정
(`_COMPANY_HEADER` 프리픽스)을 그대로 재사용한다 — 새로 발견한 문제가 아니라
이미 검증된 수정의 재사용이다. 추가로 이번 `raw_data.md` 원본 자체에도 각
섹션에 회사명을 직접 적어, 두 프로젝트의 raw_data.md 작성 방식 차이가 실제
재현 여부에 영향을 주는지 관찰한다(EVIDENCE.md 참고).

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
ISSUE_DIR = PROJECT_ROOT / "issues" / "0001-nvda-analysis"
RAW_DATA_PATH = ISSUE_DIR / "raw_data.md"

_SECTION_TAGS = [
    "[FUNDAMENTAL]",
    "[TECHNICAL]",
    "[INDUSTRY]",
    "[NEWS/EVENT]",
    "[SENTIMENT]",
]

_COMPANY_HEADER = "Company: NVIDIA Corporation (Ticker: NVDA)"


def _extract_section(raw_text: str, tag: str) -> str:
    marker = f"## {tag}"
    start = raw_text.index(marker)
    rest = raw_text[start:]
    next_header = rest.find("\n## ", 1)
    section = rest if next_header == -1 else rest[:next_header]
    return section.strip()


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

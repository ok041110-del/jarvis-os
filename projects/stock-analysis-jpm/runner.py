"""JPM Stock Analysis runner (4번째 반복 실행).

raw_data.md(이 세션이 WebSearch로 미리 수집한 실제 데이터) -> 5개 전문 분석
(Fundamental/Technical/Industry/News-Event/Sentiment) -> Bull Case/Bear Case ->
Synthesis -> Final Report. 각 단계는 `agents.py`의 함수를 순서대로 직접
호출하는 하드코딩된 흐름이다 — Workflow Parser/Scheduler/Dispatcher를 만들지
않는다(AAPL/NVDA/MSFT runner.py와 동일한 성격).

이번 실행은 AAPL runner.py 대비 한 가지를 추가한다: 각 호출의 입력 길이/
출력 길이/소요 시간을 `call_log.json`에 기록한다. 이는 새 Contract나
Capability가 아니라, 이번 Evidence 확보 목적(역할/Agent 분리 필요성 검증)을
위해 이 project-local 파일 안에서만 관찰 데이터를 남기는 것이다 —
`development-hq/mvp`는 수정하지 않는다.

이 파일은 Development HQ(`development-hq/mvp`)를 수정하지 않는다.
"""

import json
import time
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
ISSUE_DIR = PROJECT_ROOT / "issues" / "0001-jpm-analysis"
RAW_DATA_PATH = ISSUE_DIR / "raw_data.md"

_SECTION_TAGS = [
    "[FUNDAMENTAL]",
    "[TECHNICAL]",
    "[INDUSTRY]",
    "[NEWS/EVENT]",
    "[SENTIMENT]",
]

_COMPANY_HEADER = "Company: JPMorgan Chase & Co. (Ticker: JPM)"

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

    (ISSUE_DIR / "call_log.json").write_text(
        json.dumps(_call_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    return results


if __name__ == "__main__":
    run()
    print(f"Done. Output written to {ISSUE_DIR}")

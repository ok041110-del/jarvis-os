"""QQQ ETF Analysis runner — 첫 ETF Dogfooding.

raw_data.md(이 세션이 WebSearch로 미리 수집한 실제 데이터) -> 7개 전문 분석
(Composition/Holdings/Cost/Performance/Exposure/Distribution/Macro) -> Bull
Case/Bear Case -> Synthesis -> Final Report. 각 단계는 `agents.py`의 함수를
순서대로 직접 호출하는 하드코딩된 흐름이다 — Workflow Parser/Scheduler/
Dispatcher를 만들지 않는다(Stock Dogfooding runner.py와 동일한 성격).

Stock runner.py와 마찬가지로 각 호출의 입력 길이/출력 길이/소요 시간을
`call_log.json`에 기록해, Stock과 ETF 간 Context 규모 차이를 정량적으로
비교할 수 있게 한다.

이 파일은 Development HQ(`development-hq/mvp`)를 수정하지 않는다.
"""

import json
import time
from pathlib import Path

from agents import (
    bear_researcher_bear_case,
    bull_researcher_bull_case,
    composition_analyst_composition_analysis,
    cost_analyst_cost_analysis,
    distribution_analyst_distribution_analysis,
    exposure_analyst_exposure_analysis,
    holdings_analyst_holdings_analysis,
    macro_analyst_macro_analysis,
    performance_analyst_performance_analysis,
    report_writer_final_report,
    synthesis_judgment,
)

PROJECT_ROOT = Path(__file__).resolve().parent
ISSUE_DIR = PROJECT_ROOT / "issues" / "0001-qqq-analysis"
RAW_DATA_PATH = ISSUE_DIR / "raw_data.md"

_SECTION_TAGS = [
    "[COMPOSITION]",
    "[HOLDINGS]",
    "[COST]",
    "[PERFORMANCE]",
    "[SECTOR]",
    "[DISTRIBUTION]",
    "[MACRO]",
]

_FUND_HEADER = "Fund: Invesco QQQ Trust, Series 1 (Ticker: QQQ, tracks Nasdaq-100 Index)"

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
        tag: f"{_FUND_HEADER}\n\n{_extract_section(raw_text, tag)}"
        for tag in _SECTION_TAGS
    }

    composition = _timed(
        "composition_analyst_composition_analysis",
        composition_analyst_composition_analysis,
        f"{sections['[COMPOSITION]']}\n\n{limitation}",
    )
    holdings = _timed(
        "holdings_analyst_holdings_analysis",
        holdings_analyst_holdings_analysis,
        f"{sections['[HOLDINGS]']}\n\n{limitation}",
    )
    cost = _timed(
        "cost_analyst_cost_analysis",
        cost_analyst_cost_analysis,
        f"{sections['[COST]']}\n\n{limitation}",
    )
    performance = _timed(
        "performance_analyst_performance_analysis",
        performance_analyst_performance_analysis,
        f"{sections['[PERFORMANCE]']}\n\n{limitation}",
    )
    exposure = _timed(
        "exposure_analyst_exposure_analysis",
        exposure_analyst_exposure_analysis,
        f"{sections['[SECTOR]']}\n\n{limitation}",
    )
    distribution = _timed(
        "distribution_analyst_distribution_analysis",
        distribution_analyst_distribution_analysis,
        f"{sections['[DISTRIBUTION]']}\n\n{limitation}",
    )
    macro = _timed(
        "macro_analyst_macro_analysis",
        macro_analyst_macro_analysis,
        f"{sections['[MACRO]']}\n\n{limitation}",
    )

    all_analyses = (
        f"[COMPOSITION ANALYSIS]\n{composition}\n\n"
        f"[HOLDINGS ANALYSIS]\n{holdings}\n\n"
        f"[COST ANALYSIS]\n{cost}\n\n"
        f"[PERFORMANCE ANALYSIS]\n{performance}\n\n"
        f"[EXPOSURE ANALYSIS]\n{exposure}\n\n"
        f"[DISTRIBUTION ANALYSIS]\n{distribution}\n\n"
        f"[MACRO ANALYSIS]\n{macro}"
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
        composition,
        holdings,
        cost,
        performance,
        exposure,
        distribution,
        macro,
        bull_case,
        bear_case,
        synthesis,
    )

    results = {
        "composition_analysis.md": composition,
        "holdings_analysis.md": holdings,
        "cost_analysis.md": cost,
        "performance_analysis.md": performance,
        "exposure_analysis.md": exposure,
        "distribution_analysis.md": distribution,
        "macro_analysis.md": macro,
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

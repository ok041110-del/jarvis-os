"""Prototype A — Timeout 상향. `shared/agents.py`(Nestlé/Toyota와 동일한
7분석→Bull/Bear→Synthesis→Final Report, 11단계) 파이프라인을 그대로
쓰되, 각 Engine 호출의 timeout만 180초(Dev HQ 기본값) 대신
`RAISED_TIMEOUT_SECONDS`로 바꿔 실행한다.

`development-hq/mvp/engine.py`는 import하지 않는다 — `shared/agents.py`가
import한 진짜 `call_engine`을, 이 스크립트가 실행 시점에 프로세스
내부에서만 `call_engine_with_timeout`으로 바꿔치기(monkeypatch)한다.
`engine.py` 파일 자체, `ENGINE_TIMEOUT_SECONDS` 상수는 디스크 위에서
전혀 수정되지 않는다 — Dev HQ v1.0 Freeze 유지.

사용법: python3 runner_raised_timeout.py <trial_id> <raised_timeout_seconds>
"""

import functools
import json
import sys
import time
from pathlib import Path

PROTO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROTO_ROOT / "shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import agents  # noqa: E402  (shared/agents.py)
from call_engine_prototype import call_engine_with_timeout  # noqa: E402

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


def run(issue_dir: Path) -> dict:
    raw_text = RAW_DATA_PATH.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")

    sections = {
        tag: f"{_COMPANY_HEADER}\n\n{_extract_section(raw_text, tag)}"
        for tag in _SECTION_TAGS
    }

    fundamental = _timed(
        "fundamental_analyst_fundamental_analysis",
        agents.fundamental_analyst_fundamental_analysis,
        f"{sections['[FUNDAMENTAL]']}\n\n{limitation}",
    )
    dividend_quality = _timed(
        "dividend_quality_analyst_dividend_quality_analysis",
        agents.dividend_quality_analyst_dividend_quality_analysis,
        f"{sections['[DIVIDEND_QUALITY]']}\n\n{limitation}",
    )
    valuation = _timed(
        "valuation_analyst_valuation_analysis",
        agents.valuation_analyst_valuation_analysis,
        f"{sections['[VALUATION]']}\n\n{limitation}",
    )
    technical = _timed(
        "technical_analyst_technical_analysis",
        agents.technical_analyst_technical_analysis,
        f"{sections['[TECHNICAL]']}\n\n{limitation}",
    )
    industry = _timed(
        "industry_analyst_industry_analysis",
        agents.industry_analyst_industry_analysis,
        f"{sections['[INDUSTRY]']}\n\n{limitation}",
    )
    news_event = _timed(
        "news_analyst_news_event_analysis",
        agents.news_analyst_news_event_analysis,
        f"{sections['[NEWS/EVENT]']}\n\n{limitation}",
    )
    sentiment = _timed(
        "sentiment_analyst_sentiment_analysis",
        agents.sentiment_analyst_sentiment_analysis,
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
        "bull_researcher_bull_case", agents.bull_researcher_bull_case, all_analyses
    )
    bear_case = _timed(
        "bear_researcher_bear_case", agents.bear_researcher_bear_case, all_analyses
    )
    synthesis = _timed(
        "synthesis_judgment", agents.synthesis_judgment, bull_case, bear_case
    )
    final_report = _timed(
        "report_writer_final_report",
        agents.report_writer_final_report,
        fundamental, dividend_quality, valuation, technical,
        industry, news_event, sentiment, bull_case, bear_case, synthesis,
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
    issue_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in results.items():
        (issue_dir / filename).write_text(content.rstrip() + "\n", encoding="utf-8")

    (issue_dir / "call_log.json").write_text(
        json.dumps(_call_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    trial_id = sys.argv[1] if len(sys.argv) > 1 else "trial"
    raised_timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 400

    # 여기서만 call_engine을 바꿔치기한다 — shared/agents.py 파일 자체는
    # 수정하지 않는다(프로세스 내부 바인딩 교체일 뿐).
    agents.call_engine = functools.partial(
        call_engine_with_timeout, timeout_seconds=raised_timeout
    )

    issue_dir = PROTO_ROOT / "trials" / f"raised_timeout_{trial_id}"
    t0 = time.monotonic()
    status = "success"
    try:
        run(issue_dir)
    except Exception as e:
        status = f"failed: {type(e).__name__}: {e}"
        raise
    finally:
        elapsed_total = time.monotonic() - t0
        summary = {
            "variant": "raised_timeout",
            "trial_id": trial_id,
            "timeout_seconds": raised_timeout,
            "status": status,
            "elapsed_total_sec": round(elapsed_total, 1),
            "steps_completed": len(_call_log),
        }
        summary_path = PROTO_ROOT / "trials" / f"raised_timeout_{trial_id}_summary.json"
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))

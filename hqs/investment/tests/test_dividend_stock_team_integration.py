"""Dividend Stock Team Integration Test — `test_stock_team_integration.py`와
동일한 검증을 Dividend Stock Team(7개 분석 역할)에 대해 수행한다."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "teams"))

import dividend_stock_team  # noqa: E402

RAW_DATA = """# Raw Data — TEST

## [FUNDAMENTAL] 테스트 실적
매출 성장 데이터.

## [DIVIDEND_QUALITY] 테스트 배당 데이터
배당 지속가능성 데이터.

## [VALUATION] 테스트 밸류에이션
P/E 데이터.

## [TECHNICAL] 테스트 기술적 지표
이동평균 데이터.

## [INDUSTRY] 테스트 산업 데이터
시장 점유율 데이터.

## [NEWS/EVENT] 테스트 뉴스
최근 이벤트.

## [SENTIMENT] 테스트 심리 데이터
애널리스트 등급.

## 데이터 한계
스냅샷 시점 데이터.
"""

TRADER_OUTPUT = """## REPORT

Bull and bear agree on the facts, disagree on interpretation only.

## DECISION

- **Direction:** HOLD
- **Rationale:** Balanced evidence, no clean directional edge.
- **Reassess when:** FCF dividend coverage disclosure.
"""


def _fake_call_engine(prompt: str) -> str:
    marker = prompt.split(":", 1)[0]
    if marker == "TRADER":
        return TRADER_OUTPUT
    if marker == "FINAL_REPORT":
        assert "Direction:" not in prompt
        return "# Final Report\n\nDisclaimer: not investment advice."
    return f"{marker} body."


def test_run_wires_trader_between_synthesis_and_final_report(tmp_path, monkeypatch):
    monkeypatch.setattr(dividend_stock_team, "call_engine", _fake_call_engine)

    raw_data_path = tmp_path / "raw_data.md"
    raw_data_path.write_text(RAW_DATA, encoding="utf-8")
    issue_dir = tmp_path / "issue"

    result = dividend_stock_team.run("TESTCO", raw_data_path, issue_dir)

    synthesis_saved = (issue_dir / "synthesis.md").read_text(encoding="utf-8")
    decision_saved = (issue_dir / "trader_decision.md").read_text(encoding="utf-8")
    assert "Direction:" not in synthesis_saved
    assert "Direction:" in decision_saved
    assert (issue_dir / "checkpoints" / "trader_decision.md").exists()

    decision_parsed = result["wave_summary"]["trader_decision"]
    assert decision_parsed["action"] == "HOLD"
    assert decision_parsed["warnings"] == []

    final_report = (issue_dir / "final_report.md").read_text(encoding="utf-8")
    assert "Direction:" not in final_report

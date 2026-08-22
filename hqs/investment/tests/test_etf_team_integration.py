"""ETF Team Integration Test — `test_stock_team_integration.py`와 동일한
검증을 ETF Team(6개 분석 역할)에 대해 수행한다."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "teams"))

import etf_team  # noqa: E402

RAW_DATA = """# Raw Data — TEST

## [COMPOSITION] 테스트 구성
지수 추종 방식 데이터.

## [HOLDINGS_EXPOSURE] 테스트 보유종목
상위 종목 데이터.

## [COST_TRACKING] 테스트 비용
추적오차 데이터.

## [PERFORMANCE_RISK] 테스트 성과
변동성 데이터.

## [DISTRIBUTION] 테스트 분배금
배당 데이터.

## [MACRO] 테스트 매크로
금리 데이터.

## 데이터 한계
스냅샷 시점 데이터.
"""

TRADER_OUTPUT = """## REPORT

Bull and bear agree on the facts, disagree on interpretation only.

## DECISION

- **Direction:** HOLD
- **Rationale:** Balanced evidence, no clean directional edge.
- **Reassess when:** Fed rate path resolution.
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
    monkeypatch.setattr(etf_team, "call_engine", _fake_call_engine)

    raw_data_path = tmp_path / "raw_data.md"
    raw_data_path.write_text(RAW_DATA, encoding="utf-8")
    issue_dir = tmp_path / "issue"

    result = etf_team.run("TESTFUND", raw_data_path, issue_dir)

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

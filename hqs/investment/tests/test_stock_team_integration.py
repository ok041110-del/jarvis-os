"""Stock Team Integration Test — Bull/Bear -> Trader(REPORT/DECISION) ->
Final Report 데이터 흐름을 실제 `run()` 호출로 검증한다. Engine은
Mock으로 대체한다(비용/시간 문제로 Unit 단계에서는 실제 Engine을 쓰지
않는다 — 실제 Engine 검증은 Dogfooding 단계(§15)에서 별도로 한다).

검증 대상:
- Wave1~4가 정상적으로 이어지는가(Synthesis/Trader 단계가 하나로
  합쳐졌어도 나머지 Wave 구조는 그대로인가).
- DECISION이 Final Report 생성 프롬프트에 섞여 들어가지 않는가
  (사용자 지시 §7 "REPORT 영역에는 Trader의 방향 판단이 섞이지
  않도록" — 코드 레벨로 확인).
- `synthesis.md`/`trader_decision.md`가 분리 저장되는가.
- Resume 시 Trader 단계가 재호출되지 않는가.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "teams"))

import stock_team  # noqa: E402

RAW_DATA = """# Raw Data — TEST

## [FUNDAMENTAL] 테스트 실적
매출 성장 데이터.

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
- **Reassess when:** Next quarter's guidance clarity.
"""


def _fake_call_engine(prompt: str) -> str:
    marker = prompt.split(":", 1)[0]
    if marker == "TRADER":
        return TRADER_OUTPUT
    if marker == "FINAL_REPORT":
        assert "DECISION" not in prompt, "DECISION 텍스트가 Final Report 프롬프트에 섞였다"
        assert "Direction:" not in prompt, "Trader 방향 판단이 Final Report 프롬프트에 섞였다"
        return "# Final Report\n\nDisclaimer: not investment advice."
    if marker == "BULL_CASE":
        return "Bull case body."
    if marker == "BEAR_CASE":
        return "Bear case body."
    # 5개 Analyst 호출 전부 동일한 최소 응답으로 충분(분석 품질은 이 테스트의 대상이 아님)
    return f"{marker} body."


def test_run_wires_trader_between_synthesis_and_final_report(tmp_path, monkeypatch):
    monkeypatch.setattr(stock_team, "call_engine", _fake_call_engine)

    raw_data_path = tmp_path / "raw_data.md"
    raw_data_path.write_text(RAW_DATA, encoding="utf-8")
    issue_dir = tmp_path / "issue"

    result = stock_team.run("TESTCO", raw_data_path, issue_dir)

    # 1) synthesis.md는 REPORT만, trader_decision.md는 DECISION만 담는다(분리 확인)
    synthesis_saved = (issue_dir / "synthesis.md").read_text(encoding="utf-8")
    decision_saved = (issue_dir / "trader_decision.md").read_text(encoding="utf-8")
    assert "Bull and bear agree" in synthesis_saved
    assert "Direction:" not in synthesis_saved
    assert "Direction:" in decision_saved

    # 2) checkpoint는 "trader_decision" 하나로 통합(별도 "synthesis" 체크포인트 없음)
    assert (issue_dir / "checkpoints" / "trader_decision.md").exists()
    assert not (issue_dir / "checkpoints" / "synthesis.md").exists()

    # 3) wave_summary에 파싱된 Decision이 담긴다
    decision_parsed = result["wave_summary"]["trader_decision"]
    assert decision_parsed["action"] == "HOLD"
    assert decision_parsed["warnings"] == []

    # 4) Final Report는 정상 생성되고 DECISION 텍스트를 담지 않는다
    final_report = (issue_dir / "final_report.md").read_text(encoding="utf-8")
    assert "Direction:" not in final_report


def test_resume_does_not_recall_trader(tmp_path, monkeypatch):
    calls = {"trader": 0}

    def counting_call_engine(prompt: str) -> str:
        marker = prompt.split(":", 1)[0]
        if marker == "TRADER":
            calls["trader"] += 1
        return _fake_call_engine(prompt)

    monkeypatch.setattr(stock_team, "call_engine", counting_call_engine)

    raw_data_path = tmp_path / "raw_data.md"
    raw_data_path.write_text(RAW_DATA, encoding="utf-8")
    issue_dir = tmp_path / "issue"

    stock_team.run("TESTCO", raw_data_path, issue_dir)
    assert calls["trader"] == 1

    # 두 번째 실행(Resume) — Trader 단계가 이미 checkpoint에 있으므로 재호출되면 안 된다
    stock_team.run("TESTCO", raw_data_path, issue_dir)
    assert calls["trader"] == 1

"""Wave1/Wave2 Task 실패 격리 테스트 — ThreadPoolExecutor 동시 실행 중
하나가 ContentFailureError를 던져도 나머지 Task는 정상 완료·저장되고,
Resume 시 실패한 Task만 재실행되는지 실제 stock_team.run()으로 검증한다.
etf_team/dividend_stock_team은 동일한 Wave 구조를 재사용하므로 stock_team이
대표 사례다(STRUCTURE.md "신규 표준 실행 패턴 재사용" 참조)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "teams"))

import stock_team  # noqa: E402
from checkpoint import ContentFailureError  # noqa: E402

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

WAVE1_MARKERS = [
    "FUNDAMENTAL_ANALYSIS",
    "TECHNICAL_ANALYSIS",
    "INDUSTRY_ANALYSIS",
    "NEWS_EVENT_ANALYSIS",
    "SENTIMENT_ANALYSIS",
]
WAVE1_STEPS = [
    "fundamental_analysis",
    "technical_analysis",
    "industry_analysis",
    "news_event_analysis",
    "sentiment_analysis",
]


def _load_manifest(issue_dir: Path) -> dict:
    return json.loads((issue_dir / "checkpoints" / "manifest.json").read_text(encoding="utf-8"))


def test_wave1_single_failure_isolates_siblings(tmp_path, monkeypatch):
    def fake_call_engine(prompt: str) -> str:
        marker = prompt.split(":", 1)[0]
        if marker == "TECHNICAL_ANALYSIS":
            return "API Error: rate limited"
        return f"{marker} body."

    monkeypatch.setattr(stock_team, "call_engine", fake_call_engine)

    raw_data_path = tmp_path / "raw_data.md"
    raw_data_path.write_text(RAW_DATA, encoding="utf-8")
    issue_dir = tmp_path / "issue"

    with pytest.raises(ContentFailureError):
        stock_team.run("TESTCO", raw_data_path, issue_dir)

    manifest = _load_manifest(issue_dir)
    checkpoints_dir = issue_dir / "checkpoints"

    assert "technical_analysis" not in manifest["completed_steps"]
    assert not (checkpoints_dir / "technical_analysis.md").exists()

    other_steps = [s for s in WAVE1_STEPS if s != "technical_analysis"]
    for step in other_steps:
        assert step in manifest["completed_steps"]
        assert (checkpoints_dir / f"{step}.md").exists()

    assert len(manifest["completed_steps"]) == len(other_steps)
    assert len(set(manifest["completed_steps"])) == len(other_steps)
    assert len(manifest["call_log"]) == len(other_steps)


def test_wave1_resume_retries_only_failed_step(tmp_path, monkeypatch):
    calls = []
    fail = {"active": True}

    def fake_call_engine(prompt: str) -> str:
        marker = prompt.split(":", 1)[0]
        calls.append(marker)
        if marker == "TECHNICAL_ANALYSIS" and fail["active"]:
            return "API Error: rate limited"
        if marker == "TRADER":
            return TRADER_OUTPUT
        return f"{marker} body."

    monkeypatch.setattr(stock_team, "call_engine", fake_call_engine)

    raw_data_path = tmp_path / "raw_data.md"
    raw_data_path.write_text(RAW_DATA, encoding="utf-8")
    issue_dir = tmp_path / "issue"

    with pytest.raises(ContentFailureError):
        stock_team.run("TESTCO", raw_data_path, issue_dir)

    fail["active"] = False
    calls.clear()
    stock_team.run("TESTCO", raw_data_path, issue_dir)

    assert calls.count("TECHNICAL_ANALYSIS") == 1
    for marker in WAVE1_MARKERS:
        if marker != "TECHNICAL_ANALYSIS":
            assert marker not in calls, f"{marker}는 이미 완료된 Task이므로 재호출되면 안 됨"

    manifest = _load_manifest(issue_dir)
    assert sorted(manifest["completed_steps"]).count("technical_analysis") == 1
    for step in WAVE1_STEPS:
        assert manifest["completed_steps"].count(step) == 1


def test_wave2_single_failure_isolates_other_branch(tmp_path, monkeypatch):
    def fake_call_engine(prompt: str) -> str:
        marker = prompt.split(":", 1)[0]
        if marker == "BEAR_CASE":
            return "API Error: rate limited"
        return f"{marker} body."

    monkeypatch.setattr(stock_team, "call_engine", fake_call_engine)

    raw_data_path = tmp_path / "raw_data.md"
    raw_data_path.write_text(RAW_DATA, encoding="utf-8")
    issue_dir = tmp_path / "issue"

    with pytest.raises(ContentFailureError):
        stock_team.run("TESTCO", raw_data_path, issue_dir)

    manifest = _load_manifest(issue_dir)
    checkpoints_dir = issue_dir / "checkpoints"

    for step in WAVE1_STEPS:
        assert step in manifest["completed_steps"]

    assert "bull_case" in manifest["completed_steps"]
    assert (checkpoints_dir / "bull_case.md").exists()
    assert "bear_case" not in manifest["completed_steps"]
    assert not (checkpoints_dir / "bear_case.md").exists()

    assert len(manifest["completed_steps"]) == len(set(manifest["completed_steps"]))


def test_wave2_resume_retries_only_failed_branch(tmp_path, monkeypatch):
    calls = []
    fail = {"active": True}

    def fake_call_engine(prompt: str) -> str:
        marker = prompt.split(":", 1)[0]
        calls.append(marker)
        if marker == "BEAR_CASE" and fail["active"]:
            return "API Error: rate limited"
        if marker == "TRADER":
            return TRADER_OUTPUT
        return f"{marker} body."

    monkeypatch.setattr(stock_team, "call_engine", fake_call_engine)

    raw_data_path = tmp_path / "raw_data.md"
    raw_data_path.write_text(RAW_DATA, encoding="utf-8")
    issue_dir = tmp_path / "issue"

    with pytest.raises(ContentFailureError):
        stock_team.run("TESTCO", raw_data_path, issue_dir)

    fail["active"] = False
    calls.clear()
    stock_team.run("TESTCO", raw_data_path, issue_dir)

    assert calls.count("BEAR_CASE") == 1
    assert "BULL_CASE" not in calls, "BULL_CASE는 이미 완료된 Task이므로 재호출되면 안 됨"
    for marker in WAVE1_MARKERS:
        assert marker not in calls, f"{marker}는 이미 완료된 Task이므로 재호출되면 안 됨"

    manifest = _load_manifest(issue_dir)
    assert manifest["completed_steps"].count("bear_case") == 1
    assert manifest["completed_steps"].count("bull_case") == 1
    assert len(manifest["completed_steps"]) == len(set(manifest["completed_steps"]))

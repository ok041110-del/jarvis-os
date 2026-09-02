"""`hqs/investment/trader.py`의 REPORT/DECISION 분리·파싱 Unit Test.
Engine을 호출하지 않고 실제 산출물 형태의 고정 입력만 사용한다."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checkpoint import Checkpointer  # noqa: E402
from trader import (  # noqa: E402
    TraderOutputError,
    parse_decision,
    run_trader_decision,
    split_report_decision,
)

# 실제 Engine 산출물(aapl_trader_expanded.md)에서 그대로 가져온 형태.
REAL_TRADER_OUTPUT = """## REPORT

**Where the two cases actually disagree on facts: nowhere significant**

Bull and bear draw from the same figures.

## DECISION

- **Direction:** HOLD
- **Rationale:** The two cases agree on nearly all underlying facts and \
differ mainly in interpretive weighting rather than in the data itself.
- **Reassess when:** Whether the Services miss reflects a one-quarter \
timing issue or the start of a trend break.
"""


def test_split_report_decision_real_shape():
    report, decision = split_report_decision(REAL_TRADER_OUTPUT)
    assert report.startswith("**Where the two cases")
    assert "## REPORT" not in report and "## DECISION" not in report
    assert decision.startswith("- **Direction:**")


def test_split_report_decision_missing_headers_raises():
    with pytest.raises(TraderOutputError):
        split_report_decision("no headers here at all")


def test_split_report_decision_wrong_order_raises():
    with pytest.raises(TraderOutputError):
        split_report_decision("## DECISION\nfoo\n## REPORT\nbar")


def test_parse_decision_extracts_all_fields():
    _, decision = split_report_decision(REAL_TRADER_OUTPUT)
    parsed = parse_decision(decision)
    assert parsed["action"] == "HOLD"
    assert "interpretive weighting" in parsed["rationale"]
    assert "Services miss" in parsed["reassessment_trigger"]
    assert parsed["warnings"] == []


def test_parse_decision_recognizes_buy_and_sell():
    buy_text = "- Direction: BUY\n- Rationale: strong case.\n- Reassess when: X."
    sell_text = "- Direction: SELL\n- Rationale: weak case.\n- Reassess when: Y."
    assert parse_decision(buy_text)["action"] == "BUY"
    assert parse_decision(sell_text)["action"] == "SELL"


def test_parse_decision_missing_fields_are_warned_not_raised():
    parsed = parse_decision("no structured fields at all")
    assert parsed["action"] is None
    assert parsed["rationale"] is None
    assert parsed["reassessment_trigger"] is None
    assert set(parsed["warnings"]) == {
        "action missing or unrecognized",
        "rationale missing",
        "reassessment_trigger missing",
    }


def test_parse_decision_partial_fields():
    text = "- Direction: HOLD\n- Rationale: balanced evidence on both sides."
    parsed = parse_decision(text)
    assert parsed["action"] == "HOLD"
    assert parsed["rationale"] == "balanced evidence on both sides."
    assert parsed["reassessment_trigger"] is None
    assert parsed["warnings"] == ["reassessment_trigger missing"]


def test_parse_decision_ambiguous_direction_is_deterministic():
    """Direction 텍스트에 방향 단어가 둘 이상 섞여도(모호한 Engine 응답)
    `_VALID_ACTIONS` 우선순위(BUY > SELL > HOLD)로 항상 동일한 값을 고른다
    — set 순회였을 때는 프로세스 문자열 해시 랜덤화에 따라 달라질 수 있었다."""
    text = "- Direction: BUY leaning SELL or HOLD\n- Rationale: r.\n- Reassess when: q."
    for _ in range(20):
        assert parse_decision(text)["action"] == "BUY"


def test_run_trader_decision_saves_only_after_validation(tmp_path):
    """형식이 올바른 출력은 검증 후 정상 저장된다."""
    cp = Checkpointer(tmp_path)

    def fn(bull_case, bear_case):
        return REAL_TRADER_OUTPUT

    result = run_trader_decision(cp, fn, "bull", "bear")

    assert result == REAL_TRADER_OUTPUT
    assert cp.has("trader_decision") is True


def test_run_trader_decision_malformed_output_is_not_checkpointed(tmp_path):
    """REPORT/DECISION 헤더가 없는 malformed 출력은 checkpoint 저장 전에
    `TraderOutputError`가 발생해야 한다 — 저장 후에 발생하면 다음 실행에서
    같은 malformed 텍스트를 그대로 다시 읽어 영구적으로 동일하게 실패한다."""
    cp = Checkpointer(tmp_path)

    def fn(bull_case, bear_case):
        return "no headers here at all"

    with pytest.raises(TraderOutputError):
        run_trader_decision(cp, fn, "bull", "bear")

    assert cp.has("trader_decision") is False
    assert not (tmp_path / "checkpoints" / "trader_decision.md").exists()


def test_run_trader_decision_retries_after_malformed_output(tmp_path):
    """malformed 출력 이후 재실행하면(같은 issue_dir에서 새 Checkpointer로
    재개) `trader_decision_fn`이 다시 호출돼 정상 출력으로 회복된다 —
    이 회복이 새 재시도 로직이 아니라 checkpoint의 기존 Resume 동작만으로
    성립한다는 것을 확인한다."""
    cp = Checkpointer(tmp_path)
    calls = {"n": 0}

    def failing_fn(bull_case, bear_case):
        calls["n"] += 1
        return "no headers here at all"

    with pytest.raises(TraderOutputError):
        run_trader_decision(cp, failing_fn, "bull", "bear")
    assert calls["n"] == 1

    cp2 = Checkpointer(tmp_path)

    def recovered_fn(bull_case, bear_case):
        calls["n"] += 1
        return REAL_TRADER_OUTPUT

    result = run_trader_decision(cp2, recovered_fn, "bull", "bear")

    assert result == REAL_TRADER_OUTPUT
    assert calls["n"] == 2
    assert cp2.has("trader_decision") is True

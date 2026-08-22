"""`hqs/investment/trader.py`의 REPORT/DECISION 분리·파싱 Unit Test.
Engine을 호출하지 않고 실제 산출물 형태의 고정 입력만 사용한다."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from trader import TraderOutputError, parse_decision, split_report_decision  # noqa: E402

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

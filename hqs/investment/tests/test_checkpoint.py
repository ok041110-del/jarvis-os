"""`hqs/investment/checkpoint.py`의 콘텐츠 실패 감지 통합 테스트.

`projects/investment-hq-checkpoint-detection-prototype/`에서 검증된
감지 로직(Feasibility PASS)이 `checkpoint.py`에 최소 통합된 뒤에도
실패 감지·저장 차단·정상 저장·Resume 네 가지 동작이 실제로 성립하는지
확인한다. 재시도/알림/동시성은 다루지 않는다(범위 밖).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checkpoint import Checkpointer, ContentFailureError, run_step  # noqa: E402

# efa-2026-08, pg-hq-verify 양쪽에서 토씨 하나 다르지 않게 재현된 실제 관찰값.
KNOWN_FAILURE_TEXT = (
    "API Error: Unable to connect to API: Self-signed certificate detected. "
    "Check your proxy or corporate SSL certificates"
)


def test_known_failure_blocks_save(tmp_path):
    cp = Checkpointer(tmp_path)
    calls = []

    def fn(data):
        calls.append(data)
        return KNOWN_FAILURE_TEXT

    with pytest.raises(ContentFailureError):
        run_step(cp, "synthesis", fn, "input data")

    assert calls == ["input data"]  # fn은 실제로 호출됨(Engine 호출 자체는 발생)
    assert not (tmp_path / "checkpoints" / "synthesis.md").exists()
    assert cp.has("synthesis") is False
    assert cp.manifest["completed_steps"] == []
    assert cp.manifest["call_log"] == []


def test_success_path_saves_normally(tmp_path):
    cp = Checkpointer(tmp_path)

    def fn(data):
        return "정상 분석 결과 본문"

    result = run_step(cp, "fundamental_analysis", fn, "input data")

    assert result == "정상 분석 결과 본문"
    assert cp.has("fundamental_analysis") is True
    saved = (tmp_path / "checkpoints" / "fundamental_analysis.md").read_text(encoding="utf-8")
    assert saved.strip() == "정상 분석 결과 본문"
    assert cp.manifest["completed_steps"] == ["fundamental_analysis"]
    assert len(cp.manifest["call_log"]) == 1


def test_resume_skips_second_engine_call(tmp_path):
    cp = Checkpointer(tmp_path)
    call_count = {"n": 0}

    def fn(data):
        call_count["n"] += 1
        return "정상 분석 결과 본문"

    run_step(cp, "technical_analysis", fn, "input data")
    assert call_count["n"] == 1

    # 재실행(같은 issue_dir에서 새 Checkpointer로 재개하는 실제 시나리오 재현)
    cp2 = Checkpointer(tmp_path)

    def fn_should_not_be_called(data):
        raise AssertionError("Resume 시 fn이 다시 호출되면 안 된다")

    result = run_step(cp2, "technical_analysis", fn_should_not_be_called, "input data")
    assert result.strip() == "정상 분석 결과 본문"  # save()가 trailing newline을 붙인다(기존 동작)
    assert call_count["n"] == 1


def test_failed_step_is_retried_on_resume(tmp_path):
    """실패한 단계는 저장되지 않으므로, 재실행 시 정상적으로 재시도된다
    (자동 재시도 로직을 추가한 것이 아니라, 기존 Resume 동작이 그대로
    적용될 뿐임을 확인한다)."""
    cp = Checkpointer(tmp_path)

    with pytest.raises(ContentFailureError):
        run_step(cp, "synthesis", lambda data: KNOWN_FAILURE_TEXT, "input data")

    cp2 = Checkpointer(tmp_path)
    result = run_step(cp2, "synthesis", lambda data: "복구된 정상 Synthesis", "input data")

    assert result == "복구된 정상 Synthesis"
    assert cp2.has("synthesis") is True


def test_partial_api_mention_is_not_false_positive(tmp_path):
    """본문 중간에 'api'를 부분 문자열로 포함하는 정상 콘텐츠(예: 'capital')는
    오탐하지 않는다 — Prototype EVIDENCE에서 실제 checkpoint 파일로 확인된
    케이스."""
    cp = Checkpointer(tmp_path)

    def fn(data):
        return "Operating margin premium reflects PG's capital efficiency."

    result = run_step(cp, "valuation_analysis", fn, "input data")
    assert cp.has("valuation_analysis") is True
    assert "capital" in result

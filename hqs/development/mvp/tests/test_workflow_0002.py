"""Characterization tests for `mvp.workflow_0002.run_mvp_0002` (P1-2).

이 테스트는 현재 behavior를 고정(lock)하기 위한 것이며, Production
code(`workflow_0002.py`)는 이 테스트 작성 과정에서 전혀 수정하지
않았다. 외부 Engine 호출은 결정적 테스트를 위해 `workflow_0002`의
`backend_agent_code_review`/`qa_agent_test_execution` 지점에서 전부
mock/stub한다 — `test_mvp_0001.py`(real-Engine 통합 테스트)와는
다른 목적의 테스트다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp import workflow_0002
from mvp.agents import NO_ISSUES_MARKER

SAMPLE_CODE = "def add(a, b):\n    return a + b\n"


def test_happy_path_with_issues_returns_review_and_test_cases(monkeypatch):
    """이슈가 있는 리뷰(마커 없음) -> test_execution이 정상 호출됨."""
    calls = []

    def fake_review(code):
        calls.append(("review", code))
        return "Found an issue: missing type hints."

    def fake_test_execution(code, review):
        calls.append(("test_execution", code, review))
        return "Test case: add(1, 2) == 3"

    monkeypatch.setattr(workflow_0002, "backend_agent_code_review", fake_review)
    monkeypatch.setattr(workflow_0002, "qa_agent_test_execution", fake_test_execution)

    result = workflow_0002.run_mvp_0002(SAMPLE_CODE)

    assert result == {
        "code_review": "Found an issue: missing type hints.",
        "test_execution": "Test case: add(1, 2) == 3",
    }
    assert calls == [
        ("review", SAMPLE_CODE),
        ("test_execution", SAMPLE_CODE, "Found an issue: missing type hints."),
    ]


def test_no_issues_branch_skips_test_execution_and_strips_marker(monkeypatch):
    """마커가 리뷰 마지막 줄에 있으면 test_execution을 건너뛰고, 반환되는
    code_review에서 마커를 제거한다."""
    review_with_marker = f"The code looks good.\n\n{NO_ISSUES_MARKER}"
    test_execution_called = []

    def fake_review(code):
        return review_with_marker

    def fake_test_execution(code, review):
        test_execution_called.append((code, review))
        return "SHOULD NOT BE CALLED"

    monkeypatch.setattr(workflow_0002, "backend_agent_code_review", fake_review)
    monkeypatch.setattr(workflow_0002, "qa_agent_test_execution", fake_test_execution)

    result = workflow_0002.run_mvp_0002(SAMPLE_CODE)

    assert test_execution_called == []
    assert result == {
        "code_review": "The code looks good.",
        "test_execution": "(생략됨: code_review에서 이슈가 발견되지 않아 test_execution을 건너뜀)",
    }


def test_marker_not_on_last_line_is_treated_as_having_issues(monkeypatch):
    """마커가 리뷰 안에 있지만 마지막 줄이 아니면 분기하지 않는다(현재
    `NO_ISSUES_MARKER in review` 판단은 위치를 가리지 않으므로 분기는
    타지만, `_strip_trailing_marker`는 원문을 그대로 반환한다는 것을
    고정한다)."""
    review_with_marker_mid = f"{NO_ISSUES_MARKER}\nBut here is more text after."

    def fake_review(code):
        return review_with_marker_mid

    def fake_test_execution(code, review):
        return "SHOULD NOT BE CALLED"

    monkeypatch.setattr(workflow_0002, "backend_agent_code_review", fake_review)
    monkeypatch.setattr(workflow_0002, "qa_agent_test_execution", fake_test_execution)

    result = workflow_0002.run_mvp_0002(SAMPLE_CODE)

    assert result["code_review"] == review_with_marker_mid
    assert result["test_execution"] == (
        "(생략됨: code_review에서 이슈가 발견되지 않아 test_execution을 건너뜀)"
    )


def test_engine_failure_in_code_review_returns_error_for_both_keys(monkeypatch):
    def raising_review(code):
        raise RuntimeError("boom")

    monkeypatch.setattr(workflow_0002, "backend_agent_code_review", raising_review)

    result = workflow_0002.run_mvp_0002(SAMPLE_CODE)

    assert result == {
        "code_review": "Engine call failed: boom",
        "test_execution": "Engine call failed: boom",
    }


def test_engine_failure_in_test_execution_returns_error_for_both_keys(monkeypatch):
    def fake_review(code):
        return "Found an issue."

    def raising_test_execution(code, review):
        raise TimeoutError("timed out")

    monkeypatch.setattr(workflow_0002, "backend_agent_code_review", fake_review)
    monkeypatch.setattr(workflow_0002, "qa_agent_test_execution", raising_test_execution)

    result = workflow_0002.run_mvp_0002(SAMPLE_CODE)

    assert result == {
        "code_review": "Engine call failed: timed out",
        "test_execution": "Engine call failed: timed out",
    }


def test_strip_trailing_marker_helper_no_marker_returns_original():
    text = "Just a normal review with no marker."
    assert workflow_0002._strip_trailing_marker(text, NO_ISSUES_MARKER) == text


def test_strip_trailing_marker_helper_marker_as_last_line_removed():
    text = f"Looks fine.\n\n{NO_ISSUES_MARKER}"
    assert workflow_0002._strip_trailing_marker(text, NO_ISSUES_MARKER) == "Looks fine."

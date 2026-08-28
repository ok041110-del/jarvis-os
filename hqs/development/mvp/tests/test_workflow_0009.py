"""Characterization tests for `mvp.workflow_0009` (P1-2):
`run_issue_to_planning_with_bundle`, `run_comparison`.

`run_comparison`의 Multi-Task 동시 실행 반영(`docs/architecture/core/ADR-0006-multi-task-minimal-responsibility-baseline.md`)
이후 외부 의존성은 계속 mock/stub한다.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from mvp import workflow_0009

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}
SAMPLE_BUNDLE = {
    "issue": SAMPLE_ISSUE,
    "goal": "Ship the thing.",
    "relevant_documents": [],
    "relevant_code": [],
    "relevant_observations": [],
    "relevant_decisions": [],
    "known_constraints": [],
    "open_questions": [],
}


def test_happy_path_returns_bundle_and_planning(monkeypatch):
    monkeypatch.setattr(workflow_0009, "build_context_bundle", lambda issue: SAMPLE_BUNDLE)
    monkeypatch.setattr(
        workflow_0009, "requirements_agent_requirement_analysis", lambda issue: "REQUIREMENT"
    )

    result = workflow_0009.run_issue_to_planning_with_bundle(SAMPLE_ISSUE)

    assert result == {"context_bundle": SAMPLE_BUNDLE, "planning": "REQUIREMENT"}


def test_engine_failure_preserves_bundle_and_fills_planning_error(monkeypatch):
    monkeypatch.setattr(workflow_0009, "build_context_bundle", lambda issue: SAMPLE_BUNDLE)

    def raising_requirement(issue):
        raise RuntimeError("boom")

    monkeypatch.setattr(workflow_0009, "requirements_agent_requirement_analysis", raising_requirement)

    result = workflow_0009.run_issue_to_planning_with_bundle(SAMPLE_ISSUE)

    assert result == {
        "context_bundle": SAMPLE_BUNDLE,
        "planning": "Engine call failed: boom",
    }


def test_render_context_bundle_includes_all_sections():
    rendered = workflow_0009._render_context_bundle(SAMPLE_BUNDLE)

    for heading in [
        "## Issue",
        "## Goal",
        "## Relevant Documents",
        "## Relevant Code",
        "## Relevant Observations",
        "## Relevant Decisions",
        "## Known Constraints",
        "## Open Questions",
    ]:
        assert heading in rendered


def test_render_context_bundle_empty_lists_render_placeholder():
    rendered = workflow_0009._render_context_bundle(SAMPLE_BUNDLE)
    assert rendered.count("- (없음)") == 6  # 6 of the 8 sections are empty lists in the fixture


def test_run_comparison_assembles_flat_and_bundled_results(monkeypatch):
    def fake_flat(issue):
        return {"context": {"a": 1}, "planning": "FLAT_PLANNING"}

    def fake_bundled(issue):
        return {"context_bundle": SAMPLE_BUNDLE, "planning": "BUNDLED_PLANNING"}

    monkeypatch.setattr(workflow_0009, "run_issue_to_planning", fake_flat)
    monkeypatch.setattr(workflow_0009, "run_issue_to_planning_with_bundle", fake_bundled)

    result = workflow_0009.run_comparison(SAMPLE_ISSUE)

    assert result == {
        "flat_context_planning": "FLAT_PLANNING",
        "context_bundle_planning": "BUNDLED_PLANNING",
        "context_bundle": SAMPLE_BUNDLE,
    }


def test_run_comparison_executes_branches_concurrently(monkeypatch):
    """flat/bundled 두 분기는 순차가 아니라 동시에 실행돼야 한다 —
    각각 0.2초씩 걸려도 총 소요 시간은 두 배가 아니라 한 번 분량에
    가까워야 한다(§16.4 Multi-Task 존재 근거 그 자체)."""

    def fake_flat(issue):
        time.sleep(0.2)
        return {"context": {}, "planning": "FLAT_PLANNING"}

    def fake_bundled(issue):
        time.sleep(0.2)
        return {"context_bundle": SAMPLE_BUNDLE, "planning": "BUNDLED_PLANNING"}

    monkeypatch.setattr(workflow_0009, "run_issue_to_planning", fake_flat)
    monkeypatch.setattr(workflow_0009, "run_issue_to_planning_with_bundle", fake_bundled)

    started = time.monotonic()
    result = workflow_0009.run_comparison(SAMPLE_ISSUE)
    elapsed = time.monotonic() - started

    assert result == {
        "flat_context_planning": "FLAT_PLANNING",
        "context_bundle_planning": "BUNDLED_PLANNING",
        "context_bundle": SAMPLE_BUNDLE,
    }
    assert elapsed < 0.35  # 순차 실행이었다면 0.4초 이상 걸린다


def test_run_comparison_other_branch_completes_despite_one_failure(monkeypatch):
    """한 분기가 처리되지 않은 예외를 던져도, 이미 동시에 시작된 다른
    분기의 실행 자체는 영향받지 않고 끝까지 완료돼야 한다(실패 격리)."""
    bundled_completed = []

    def raising_flat(issue):
        raise RuntimeError("boom")

    def fake_bundled(issue):
        time.sleep(0.1)
        bundled_completed.append(True)
        return {"context_bundle": SAMPLE_BUNDLE, "planning": "BUNDLED_PLANNING"}

    monkeypatch.setattr(workflow_0009, "run_issue_to_planning", raising_flat)
    monkeypatch.setattr(workflow_0009, "run_issue_to_planning_with_bundle", fake_bundled)

    with pytest.raises(RuntimeError, match="boom"):
        workflow_0009.run_comparison(SAMPLE_ISSUE)

    time.sleep(0.15)  # bundled의 Worker Thread가 끝날 시간을 준다
    assert bundled_completed == [True]


def test_run_comparison_retry_does_not_corrupt_previous_successful_result(monkeypatch):
    """실패 후 재시도(전체 함수 재호출)해도, 이전에 반환된 결과 객체가
    이후 호출에 의해 변형되지 않는다 — `run_comparison`은 상태를 갖지
    않으므로 두 번째 호출이 첫 번째 호출의 반환값을 훼손할 수 없다."""

    def fake_flat(issue):
        return {"context": {}, "planning": "FLAT_PLANNING"}

    def fake_bundled(issue):
        return {"context_bundle": SAMPLE_BUNDLE, "planning": "BUNDLED_PLANNING"}

    monkeypatch.setattr(workflow_0009, "run_issue_to_planning", fake_flat)
    monkeypatch.setattr(workflow_0009, "run_issue_to_planning_with_bundle", fake_bundled)

    first = workflow_0009.run_comparison(SAMPLE_ISSUE)
    first_snapshot = dict(first)

    second = workflow_0009.run_comparison(SAMPLE_ISSUE)

    assert first == first_snapshot
    assert second == first

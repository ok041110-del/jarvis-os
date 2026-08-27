"""Process Runtime Strategy — Experimental Validation.

`runtime-boundary` Prototype의 `rtb_runtime`/`rtb_task`를 그대로
재사용한다(중복 구현 금지). `hqs/development/mvp/tests/test_mvp_0001.py`
(실측 ~69초)는 자동 테스트 전체에서 단 한 번만 시작한다(RUNNING
관찰 + 최종 정확성 확인을 같은 테스트에서 함께 수행).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
RUNTIME_BOUNDARY_DIR = PROTOTYPE_DIR.parents[0] / "runtime-boundary"
sys.path.insert(0, str(PROTOTYPE_DIR))
sys.path.insert(0, str(RUNTIME_BOUNDARY_DIR))

import rtb_dashboard_view as dashboard_view  # noqa: E402
import rtb_task as task  # noqa: E402
from prs_dev_validation import DEV_HQ_TARGETS, EXPECTED_PASSED  # noqa: E402

CONTAMINATION_TARGET = "hqs/investment/tests/test_stock_team_integration.py"  # 2 tests, 실제 monkeypatch 오염 대상


def _wait_until_done(task_obj, timeout=90.0):
    deadline = time.monotonic() + timeout
    while task_obj.status in ("PENDING", "RUNNING") and time.monotonic() < deadline:
        time.sleep(0.02)
        task.refresh(task_obj.task_id)
    return task_obj


# --- 작업 지시 §2: 서로 다른 실제 Dev HQ Validation에 Process 반복 적용 ------

def test_process_strategy_accurate_across_repeated_different_dev_hq_targets():
    for name in ("ast_context", "stage_01"):
        target = DEV_HQ_TARGETS[name]
        expected = EXPECTED_PASSED[name]
        for _ in range(3):
            t = task.start(target, "process")
            _wait_until_done(t)
            assert t.status == "COMPLETED", f"{name} failed: {t.error}"
            assert t.result == (expected, 0), f"{name}: {t.result} != ({expected}, 0)"


def test_process_strategy_handles_long_running_dev_hq_validation():
    t = task.start(DEV_HQ_TARGETS["mvp_0001"], "process")
    assert t.status in ("PENDING", "RUNNING")  # 즉시 반환 확인(69초 작업이 즉시 끝났을 리 없음)
    _wait_until_done(t)
    assert t.status == "COMPLETED"
    assert t.result == (EXPECTED_PASSED["mvp_0001"], 0)


# --- 작업 지시 §1: 동일 Target 동시 실행 최소 재현 -----------------------------

def test_process_is_accurate_on_identical_target_concurrent_execution():
    for _ in range(3):
        t1 = task.start(CONTAMINATION_TARGET, "process")
        t2 = task.start(CONTAMINATION_TARGET, "process")
        _wait_until_done(t1)
        _wait_until_done(t2)
        assert t1.result == (2, 0)
        assert t2.result == (2, 0)


def test_thread_can_still_be_contaminated_on_identical_target():
    """`runtime-boundary` Evidence의 재확인 — 이 Prototype이 새로
    깨뜨린 게 아니라 여전히 사실인지 다시 확인한다."""

    contaminated = False
    for _ in range(5):
        t1 = task.start(CONTAMINATION_TARGET, "thread")
        t2 = task.start(CONTAMINATION_TARGET, "thread")
        _wait_until_done(t1)
        _wait_until_done(t2)
        combined = (t1.result[0] if t1.result else 0) + (t2.result[0] if t2.result else 0)
        if combined != 4:
            contaminated = True
            break
    assert contaminated, "5회 안에 재현되지 않음 — runtime-boundary Evidence 재확인 필요"


# --- 작업 지시 §3: 서로 다른 Target 동시 실행은 Thread로도 안전한가? --------

def test_different_dev_hq_targets_are_safe_under_thread_concurrency():
    """Dev HQ 내부의 서로 다른 두 실제 파일(둘 다 monkeypatch 없음)을
    Thread로 동시 실행해도 정확한지 3회 반복 확인 — Process가
    "동시 실행" 자체가 아니라 "동일 Target 동시 실행"에서만
    필요한지 구분하기 위함."""

    t1_target, t1_expected = DEV_HQ_TARGETS["ast_context"], EXPECTED_PASSED["ast_context"]
    t2_target, t2_expected = DEV_HQ_TARGETS["stage_01"], EXPECTED_PASSED["stage_01"]

    for _ in range(3):
        a = task.start(t1_target, "thread")
        b = task.start(t2_target, "thread")
        _wait_until_done(a)
        _wait_until_done(b)
        assert a.result == (t1_expected, 0)
        assert b.result == (t2_expected, 0)


def test_different_dev_hq_targets_also_correct_under_process():
    a = task.start(DEV_HQ_TARGETS["ast_context"], "process")
    b = task.start(DEV_HQ_TARGETS["stage_01"], "process")
    _wait_until_done(a)
    _wait_until_done(b)
    assert a.result == (EXPECTED_PASSED["ast_context"], 0)
    assert b.result == (EXPECTED_PASSED["stage_01"], 0)


# --- Sequential baseline과 Process 결과 일치 -----------------------------------

def test_sequential_and_process_results_match():
    seq = task.start(DEV_HQ_TARGETS["ast_context"], "sequential")
    proc = task.start(DEV_HQ_TARGETS["ast_context"], "process")
    _wait_until_done(proc)
    assert seq.result == proc.result == (EXPECTED_PASSED["ast_context"], 0)


# --- 작업 지시 §5: Failure/Retry, Dashboard Observe가 Process에서도 유지되는가 -

def test_failure_and_retry_still_work_under_process_strategy():
    failed = task.start("hqs/development/mvp/tests_does_not_exist", "process")
    _wait_until_done(failed)
    assert failed.status == "FAILED"
    assert failed.error is not None

    retried = task.retry(failed.task_id)
    assert retried.task_id != failed.task_id
    _wait_until_done(retried)
    assert retried.status == "FAILED"  # 같은 잘못된 대상이므로 다시 실패해야 정상


def test_dashboard_observes_process_tasks_same_as_before():
    t = task.start(DEV_HQ_TARGETS["stage_01"], "process")
    running = dashboard_view.list_running_tasks()
    assert any(r.task_id == t.task_id for r in running) or t.status == "COMPLETED"
    _wait_until_done(t)
    running_after = dashboard_view.list_running_tasks()
    assert not any(r.task_id == t.task_id for r in running_after)


# --- Boundary ------------------------------------------------------------------

def test_dev_validation_module_has_no_direct_hq_import():
    import ast

    tree = ast.parse((PROTOTYPE_DIR / "prs_dev_validation.py").read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    assert "hqs" not in modules
    assert "core" not in modules
    assert "mvp" not in modules

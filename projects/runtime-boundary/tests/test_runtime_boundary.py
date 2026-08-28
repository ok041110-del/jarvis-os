"""Runtime Boundary Prototype — Functional/Boundary Validation.

`hqs/investment/tests/test_stock_team_integration.py`(실측 0.03~0.13초,
2 passed)를 오염 재현의 최소 대상으로 쓴다 — in-process-async-command
Prototype이 발견한 오염(§8/§12, `hqs/investment/tests` 전체 16개 중
`monkeypatch` 충돌)을 가장 작은 실제 대상으로 재현한다(작업 지시 §1).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import rtb_dashboard_view as dashboard_view  # noqa: E402
import rtb_runtime as runtime  # noqa: E402
import rtb_task as task  # noqa: E402

CONTAMINATION_TARGET = "hqs/investment/tests/test_stock_team_integration.py"  # 2 tests, ~0.03s
FAST_TARGET = "hqs/investment/tests"  # 16 tests, <1s


def _wait_until_done(task_obj, timeout=5.0):
    deadline = time.monotonic() + timeout
    while task_obj.status in ("PENDING", "RUNNING") and time.monotonic() < deadline:
        time.sleep(0.02)
        task.refresh(task_obj.task_id)
    return task_obj


# --- Sequential: 블로킹, 즉시 완료 --------------------------------------------

def test_sequential_execution_is_blocking_and_immediately_completed():
    t = task.start(CONTAMINATION_TARGET, "sequential")
    assert t.status == "COMPLETED"
    assert t.result == (2, 0)


# --- Thread/Process: 즉시 반환(비동기) -----------------------------------------

def test_thread_execution_returns_without_blocking():
    t = task.start(FAST_TARGET, "thread")
    assert t.status in ("PENDING", "RUNNING")
    _wait_until_done(t)
    assert t.status == "COMPLETED"
    assert t.result == (16, 0)


def test_process_execution_returns_without_blocking():
    t = task.start(FAST_TARGET, "process")
    assert t.status in ("PENDING", "RUNNING")
    _wait_until_done(t)
    assert t.status == "COMPLETED"
    assert t.result == (16, 0)


# --- 핵심 비교: 동일 대상 동시 실행 — Thread vs Process ------------------------

def test_process_isolation_produces_correct_concurrent_results_on_identical_target():
    """Process 전략은 OS 프로세스 경계로 격리되므로, 동일 대상을 동시
    실행해도 오염되지 않아야 한다(여러 번 반복해 안정성을 확인)."""

    for _ in range(3):
        t1 = task.start(CONTAMINATION_TARGET, "process")
        t2 = task.start(CONTAMINATION_TARGET, "process")
        _wait_until_done(t1)
        _wait_until_done(t2)
        assert t1.result == (2, 0)
        assert t2.result == (2, 0)


def test_thread_execution_on_identical_target_can_produce_contaminated_results():
    """Thread 전략은 동일 프로세스 메모리를 공유하므로, 동일 대상을
    동시 실행하면 `monkeypatch` 상태가 섞여 결과가 오염될 수 있다
    (in-process-async-command Evidence §8 재확인). 확률적 현상이므로
    최대 5회 시도 안에 재현되는지 확인한다 — 5회 안에 재현되지
    않으면 이 Prototype이 주장하는 오염 자체가 사실이 아니라는
    뜻이므로 테스트를 실패시켜 정직하게 알린다."""

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

    assert contaminated, "5회 시도 안에 Thread 오염이 재현되지 않음 — Evidence 문서의 주장을 재확인 필요"


# --- Failure / Retry(Process 전략) --------------------------------------------

def test_failure_is_observable_with_process_strategy():
    t = task.start("hqs/investment/tests_does_not_exist", "process")
    _wait_until_done(t)
    assert t.status == "FAILED"
    assert t.error is not None
    assert t.result is None


def test_retry_reuses_target_and_strategy_and_produces_new_task():
    failed = task.start("hqs/investment/tests_does_not_exist", "process")
    _wait_until_done(failed)
    assert failed.status == "FAILED"

    retried = task.retry(failed.task_id)
    assert retried.task_id != failed.task_id
    assert retried.target == failed.target
    assert retried.strategy == failed.strategy
    _wait_until_done(retried)
    assert retried.status == "FAILED"  # 같은 잘못된 target을 재사용했으므로 다시 실패해야 정상


def test_retry_with_valid_target_after_fixing_succeeds():
    """Retry가 새 Task를 만든다는 것만 확인하는 것이 아니라, 실제로
    독립적인 새 실행을 만든다는 것을 올바른 대상으로도 확인한다."""

    t1 = task.start(CONTAMINATION_TARGET, "process")
    _wait_until_done(t1)
    assert t1.status == "COMPLETED"

    t2 = task.retry(t1.task_id)
    assert t2.task_id != t1.task_id
    _wait_until_done(t2)
    assert t2.status == "COMPLETED"
    assert t2.result == (2, 0)


# --- 동시 실행에서 Task 상태/결과 독립성(Process, 서로 다른 대상) -------------

def test_concurrent_tasks_on_different_targets_are_independent():
    t_fast = task.start(CONTAMINATION_TARGET, "process")
    t_slow = task.start(FAST_TARGET, "process")

    assert t_fast.status in ("PENDING", "RUNNING")
    assert t_slow.status in ("PENDING", "RUNNING")

    _wait_until_done(t_fast)
    _wait_until_done(t_slow)

    assert t_fast.result == (2, 0)
    assert t_slow.result == (16, 0)
    assert t_fast.task_id != t_slow.task_id


# --- Dashboard Observation(전략 무관) -------------------------------------------

def test_dashboard_observes_running_tasks_regardless_of_strategy():
    t_thread = task.start(FAST_TARGET, "thread")
    t_process = task.start(FAST_TARGET, "process")

    running = dashboard_view.list_running_tasks()
    running_ids = {t.task_id for t in running}
    assert t_thread.task_id in running_ids or t_thread.status == "COMPLETED"
    assert t_process.task_id in running_ids or t_process.status == "COMPLETED"

    _wait_until_done(t_thread)
    _wait_until_done(t_process)

    running_after = dashboard_view.list_running_tasks()
    running_after_ids = {t.task_id for t in running_after}
    assert t_thread.task_id not in running_after_ids
    assert t_process.task_id not in running_after_ids


def test_dashboard_view_does_not_start_or_control_execution():
    import ast

    tree = ast.parse((PROTOTYPE_DIR / "rtb_dashboard_view.py").read_text(encoding="utf-8"))
    called_names = {
        node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    assert "start" not in called_names
    assert "refresh" not in called_names
    assert "retry" not in called_names


# --- Boundary: Task는 Executor를 직접 참조하지 않는다 --------------------------

def test_task_module_does_not_reference_executor_classes_directly():
    import ast

    tree = ast.parse((PROTOTYPE_DIR / "rtb_task.py").read_text(encoding="utf-8"))
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attrs = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "ThreadPoolExecutor" not in names
    assert "ProcessPoolExecutor" not in names
    assert "submit" not in attrs  # Task는 executor.submit()을 직접 호출하지 않는다


# --- Boundary: hqs/*, core/를 직접 import하지 않는다 ---------------------------

def test_no_direct_hq_or_kernel_import():
    import ast

    for filename in ("rtb_runtime.py", "rtb_task.py", "rtb_dashboard_view.py"):
        tree = ast.parse((PROTOTYPE_DIR / filename).read_text(encoding="utf-8"))
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module.split(".")[0])
        assert "hqs" not in modules, filename
        assert "core" not in modules, filename
        assert "mvp" not in modules, filename

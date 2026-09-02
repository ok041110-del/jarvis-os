"""In-process Async Command Prototype — Functional/Boundary Validation.

`hqs/development/mvp/tests/test_mvp_0001.py`(실측 ~69초)는 자동 테스트
전체에서 단 한 번만 시작한다 — RUNNING 상태와 Investment HQ(빠름)와의
독립적 동시 실행을 같은 테스트에서 함께 확인해 실행 횟수를 최소화한다
(작업 지시 §21이 요구하는 최소 검증을 벗어나지 않으면서 테스트 스위트
실행 시간을 보호하기 위함). in-process 실행은 subprocess와 달리 강제
종료(`terminate()`)가 없으므로, 시작된 Dev HQ 작업은 프로세스 종료 시
Executor가 자연히 완료를 기다린다 — 이는 그 자체로 실제 Evidence다
(operation.py 참조).
"""

from __future__ import annotations

import sys
import time
from dataclasses import FrozenInstanceError
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import inproc_case_a as case_a  # noqa: E402
import inproc_case_b as case_b  # noqa: E402
import inproc_dashboard_view as dashboard_view  # noqa: E402
import inproc_operation as operation  # noqa: E402


# --- Q1/§14: 즉시 반환 + RUNNING + 독립적 동시 실행 --------------------------

def test_dev_and_investment_run_concurrently_with_independent_lifecycles():
    dev_task = case_b.start("Development HQ 상태를 보여줘")
    inv_task = case_b.start("Investment HQ 최신 상태를 보여줘")

    assert dev_task.status == "RUNNING"
    assert inv_task.status == "RUNNING"

    deadline = time.monotonic() + 5
    while inv_task.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(inv_task.task_id)

    assert inv_task.status == "COMPLETED"
    assert inv_task.result == (20, 0)

    # investment가 끝난 뒤에도 dev는 계속 RUNNING이어야 한다(69초 작업).
    case_b.refresh(dev_task.task_id)
    assert dev_task.status == "RUNNING", "두 작업이 독립적 lifecycle을 갖지 않으면 investment 완료가 dev에 영향을 준다"


# --- Case A / Case B 전체 lifecycle(Investment HQ, 빠름) --------------------

def test_case_a_full_lifecycle_completes():
    command = case_a.start("Investment HQ 최신 상태를 보여줘")
    assert command.status == "RUNNING"

    deadline = time.monotonic() + 5
    while command.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_a.refresh(command)

    assert command.status == "COMPLETED"
    assert command.passed == 20


def test_case_b_full_lifecycle_completes():
    task = case_b.start("Investment HQ 최신 상태를 보여줘")
    assert task.status == "RUNNING"

    deadline = time.monotonic() + 5
    while task.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(task.task_id)

    assert task.status == "COMPLETED"
    assert task.result == (20, 0)


# --- Failure / Retry ---------------------------------------------------------

def test_failure_is_observable_and_distinguishable_from_result():
    task = case_b.start("Investment HQ 최신 상태를 보여줘", valid_path=False)
    deadline = time.monotonic() + 5
    while task.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(task.task_id)

    assert task.status == "FAILED"
    assert task.error is not None
    assert task.result is None


def test_retry_reuses_command_and_produces_new_task():
    failed = case_b.start("Investment HQ 최신 상태를 보여줘", valid_path=False)
    deadline = time.monotonic() + 5
    while failed.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(failed.task_id)
    assert failed.status == "FAILED"

    retried = case_b.retry(failed.task_id)
    assert retried.task_id != failed.task_id
    assert retried.command == failed.command  # 같은 immutable Command

    deadline = time.monotonic() + 5
    while retried.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(retried.task_id)
    assert retried.status == "COMPLETED"


# --- Command 불변성: Case A vs Case B ----------------------------------------

def test_case_a_command_cannot_stay_frozen():
    """Case A는 실행 상태를 Command 자체에 담아야 하므로 frozen=True로
    선언할 수 없다 — 실제로 status가 외부에서도 자유롭게 mutate된다."""

    command = case_a.start("Investment HQ 최신 상태를 보여줘")
    command.status = "MANUALLY_TAMPERED"
    assert command.status == "MANUALLY_TAMPERED"


def test_case_b_command_stays_frozen():
    task = case_b.start("Investment HQ 최신 상태를 보여줘")
    try:
        task.command.raw_input = "tampered"
        assert False, "Command가 frozen이면 여기 도달하지 않아야 함"
    except FrozenInstanceError:
        pass


# --- Task Registry 조회(객체 참조 없이) --------------------------------------

def test_task_lookup_by_id_without_holding_object_reference():
    task = case_b.start("Investment HQ 최신 상태를 보여줘")
    task_id = task.task_id
    del task

    looked_up = case_b.get_task(task_id)
    assert looked_up.task_id == task_id


def test_case_a_has_no_equivalent_registry():
    assert not hasattr(case_a, "_COMMAND_REGISTRY")


# --- Dashboard Observation ----------------------------------------------------

def test_dashboard_can_observe_running_tasks_via_registry_only():
    task = case_b.start("Investment HQ 최신 상태를 보여줘")
    running = dashboard_view.list_running_tasks()
    assert any(t.task_id == task.task_id for t in running)

    deadline = time.monotonic() + 5
    while task.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(task.task_id)
    running_after = dashboard_view.list_running_tasks()
    assert not any(t.task_id == task.task_id for t in running_after)


def test_dashboard_view_does_not_start_or_control_execution():
    import ast

    tree = ast.parse((PROTOTYPE_DIR / "inproc_dashboard_view.py").read_text(encoding="utf-8"))
    called_names = {
        node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    assert "start" not in called_names
    assert "refresh" not in called_names
    assert "retry" not in called_names


# --- HQ Isolation --------------------------------------------------------------

def test_unknown_hq_fails_without_starting_operation():
    task = case_b.start("Trading HQ 상태를 보여줘")
    assert task.status == "FAILED"
    assert task.error == "unknown_hq"
    assert task.execution_id is None


# --- Boundary: hqs/*, core/를 직접 import하지 않는다 -------------------------

def test_no_direct_hq_or_kernel_import():
    import ast

    for filename in ("inproc_operation.py", "inproc_case_a.py", "inproc_case_b.py", "inproc_dashboard_view.py"):
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

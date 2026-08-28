"""Async/Long-running Command Prototype — Functional/Boundary Validation.

Dev HQ 실행(hqs/development/mvp/tests, 실측 ~70초)은 자동 테스트에서
완료까지 기다리지 않는다 — "즉시 반환 + RUNNING 관찰"만 자동
검증하고, 전체 완료 관찰은 Evidence 문서에 수동 실행 결과로
기록한다(작업 지시 §20이 요구하는 최소 검증을 벗어나지 않으면서
테스트 스위트 실행 시간을 보호하기 위함). Investment HQ 실행
(hqs/investment/tests, 실측 <1초)으로 전체 lifecycle(RUNNING->
COMPLETED, FAILED->retry->COMPLETED)을 빠르게 검증한다.
"""

from __future__ import annotations

import sys
import time
from dataclasses import FrozenInstanceError
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import case_a_command_only as case_a  # noqa: E402
import case_b_command_task as case_b  # noqa: E402
import dashboard_view  # noqa: E402
import operation  # noqa: E402


# --- Q1: Command가 즉시 결과를 반환하지 않는다 -------------------------------

def test_dev_hq_operation_does_not_return_immediately_with_result():
    """실제 Dev HQ 테스트 스위트(~70초)를 시작하고, 즉시 poll하면
    아직 RUNNING이어야 한다 — sleep()이 아니라 실제 Architecture와
    연결된 작업이 비동기로 동작함을 확인한다."""

    command = case_a.start("Development HQ 상태를 보여줘")
    assert command.status == "RUNNING"
    assert command.result is None

    # 즉시 poll — 120개 테스트가 그 사이 전부 끝났을 리 없다.
    case_a.refresh(command)
    assert command.status == "RUNNING", "실제 pytest 실행이 명령 반환 직후 완료된다면 Long-running Case로 부적절"
    operation.terminate(command.execution_id)  # 70초 전체 대기 없이 정리(테스트 목적은 RUNNING 관찰로 충분)


# --- Case A / Case B 전체 lifecycle(Investment HQ, 빠름) --------------------

def test_case_a_full_lifecycle_completes():
    command = case_a.start("Investment HQ 최신 상태를 보여줘")
    assert command.status == "RUNNING"

    deadline = time.monotonic() + 5
    while command.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_a.refresh(command)

    assert command.status == "COMPLETED"
    assert command.result is not None


def test_case_b_full_lifecycle_completes():
    task = case_b.start("Investment HQ 최신 상태를 보여줘")
    assert task.status == "RUNNING"

    deadline = time.monotonic() + 5
    while task.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(task.task_id)

    assert task.status == "COMPLETED"
    assert task.result is not None


# --- Failure / Retry ---------------------------------------------------------

def test_failure_is_observable_and_distinguishable_from_result():
    task = case_b.start("Investment HQ 최신 상태를 보여줘", valid_path=False)
    deadline = time.monotonic() + 5
    while task.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(task.task_id)

    assert task.status == "FAILED"
    assert task.error is not None
    assert task.result is None  # 결과와 실패가 같은 필드에 섞이지 않는다


def test_retry_reuses_command_and_produces_new_task():
    failed = case_b.start("Investment HQ 최신 상태를 보여줘", valid_path=False)
    deadline = time.monotonic() + 5
    while failed.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(failed.task_id)
    assert failed.status == "FAILED"

    retried = case_b.retry(failed.task_id)
    assert retried.task_id != failed.task_id  # 새 Task, 같은 Command
    assert retried.command == failed.command

    deadline = time.monotonic() + 5
    while retried.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(retried.task_id)
    assert retried.status == "COMPLETED"


# --- Command 불변성: Case A vs Case B ----------------------------------------

def test_case_a_command_cannot_stay_frozen():
    """Case A는 Command 자체에 실행 상태를 담아야 하므로 frozen=True로
    선언할 수 없다(command.py의 원래 Command Contract 설계와
    충돌) — 실제로 status 필드가 외부에서도 자유롭게 mutate된다."""

    command = case_a.start("Investment HQ 최신 상태를 보여줘")
    command.status = "MANUALLY_TAMPERED"  # frozen이 아니므로 외부에서도 변경 가능 — 이것이 문제
    assert command.status == "MANUALLY_TAMPERED"
    if command.execution_id:
        operation.terminate(command.execution_id)


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
    del task  # 참조를 버려도 task_id만으로 다시 찾을 수 있어야 한다

    looked_up = case_b.get_task(task_id)
    assert looked_up.task_id == task_id


def test_case_a_has_no_equivalent_registry():
    """Case A에는 AsyncCommand를 위한 Registry가 없다 — Command
    객체 참조를 버리면 그 Command는 더 이상 조회할 수 없다(비교를
    위한 명시적 확인, Case A의 한계를 코드로 증명)."""

    assert not hasattr(case_a, "_COMMAND_REGISTRY")


# --- Dashboard Observation ----------------------------------------------------

def test_dashboard_can_observe_running_tasks_via_registry_only():
    task = case_b.start("Investment HQ 최신 상태를 보여줘")
    running = dashboard_view.list_running_tasks()
    assert any(t.task_id == task.task_id for t in running)

    # 완료까지 대기 후 다시 관찰 — RUNNING 목록에서 빠져야 한다
    deadline = time.monotonic() + 5
    while task.status == "RUNNING" and time.monotonic() < deadline:
        time.sleep(0.05)
        case_b.refresh(task.task_id)
    running_after = dashboard_view.list_running_tasks()
    assert not any(t.task_id == task.task_id for t in running_after)


def test_dashboard_view_does_not_start_or_control_execution():
    import ast

    tree = ast.parse((PROTOTYPE_DIR / "dashboard_view.py").read_text(encoding="utf-8"))
    called_names = {
        node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    assert "start" not in called_names
    assert "refresh" not in called_names
    assert "retry" not in called_names


# --- HQ Isolation --------------------------------------------------------------

def test_hq_isolation_investment_and_development_targets():
    inv_task = case_b.start("Investment HQ 최신 상태를 보여줘")
    dev_task = case_b.start("Development HQ 상태를 보여줘")

    assert inv_task.command.target_hq == "investment"
    assert dev_task.command.target_hq == "development"
    assert inv_task.task_id != dev_task.task_id


def test_unknown_hq_fails_without_starting_operation():
    task = case_b.start("Trading HQ 상태를 보여줘")
    assert task.status == "FAILED"
    assert task.error == "unknown_hq"
    assert task.execution_id is None


# --- Boundary: hqs/*, core/를 직접 import하지 않는다 -------------------------

def test_no_direct_hq_or_kernel_import():
    import ast

    for filename in ("operation.py", "case_a_command_only.py", "case_b_command_task.py", "dashboard_view.py"):
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

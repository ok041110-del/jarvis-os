"""Dev HQ Vertical Slice — E2E Validation.

Command → Task → Runtime(Process) → Dev HQ(실제 Validation) → Result
저장 → Dashboard 관찰 전체 경로를 실제로 검증한다.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import vs_dashboard_view as dashboard  # noqa: E402
import vs_pipeline as pipeline  # noqa: E402
import vs_result_store as result_store  # noqa: E402


def setup_module(module):
    if result_store.RESULTS_DIR.exists():
        for path in result_store.RESULTS_DIR.glob("*.json"):
            path.unlink()


def _wait(t, timeout=90.0):
    deadline = time.monotonic() + timeout
    while t.status in ("PENDING", "RUNNING") and time.monotonic() < deadline:
        time.sleep(0.02)
        t = pipeline.refresh(t.task_id)
    return t


# --- 전체 E2E: Command -> Task -> Runtime -> Dev HQ -> Result -> Dashboard ---

def test_e2e_valid_command_reaches_dashboard_via_result_file():
    t = pipeline.submit("Development HQ ast_context 검증 실행")
    assert t.status in ("PENDING", "RUNNING")  # 즉시 반환(비동기)

    running = dashboard.list_running()
    assert any(r.task_id == t.task_id for r in running)

    t = _wait(t)
    assert t.status == "COMPLETED"
    assert t.result == (8, 0)

    # Registry가 아니라 파일(Result Store)만으로 Dashboard가 관찰 가능한지 확인
    stored = result_store.load_result(t.task_id)
    assert stored is not None
    assert stored["status"] == "COMPLETED"
    assert stored["result"] == [8, 0]

    completed = dashboard.list_completed_results()
    assert any(r["task_id"] == t.task_id for r in completed)


def test_e2e_covers_all_three_dev_hq_actions():
    for action_input, expected in (
        ("Development HQ stage_01 검증 실행", (5, 0)),
        ("Development HQ mvp_0001 검증 실행", (3, 0)),
    ):
        t = pipeline.submit(action_input)
        t = _wait(t)
        assert t.status == "COMPLETED", f"{action_input}: {t.error}"
        assert t.result == expected


# --- 알 수 없는 Command ------------------------------------------------------

def test_unknown_command_fails_without_starting_runtime():
    t = pipeline.submit("Trading HQ 실행해줘")
    assert t.status == "FAILED"
    assert t.error == "unknown_action"

    stored = result_store.load_result(t.task_id)
    assert stored is not None
    assert stored["status"] == "FAILED"


# --- Command 불변성(재확인 — command-contract/runtime-boundary와 동일 원칙) ---

def test_command_is_immutable():
    import vs_command as command
    from dataclasses import FrozenInstanceError

    cmd = command.parse_command("Development HQ ast_context 검증 실행")
    assert cmd.action == "ast_context"
    try:
        cmd.action = "tampered"
        assert False, "Command가 frozen이면 여기 도달하지 않아야 함"
    except FrozenInstanceError:
        pass


# --- 서로 다른 두 Action 동시 실행(Process, 독립적 lifecycle) ----------------

def test_concurrent_different_actions_are_independent():
    t1 = pipeline.submit("Development HQ ast_context 검증 실행")
    t2 = pipeline.submit("Development HQ stage_01 검증 실행")

    assert t1.task_id != t2.task_id
    t1 = _wait(t1)
    t2 = _wait(t2)
    assert t1.result == (8, 0)
    assert t2.result == (5, 0)


# --- Dashboard는 Observe-only -------------------------------------------------

def test_dashboard_module_does_not_import_pipeline():
    import ast

    tree = ast.parse((PROTOTYPE_DIR / "vs_dashboard_view.py").read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    assert "vs_pipeline" not in modules


# --- Boundary: hqs/*, core/를 직접 import하지 않는다 --------------------------

def test_no_direct_hq_or_kernel_import():
    import ast

    for filename in (
        "vs_command.py", "vs_dev_hq_adapter.py", "vs_result_store.py",
        "vs_pipeline.py", "vs_dashboard_view.py",
    ):
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

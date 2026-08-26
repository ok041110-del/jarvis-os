"""Command Contract Prototype — Functional/Boundary Validation."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

from command import Command  # noqa: E402
from resolver import parse_command, resolve, run_command  # noqa: E402
from task_case import run_via_task  # noqa: E402


def _imported_top_level_modules(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


# --- 1. Development Command -> Development HQ -----------------------------

def test_development_command_targets_development_hq():
    result = run_command("Development HQ 상태를 보여줘")
    assert result.status == "ok"
    assert result.hq_identity == "Development HQ"
    assert result.detail


# --- 2. Investment Command -> Investment HQ --------------------------------

def test_investment_command_targets_investment_hq():
    result = run_command("Investment HQ 최신 상태를 보여줘")
    assert result.status == "ok"
    assert result.hq_identity == "Investment HQ"
    assert result.detail


# --- 3. Unknown HQ ----------------------------------------------------------

def test_unknown_hq_returns_invalid():
    result = run_command("Trading HQ 상태를 보여줘")
    assert result.status == "invalid"
    assert result.reason == "unknown_hq"


# --- 4. Unknown command ------------------------------------------------------

def test_unknown_command_returns_invalid():
    result = run_command("Development HQ에서 주문을 실행해줘")
    assert result.status == "invalid"
    assert result.reason == "unsupported_intent"

    result_empty = run_command("ㅁㄴㅇㄹ")
    assert result_empty.status == "invalid"
    assert result_empty.reason == "unknown_command"


# --- 5. Command -> Snapshot 연결 --------------------------------------------

def test_command_result_matches_dashboard_snapshot_content():
    """Command 결과(detail)가 Dashboard Prototype의 Snapshot과
    동일한 원본 데이터를 반환하는지 확인 — Command Layer가 자체
    데이터를 만들지 않고 기존 Snapshot Builder를 그대로 재사용함을
    검증한다."""

    sys.path.insert(0, str(PROTOTYPE_DIR.parent / "unified-dashboard"))
    from snapshot import build_dev_hq_snapshot  # noqa: E402

    result = run_command("Development HQ 상태를 보여줘")
    expected = build_dev_hq_snapshot()
    assert result.detail == expected.detail


# --- 6. Command -> Task 필요성 검증 ------------------------------------------

def test_task_wrapping_adds_no_observable_value_for_single_readonly_command():
    """Case A(Command->HQ)와 Case B(Command->Task->HQ)를 같은 입력으로
    비교한다. Task가 추가하는 것은 task_id(사용되지 않음)와 status
    (항상 completed, 재조회되지 않음)뿐임을 확인한다 — 이는 이번
    Prototype 범위(단발 동기 read-only 명령)에서 Task가 실질적
    이점(재실행/진행상태 추적/결과 연결)을 제공하지 않는다는 Evidence다."""

    raw_input = "Investment HQ 최신 상태를 보여줘"
    command = parse_command(raw_input)

    case_a_result = resolve(command)
    task = run_via_task(raw_input, command)

    assert task.result == case_a_result
    assert task.status == "completed"
    # Task가 끝난 뒤 task_id/status를 다시 조회하는 코드가 이 Prototype
    # 어디에도 없다 — 즉 두 필드가 생성되지만 소비되지 않는다.


# --- 7. HQ Isolation ---------------------------------------------------------

def test_hq_isolation_dev_and_investment_do_not_cross_reference():
    dev_result = run_command("Development HQ 상태를 보여줘")
    inv_result = run_command("Investment HQ 최신 상태를 보여줘")

    dev_text = " ".join(dev_result.detail)
    inv_text = " ".join(inv_result.detail)

    assert "Investment" not in dev_text
    assert "Trader" not in dev_text
    assert "Stage" not in inv_text
    assert "Agent Roles" not in inv_text


def test_multi_hq_sequential_commands_do_not_require_shared_state():
    """같은 세션에서 두 HQ Command를 순차 실행해도 이전 Command의
    상태가 다음 Command에 영향을 주지 않는지 확인(Context 필요성
    검증, Q4)."""

    first = run_command("Development HQ 상태를 보여줘")
    second = run_command("Investment HQ 최신 상태를 보여줘")
    first_again = run_command("Development HQ 상태를 보여줘")

    assert first.detail == first_again.detail
    assert first.hq_identity != second.hq_identity


# --- 8. Command ID 필요성 검증 ------------------------------------------------

def test_command_has_no_id_field_and_resolution_still_works():
    """Command에 command_id가 없어도(§5, Evidence 없이 필드 추가
    금지) 단일 동기 요청-응답 흐름이 성립하는지 확인."""

    assert not hasattr(Command(raw_input="x"), "command_id")
    result = run_command("Development HQ 상태를 보여줘")
    assert result.status == "ok"


# --- Boundary: Resolver가 hqs/*·core/를 직접 import하지 않는가 --------------

def test_resolver_does_not_import_hq_or_kernel_code_directly():
    modules = _imported_top_level_modules(PROTOTYPE_DIR / "resolver.py")
    assert "hqs" not in modules
    assert "core" not in modules
    assert "mvp" not in modules


def test_resolver_never_calls_engine():
    resolver_src = (PROTOTYPE_DIR / "resolver.py").read_text(encoding="utf-8")
    assert "call_engine" not in resolver_src

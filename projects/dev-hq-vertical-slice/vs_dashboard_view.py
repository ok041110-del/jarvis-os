"""Dashboard — Observe-only. `vs_pipeline`을 import하지 않는다(실행을
시작/재시도할 수단 자체가 이 모듈에 없다).

RUNNING 상태는 Task Registry(`rtb_task`, `runtime-boundary` Prototype
재사용)에서, 완료된 결과는 Result Store(파일)에서 읽는다 — 두 경로
모두 순수 조회다.
"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_RUNTIME_BOUNDARY_DIR = _THIS_DIR.parents[0] / "runtime-boundary"
sys.path.insert(0, str(_THIS_DIR))
sys.path.insert(0, str(_RUNTIME_BOUNDARY_DIR))

import rtb_dashboard_view as running_view  # noqa: E402

import vs_result_store as result_store  # noqa: E402


def list_running() -> list:
    return running_view.list_running_tasks()


def list_completed_results() -> list[dict]:
    return result_store.load_all_results()

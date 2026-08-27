"""Runtime Boundary Prototype — 수동 실행 데모(Evidence 문서용).

동일한 실제 대상(hqs/investment/tests/test_stock_team_integration.py,
2 tests)을 Sequential / Thread / Process 세 전략으로 두 번씩 동시
실행해 실제 격리 차이를 관찰한다.

실행: python3 projects/runtime-boundary/demo.py
"""

from __future__ import annotations

import time

import rtb_dashboard_view as dashboard_view
import rtb_task as task

TARGET = "hqs/investment/tests/test_stock_team_integration.py"


def _wait(t, timeout=10.0):
    deadline = time.monotonic() + timeout
    while t.status in ("PENDING", "RUNNING") and time.monotonic() < deadline:
        time.sleep(0.02)
        task.refresh(t.task_id)
    return t


def compare_strategies() -> None:
    print("=== 동일 대상 2회 동시 실행 — Sequential vs Thread vs Process ===")
    print(f"target={TARGET} (baseline 2 passed)\n")

    print("[Sequential] (실제로는 순차 — 블로킹, 동시성 없음)")
    t0 = time.monotonic()
    s1 = task.start(TARGET, "sequential")
    s2 = task.start(TARGET, "sequential")
    print(f"  s1.status(호출 즉시)={s1.status} s2.status(호출 즉시)={s2.status}  <- 블로킹이라 시작 즉시 이미 COMPLETED")
    print(f"  result: s1={s1.result} s2={s2.result}  elapsed={time.monotonic()-t0:.2f}s\n")

    for strategy in ("thread", "process"):
        print(f"[{strategy}]")
        t0 = time.monotonic()
        r1 = task.start(TARGET, strategy)
        r2 = task.start(TARGET, strategy)
        print(f"  r1.status(호출 직후)={r1.status} r2.status(호출 직후)={r2.status}  <- 즉시 반환(비동기)")
        _wait(r1)
        _wait(r2)
        combined = (r1.result[0] if r1.result else 0) + (r2.result[0] if r2.result else 0)
        print(f"  result: r1={r1.result} r2={r2.result}  combined_passed={combined} (기대값 4)")
        print(f"  elapsed={time.monotonic()-t0:.2f}s\n")


def dashboard_observation_demo() -> None:
    print("=== Dashboard Observation(Process 전략) ===")
    t1 = task.start(TARGET, "process")
    t2 = task.start("hqs/investment/tests", "process")
    running = dashboard_view.list_running_tasks()
    print(f"RUNNING tasks observed: {len(running)} (ids: {[r.task_id[:8] for r in running]})")
    _wait(t1)
    _wait(t2)
    running_after = dashboard_view.list_running_tasks()
    print(f"완료 후 RUNNING tasks observed: {len(running_after)}")


if __name__ == "__main__":
    compare_strategies()
    dashboard_observation_demo()

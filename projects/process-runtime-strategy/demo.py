"""Process Runtime Strategy — 수동 실행 데모(Evidence 문서용).

1) 서로 다른 실제 Dev HQ Validation 3종(ast_context/stage_01/
   mvp_0001)에 Process 전략을 적용해 정확성·실행시간을 baseline과
   비교한다.
2) 동일 Target 동시 실행(Thread 불안정 vs Process 안정) 대 서로
   다른 Target 동시 실행(Dev HQ 내부, Thread도 안전)을 나란히
   비교한다.

실행: python3 projects/process-runtime-strategy/demo.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parent
RUNTIME_BOUNDARY_DIR = PROTOTYPE_DIR.parents[0] / "runtime-boundary"
sys.path.insert(0, str(PROTOTYPE_DIR))
sys.path.insert(0, str(RUNTIME_BOUNDARY_DIR))

import rtb_task as task  # noqa: E402
from prs_dev_validation import DEV_HQ_TARGETS, EXPECTED_PASSED  # noqa: E402

CONTAMINATION_TARGET = "hqs/investment/tests/test_stock_team_integration.py"


def _wait(t, timeout=90.0):
    deadline = time.monotonic() + timeout
    while t.status in ("PENDING", "RUNNING") and time.monotonic() < deadline:
        time.sleep(0.02)
        task.refresh(t.task_id)
    return t


def part1_dev_hq_variety() -> None:
    print("=== Part 1: 서로 다른 실제 Dev HQ Validation 3종 — Process 전략 ===")
    for name, target in DEV_HQ_TARGETS.items():
        t0 = time.monotonic()
        t = task.start(target, "process")
        _wait(t)
        elapsed = time.monotonic() - t0
        expected = (EXPECTED_PASSED[name], 0)
        ok = "OK" if t.result == expected else "MISMATCH"
        print(f"  {name:12s} status={t.status:10s} result={t.result} expected={expected} elapsed={elapsed:6.2f}s [{ok}]")


def part2_same_vs_different_target() -> None:
    print("\n=== Part 2: 동일 Target vs 다른 Target 동시 실행 ===")

    print("[동일 Target, Thread] (Investment, monkeypatch 있음)")
    t1 = task.start(CONTAMINATION_TARGET, "thread")
    t2 = task.start(CONTAMINATION_TARGET, "thread")
    _wait(t1); _wait(t2)
    combined = (t1.result[0] if t1.result else 0) + (t2.result[0] if t2.result else 0)
    print(f"  combined_passed={combined} (기대값 4) {'<- 오염' if combined != 4 else ''}")

    print("[동일 Target, Process]")
    t1 = task.start(CONTAMINATION_TARGET, "process")
    t2 = task.start(CONTAMINATION_TARGET, "process")
    _wait(t1); _wait(t2)
    combined = (t1.result[0] if t1.result else 0) + (t2.result[0] if t2.result else 0)
    print(f"  combined_passed={combined} (기대값 4)")

    print("[다른 Target(Dev HQ 내부), Thread]")
    a = task.start(DEV_HQ_TARGETS["ast_context"], "thread")
    b = task.start(DEV_HQ_TARGETS["stage_01"], "thread")
    _wait(a); _wait(b)
    print(f"  ast_context={a.result} (기대 8) stage_01={b.result} (기대 5)")

    print("[다른 Target(Dev HQ 내부), Process]")
    a = task.start(DEV_HQ_TARGETS["ast_context"], "process")
    b = task.start(DEV_HQ_TARGETS["stage_01"], "process")
    _wait(a); _wait(b)
    print(f"  ast_context={a.result} (기대 8) stage_01={b.result} (기대 5)")


if __name__ == "__main__":
    part1_dev_hq_variety()
    part2_same_vs_different_target()

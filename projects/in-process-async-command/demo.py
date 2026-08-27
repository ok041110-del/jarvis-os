"""In-process Async Command Prototype — 수동 실행 데모(Evidence 문서용).

1) Case B: Dev HQ(실제 ~69초, in-process)와 Investment HQ(빠름)를 동시에
   시작하고 완료까지 관찰한다. Dev HQ 완료까지 기다린다 — 자동 테스트
   스위트에는 포함하지 않는다.
2) 동일 대상(Investment HQ tests)을 두 Thread에서 동시에 실행했을 때
   실제로 어떤 일이 일어나는지 관찰한다(§9 Runtime 평가를 위한 추가
   탐색 — Task/Command 설계와 무관하게 in-process 실행 자체의 한계를
   확인하기 위함).

실행: python3 projects/in-process-async-command/demo.py
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

import inproc_case_b as case_b
import inproc_dashboard_view as dashboard_view
import inproc_operation as operation


def part1_concurrent_dev_and_investment() -> None:
    print("=== Part 1: Case B — Dev HQ(~69초) + Investment HQ 동시 실행 ===")
    dev_task = case_b.start("Development HQ 상태를 보여줘")
    inv_task = case_b.start("Investment HQ 최신 상태를 보여줘")
    print(f"started dev={dev_task.task_id[:8]} investment={inv_task.task_id[:8]}")

    print("\n=== Dashboard Observation(Registry만 읽음) ===")
    running = dashboard_view.list_running_tasks()
    print(f"RUNNING tasks observed by Dashboard: {len(running)}")

    print("\n=== Polling until both complete ===")
    start = time.monotonic()
    while True:
        case_b.refresh(dev_task.task_id)
        case_b.refresh(inv_task.task_id)
        elapsed = time.monotonic() - start
        print(f"+{elapsed:5.1f}s  development={dev_task.status:10s}  investment={inv_task.status}")
        if dev_task.status != "RUNNING" and inv_task.status != "RUNNING":
            break
        time.sleep(2)

    print("\n=== Final ===")
    print(f"Development: status={dev_task.status} result={dev_task.result} error={dev_task.error}")
    print(f"Investment:  status={inv_task.status} result={inv_task.result} error={inv_task.error}")


def part2_identical_target_concurrency_probe() -> None:
    """동일 대상(hqs/investment/tests)을 두 Thread에서 동시에 실행하면
    결과 집계가 정확한지 확인한다 — Task/Command 설계 질문과는 별개로,
    in-process 실행 자체의 안전성에 대한 탐색적 확인이다."""

    print("\n\n=== Part 2: 동일 대상 동시 실행 — 결과 집계 정확성 확인 ===")
    print("baseline(순차, 1회): ", end="")
    baseline_id = operation.start_operation("investment")
    baseline = operation.poll(baseline_id)
    while baseline.status == "RUNNING":
        time.sleep(0.02)
        baseline = operation.poll(baseline_id)
    print(f"status={baseline.status} passed={baseline.passed} failed={baseline.failed}")

    for trial in range(1, 4):
        with ThreadPoolExecutor(max_workers=2) as pool:
            f1 = pool.submit(operation._run_pytest_inprocess, "hqs/investment/tests")
            f2 = pool.submit(operation._run_pytest_inprocess, "hqs/investment/tests")
            rc1, p1, fail1 = f1.result()
            rc2, p2, fail2 = f2.result()
        print(
            f"trial {trial}: run1(rc={rc1}, passed={p1}, failed={fail1}) "
            f"run2(rc={rc2}, passed={p2}, failed={fail2}) "
            f"combined_passed={p1 + p2} (baseline 2x16=32이어야 함)"
        )


if __name__ == "__main__":
    part1_concurrent_dev_and_investment()
    part2_identical_target_concurrency_probe()

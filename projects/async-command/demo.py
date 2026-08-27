"""Async Command Prototype — 수동 실행 데모(Evidence 문서용).

Dev HQ 전체 테스트 스위트(실측 ~70초)의 완료까지 관찰한다. 자동
테스트 스위트에는 포함하지 않는다(시간이 오래 걸림) — Evidence
문서가 이 스크립트의 실행 결과를 인용한다.

실행: python3 projects/async-command/demo.py
"""

from __future__ import annotations

import time

import case_b_command_task as case_b
import dashboard_view


def main() -> None:
    print("=== Case B: Investment HQ (빠른 lifecycle) ===")
    inv_task = case_b.start("Investment HQ 최신 상태를 보여줘")
    print(f"started task_id={inv_task.task_id} status={inv_task.status}")

    print("\n=== Case B: Development HQ (실제 ~70초 장시간 작업) ===")
    dev_task = case_b.start("Development HQ 상태를 보여줘")
    print(f"started task_id={dev_task.task_id} status={dev_task.status}")

    print("\n=== Dashboard Observation(Registry만 읽음) ===")
    running = dashboard_view.list_running_tasks()
    print(f"RUNNING tasks observed by Dashboard: {len(running)}")
    for t in running:
        print(f"  - {t.task_id[:8]} target_hq={t.command.target_hq}")

    print("\n=== Polling until both complete ===")
    start = time.monotonic()
    while True:
        case_b.refresh(inv_task.task_id)
        case_b.refresh(dev_task.task_id)
        elapsed = time.monotonic() - start
        print(f"+{elapsed:5.1f}s  investment={inv_task.status:10s}  development={dev_task.status}")
        if inv_task.status != "RUNNING" and dev_task.status != "RUNNING":
            break
        time.sleep(2)

    print("\n=== Final ===")
    print(f"Investment: status={inv_task.status} result_tail={inv_task.result!r}")
    print(f"Development: status={dev_task.status} result_tail={dev_task.result!r}")

    print("\n=== Dashboard Observation after completion ===")
    running_after = dashboard_view.list_running_tasks()
    print(f"RUNNING tasks observed by Dashboard: {len(running_after)}")


if __name__ == "__main__":
    main()

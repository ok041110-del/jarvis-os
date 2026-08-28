"""Dev HQ Vertical Slice — 수동 실행 데모(Evidence 문서용).

Command → Task → Runtime(Process) → Dev HQ(실제 Validation) → Result
저장 → Dashboard 관찰까지 전체 경로를 한 번에 보여준다.

실행: python3 projects/dev-hq-vertical-slice/demo.py
"""

from __future__ import annotations

import time

import vs_dashboard_view as dashboard
import vs_pipeline as pipeline


def _wait(t, timeout=90.0):
    deadline = time.monotonic() + timeout
    while t.status in ("PENDING", "RUNNING") and time.monotonic() < deadline:
        time.sleep(0.02)
        t = pipeline.refresh(t.task_id)
    return t


def main() -> None:
    print("=== Command 제출 ===")
    t1 = pipeline.submit("Development HQ ast_context 검증 실행")
    print(f"  task_id={t1.task_id[:8]} status={t1.status}")

    print("\n=== Dashboard 관찰(완료 전) ===")
    print(f"  RUNNING: {[t.task_id[:8] for t in dashboard.list_running()]}")

    t1 = _wait(t1)
    print(f"\n완료: status={t1.status} result={t1.result}")

    print("\n=== Dashboard 관찰(Result Store, 파일만으로) ===")
    for r in dashboard.list_completed_results():
        print(f"  {r['task_id'][:8]} target={r['target']} status={r['status']} result={r['result']}")

    print("\n=== 알 수 없는 Command ===")
    t2 = pipeline.submit("Trading HQ 실행해줘")
    print(f"  status={t2.status} error={t2.error}")


if __name__ == "__main__":
    main()

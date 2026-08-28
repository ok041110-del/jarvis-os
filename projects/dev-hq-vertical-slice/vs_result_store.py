"""Result Store — Task 완료 결과를 파일로 영속화한다.

`Task.result`는 프로세스 메모리에만 존재한다 — Registry를 가진
프로세스가 사라지면 함께 사라진다. 이 Prototype은 "Result 저장이
실제로 필요한가"를 검증하는 지점이다: Dashboard가 Task Registry
객체 참조 없이, **파일만으로** 완료된 실행 결과를 관찰할 수 있는지
실제로 확인한다(작업 지시 §6 E2E).
"""

from __future__ import annotations

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def save_result(task) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"{task.task_id}.json"
    payload = {
        "task_id": task.task_id,
        "target": task.target,
        "strategy": task.strategy,
        "status": task.status,
        "result": list(task.result) if task.result else None,
        "error": task.error,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_all_results() -> list[dict]:
    if not RESULTS_DIR.exists():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(RESULTS_DIR.glob("*.json"))]


def load_result(task_id: str) -> dict | None:
    path = RESULTS_DIR / f"{task_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

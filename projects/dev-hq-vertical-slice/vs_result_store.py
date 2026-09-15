"""Result Store — Task 완료 결과를 파일로 영속화한다.

Task.result는 프로세스 메모리에만 존재해 Registry 프로세스가 사라지면 함께 사라진다 — Dashboard가 파일만으로도 결과를 관찰 가능한지 확인하는 지점.
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

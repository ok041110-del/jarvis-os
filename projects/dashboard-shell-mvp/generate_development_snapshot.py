"""Dashboard Shell MVP — Development HQ Snapshot Generator.

Boundary: `hqs/development`의 Python 코드를 import하지 않는다(재사용하는 `build_dev_hq_snapshot()` 자체가 이미 이 Boundary를 지킨다 — AST 검증은 `tests/test_generate_development_snapshot.py` 참조). Engine/Agent를 호출하지 않는다.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIFIED_DASHBOARD_DIR = REPO_ROOT / "projects" / "unified-dashboard"
sys.path.insert(0, str(UNIFIED_DASHBOARD_DIR))

from snapshot import build_dev_hq_snapshot  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "development-snapshot.json"

_STAGE_RE = re.compile(r"^Phase:\s*(.+)$")
_TASK_RE = re.compile(r"^Current Task:\s*(.+)$")
_AGENTS_RE = re.compile(r"^Agent Roles:\s*(.+)$")


def _extract(detail: list[str], pattern: re.Pattern) -> str | None:
    for line in detail:
        match = pattern.match(line)
        if match:
            return match.group(1)
    return None


def build_document() -> dict:
    snap = build_dev_hq_snapshot()

    stage = _extract(snap.detail, _STAGE_RE)
    current_task = _extract(snap.detail, _TASK_RE)
    agents_raw = _extract(snap.detail, _AGENTS_RE)
    agents = (
        [a.strip() for a in agents_raw.split(",")]
        if agents_raw and agents_raw != "UNKNOWN"
        else []
    )

    return {
        "connection": "EVIDENCE",
        "status": snap.status,
        "stage": stage or "UNKNOWN(Evidence에서 추출 실패)",
        "progressPercent": None,
        "currentTask": current_task or "UNKNOWN(Evidence에서 추출 실패)",
        "agents": agents,
        "recentEvents": list(snap.detail),
        "sourceFiles": snap.source_files,
    }


def main() -> None:
    document = build_document()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"development-snapshot.json written to {OUTPUT_PATH}")
    print(f"- status: {document['status']}")
    print(f"- source_files: {document['sourceFiles']}")


if __name__ == "__main__":
    main()

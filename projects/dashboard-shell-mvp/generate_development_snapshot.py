"""Dashboard Shell MVP — Development HQ Snapshot Generator.

`projects/unified-dashboard/snapshot.py`의 `build_dev_hq_snapshot()`을
그대로 재사용해 Development HQ Evidence를 읽는다 — 새 Evidence 수집
로직을 만들지 않는다. 이 스크립트는 그 결과를 `js/data.js`의
`getHQSnapshot('development')`가 기대하는 최소 shape(JSON)으로만
옮겨 적는다.

Boundary: `hqs/development`의 Python 코드를 import하지 않는다(재사용하는
`build_dev_hq_snapshot()` 자체가 이미 이 Boundary를 지킨다 — AST 검증은
`tests/test_generate_development_snapshot.py` 참조). Engine/Agent를
호출하지 않는다.

`progressPercent`는 의도적으로 항상 `null`이다 — Development HQ에는
진행률(%) 같은 실제 Evidence가 없다(상시 Runtime 없음, ADC-02 Open).
Mock이 쓰던 58%~ 같은 숫자를 지어내는 대신, 없다는 사실 자체를
그대로 노출한다(js/render.js가 null을 "Evidence 없음"으로 표시).
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

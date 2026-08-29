"""Unified Dashboard Prototype — snapshot.py 데이터를 frontend가 읽을
JSON으로 내보낸다.

기존 `generate_dashboard.py`(HTML 경로)를 대체하지 않는다 — 이 파일은
같은 `snapshot.py`를 재사용해 두 번째 출력 형식(JSON)만 추가한다.
`snapshot.py`와 동일한 Boundary를 유지한다: `hqs/*` Python 모듈을
import하지 않고, Engine/Agent를 호출하지 않는다(`snapshot.py`가 이미
검증된 방식으로 읽은 값을 그대로 직렬화할 뿐이다).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from snapshot import build_global_snapshot

OUTPUT_PATH = (
    Path(__file__).resolve().parent / "frontend" / "public" / "data" / "snapshot.json"
)


def build_snapshot_document() -> dict:
    snapshots = build_global_snapshot()
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "snapshots": [asdict(s) for s in snapshots],
    }


def main() -> None:
    document = build_snapshot_document()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"snapshot.json written to {OUTPUT_PATH}")
    for snap in document["snapshots"]:
        print(f"- {snap['identity']}: {snap['status']}")


if __name__ == "__main__":
    main()

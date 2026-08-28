"""Unified Dashboard Prototype — CLI 진입점.

실행: python projects/unified-dashboard/generate_dashboard.py
출력: projects/unified-dashboard/output/dashboard.html

Dashboard = Observe 원칙 검증용 Experimental Implementation.
Agent/Engine을 호출하지 않는다 — 기존 Evidence 파일만 읽는다.
"""

from __future__ import annotations

from pathlib import Path

from render import render_dashboard
from snapshot import build_global_snapshot

OUTPUT_PATH = Path(__file__).resolve().parent / "output" / "dashboard.html"


def main() -> None:
    snapshots = build_global_snapshot()
    html = render_dashboard(snapshots)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {OUTPUT_PATH}")
    for snap in snapshots:
        print(f"- {snap.identity}: {snap.status}")


if __name__ == "__main__":
    main()

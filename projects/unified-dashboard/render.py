"""Unified Dashboard Prototype — Global/HQ 렌더링.

Global Dashboard 책임(Navigation/HQ Status/Overview 조합)과 HQ View
책임(해당 HQ의 상세 정보 표시)을 분리한다. Global Shell은 어떤
HQ-specific 내용도 알지 못한다 — snapshot.detail을 그대로 나열할 뿐
해석하지 않는다.
"""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape

from snapshot import HQSnapshot

_STATE_COLOR = {
    "NORMAL": "#2e7d32",
    "WORKING": "#f9a825",
    "BLOCKED": "#c62828",
    "DEFERRED": "#616161",
    "UNKNOWN": "#9e9e9e",
}


def _status_badge(state: str) -> str:
    color = _STATE_COLOR.get(state, "#9e9e9e")
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;">{escape(state)}</span>'


def _render_hq_card(snap: HQSnapshot) -> str:
    detail_items = "".join(f"<li>{escape(line)}</li>" for line in snap.detail)
    deferred_items = "".join(f"<li>{escape(item)} — <em>DEFERRED (미구현, 표시하지 않음)</em></li>" for item in snap.deferred)
    sources = ", ".join(escape(s) for s in snap.source_files) or "N/A"
    return f"""
    <section style="border:1px solid #ddd;border-radius:8px;padding:16px;margin-bottom:16px;">
      <h2 style="margin:0 0 8px 0;">{escape(snap.identity)} {_status_badge(snap.status)}</h2>
      <ul>{detail_items}</ul>
      {f'<h3 style="font-size:14px;color:#616161;">Deferred (의도적 미구현)</h3><ul>{deferred_items}</ul>' if snap.deferred else ''}
      <p style="font-size:11px;color:#999;">Source: {sources}</p>
    </section>
    """


def render_dashboard(snapshots: list[HQSnapshot]) -> str:
    """Global Shell — Navigation/HQ Status Overview만 조합한다.
    HQ 내부 의미(Portfolio/Trader 등)를 Global Shell이 해석하지
    않는다 — 각 HQ Card의 detail 문자열을 그대로 표시할 뿐이다."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    nav_items = "".join(f'<li>{escape(s.identity)} {_status_badge(s.status)}</li>' for s in snapshots)
    cards = "".join(_render_hq_card(s) for s in snapshots)

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>Jarvis OS — Unified Dashboard (Experimental Prototype)</title>
<style>
  body {{ font-family: -apple-system, sans-serif; margin: 0; background: #fafafa; color: #222; }}
  header {{ background: #1a1a1a; color: #fff; padding: 16px 24px; }}
  header h1 {{ margin: 0; font-size: 20px; }}
  header p {{ margin: 4px 0 0 0; font-size: 12px; color: #bbb; }}
  main {{ display: grid; grid-template-columns: 220px 1fr; gap: 24px; padding: 24px; }}
  nav ul {{ list-style: none; padding: 0; }}
  nav li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
  ul {{ padding-left: 20px; }}
</style>
</head>
<body>
<header>
  <h1>Jarvis OS — Unified Status</h1>
  <p>Experimental Prototype — Production Dashboard 아님 (projects/unified-dashboard). Updated: {now}</p>
</header>
<main>
  <nav><h3>HQ Navigation</h3><ul>{nav_items}</ul></nav>
  <div>{cards}</div>
</main>
</body>
</html>
"""

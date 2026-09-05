"""Dashboard Shell MVP — Investment HQ Snapshot Generator.

`generate_development_snapshot.py`와 같은 방식이다:
`projects/unified-dashboard/snapshot.py`의 `build_investment_hq_snapshot()`
을 그대로 재사용해 Investment HQ Evidence를 읽는다 — 새 Evidence 수집
로직을 만들지 않는다. 이 스크립트는 그 결과를 `js/data.js`의
`getHQSnapshot('investment')`가 기대하는 최소 shape(JSON)으로만
옮겨 적는다.

Boundary: `hqs/investment`의 Python 코드를 import하지 않는다(재사용하는
`build_investment_hq_snapshot()` 자체가 이미 이 Boundary를 지킨다 —
AST 검증은 `tests/test_generate_investment_snapshot.py` 참조). trader.py
등 Engine/Agent를 호출하지 않는다.

팀별 status/lastDecision은 `build_investment_hq_snapshot()`이 이미
만들어 둔 `detail` 문자열(대표 run 1개, `_TEAM_RUNS` 계열)을 정규식으로
그대로 옮긴 것뿐이다 — 새로운 판정 기준(예: "Promoted" 같은 조직
상태)을 추가하지 않는다. 대표 run이 없는 팀은 "UNKNOWN(실행 기록
없음)"을 그대로 노출한다(가상 값 생성 금지).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIFIED_DASHBOARD_DIR = REPO_ROOT / "projects" / "unified-dashboard"
sys.path.insert(0, str(UNIFIED_DASHBOARD_DIR))

from snapshot import build_investment_hq_snapshot  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "investment-snapshot.json"

_TEAM_LINE_RE = re.compile(
    r"^(?P<name>.+?): Analysis/Bull-Bear/Trader (?P<steps>\d+)단계 완료, "
    r"Trader Decision=(?P<decision>\w+), Final Report=(?P<report>있음|없음)$"
)
_TEAM_UNKNOWN_RE = re.compile(r"^(?P<name>.+?): UNKNOWN\(실행 기록 없음\)$")


def _parse_team_line(line: str) -> dict | None:
    match = _TEAM_LINE_RE.match(line)
    if match:
        return {
            "name": match.group("name"),
            "status": f"{match.group('steps')}단계 완료, Final Report {match.group('report')}",
            "lastDecision": match.group("decision"),
        }
    unknown_match = _TEAM_UNKNOWN_RE.match(line)
    if unknown_match:
        return {
            "name": unknown_match.group("name"),
            "status": "UNKNOWN(실행 기록 없음)",
            "lastDecision": "UNKNOWN",
        }
    return None


def build_document() -> dict:
    snap = build_investment_hq_snapshot()

    teams = [team for team in (_parse_team_line(line) for line in snap.detail) if team is not None]

    return {
        "connection": "EVIDENCE",
        "status": snap.status,
        "teams": teams,
        "deferred": list(snap.deferred),
        "sourceFiles": snap.source_files,
    }


def main() -> None:
    document = build_document()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"investment-snapshot.json written to {OUTPUT_PATH}")
    print(f"- status: {document['status']}")
    print(f"- teams: {[t['name'] for t in document['teams']]}")


if __name__ == "__main__":
    main()

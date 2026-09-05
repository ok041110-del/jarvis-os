"""Dashboard Shell MVP — Investment Snapshot Generator Boundary/Functional Validation.

`projects/unified-dashboard/tests/test_snapshot.py`의 AST 기반 import
검사 방식을 재사용한다(`test_generate_development_snapshot.py`와 동일
패턴).
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import generate_investment_snapshot as gen  # noqa: E402


def _imported_top_level_modules(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def test_generator_does_not_import_hq_code():
    modules = _imported_top_level_modules(PROTOTYPE_DIR / "generate_investment_snapshot.py")
    assert "hqs" not in modules
    assert "trader" not in modules


def test_generator_reuses_unified_dashboard_build_investment_hq_snapshot():
    """새 Evidence 수집 로직을 만들지 않고 기존 함수 객체를 그대로
    가져다 쓰는지 확인한다(같은 로직을 복제하지 않았는지 검증)."""
    from snapshot import build_investment_hq_snapshot as canonical

    assert gen.build_investment_hq_snapshot is canonical


def test_document_teams_match_real_representative_runs():
    """팀 이름/순서가 snapshot.py의 _TEAM_RUNS 순서와 일치해야 한다
    (가상 팀 생성/누락 금지)."""
    from snapshot import _TEAM_RUNS

    doc = gen.build_document()
    assert [t["name"] for t in doc["teams"]] == list(_TEAM_RUNS.keys())


def test_document_teams_have_no_fabricated_status():
    """status에 "Promoted" 같은 조직 상태를 새로 지어내지 않고,
    실제 detail 문자열(단계 수/Final Report)만 옮긴 것인지 검증한다."""
    doc = gen.build_document()
    assert doc["teams"], "실제 3개 팀 detail이 있으므로 비어있으면 안 됨"
    for team in doc["teams"]:
        assert "Promoted" not in team["status"]
        assert team["lastDecision"] in {"HOLD", "BUY", "SELL", "UNKNOWN"}


def test_document_deferred_matches_snapshot_exactly():
    from snapshot import build_investment_hq_snapshot

    snap = build_investment_hq_snapshot()
    doc = gen.build_document()
    assert doc["deferred"] == list(snap.deferred)


def test_document_source_files_point_to_real_paths():
    doc = gen.build_document()
    assert doc["sourceFiles"], "실제 manifest.json 경로가 최소 1개는 있어야 함"
    for path in doc["sourceFiles"]:
        assert (gen.REPO_ROOT / path).is_file()


def test_document_is_json_serializable():
    doc = gen.build_document()
    json.dumps(doc)

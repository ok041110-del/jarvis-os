"""Unified Dashboard Prototype — Functional/Boundary Validation."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

import snapshot  # noqa: E402
from render import render_dashboard  # noqa: E402


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


def test_snapshot_module_does_not_import_hq_code():
    """Boundary 검증(Evidence Q3): Dashboard가 HQ 내부 Logic을
    import하지 않고도 상태를 표현할 수 있는가."""
    modules = _imported_top_level_modules(PROTOTYPE_DIR / "snapshot.py")
    assert "hqs" not in modules
    assert "mvp" not in modules
    assert "trader" not in modules


def test_dev_hq_snapshot_has_no_fabricated_fields():
    snap = snapshot.build_dev_hq_snapshot()
    assert snap.identity == "Development HQ"
    assert snap.status in {"NORMAL", "WORKING", "BLOCKED", "DEFERRED", "UNKNOWN"}
    assert snap.detail, "Dev HQ detail이 비어있으면 안 됨"


def test_investment_hq_snapshot_marks_portfolio_risk_execution_deferred():
    snap = snapshot.build_investment_hq_snapshot()
    assert snap.identity == "Investment HQ"
    assert "Portfolio" in snap.deferred
    assert "Risk" in snap.deferred
    assert any("Execution" in item for item in snap.deferred)
    # Freeze 범위 밖 기능이 Production처럼 detail에 등장하지 않는지 확인
    for line in snap.detail:
        assert "Portfolio" not in line
        assert "Risk" not in line


def test_investment_hq_snapshot_reads_real_dogfooding_evidence():
    snap = snapshot.build_investment_hq_snapshot()
    assert snap.source_files, "실제 manifest.json 경로가 최소 1개는 있어야 함"
    for path in snap.source_files:
        assert (snapshot.REPO_ROOT / path).is_file()


def test_investment_hq_snapshot_execution_matches_real_call_log():
    """Execution Evidence Vertical Slice: execution 필드가 실제
    checkpoints/manifest.json의 call_log를 그대로 옮긴 것인지 검증한다
    (가상 데이터 생성 금지)."""
    import json

    snap = snapshot.build_investment_hq_snapshot()
    assert snap.execution, "실제 dogfooding manifest.json에 call_log가 있으므로 execution도 비어있으면 안 됨"

    expected_total = 0
    for run_name in snapshot._TEAM_RUNS.values():
        manifest_path = snapshot.REPO_ROOT / "hqs/investment/dogfooding" / run_name / "checkpoints/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_total += len(manifest.get("call_log", []))
    assert len(snap.execution) == expected_total

    for entry in snap.execution:
        assert set(entry.keys()) == {"team", "role", "input_chars", "output_chars", "elapsed_sec"}
        assert isinstance(entry["role"], str) and entry["role"]
        assert isinstance(entry["input_chars"], int)
        assert isinstance(entry["output_chars"], int)
        assert isinstance(entry["elapsed_sec"], (int, float))


def test_dev_hq_snapshot_execution_is_empty_without_fabrication():
    """Development HQ는 per-실행 call_log 파일이 존재하지 않으므로
    execution을 빈 리스트로 유지해야 한다(§3 조사 결과와 일치)."""
    snap = snapshot.build_dev_hq_snapshot()
    assert snap.execution == []


def test_render_dashboard_produces_html_without_touching_engine_or_agent():
    snapshots = snapshot.build_global_snapshot()
    html = render_dashboard(snapshots)
    assert "<html" in html
    assert "Development HQ" in html
    assert "Investment HQ" in html
    # Boundary: 렌더러가 Engine/Agent 관련 어휘를 새로 만들어내지 않는지(스냅샷 값만 표시)
    assert "call_engine" not in html

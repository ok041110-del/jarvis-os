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


def test_render_dashboard_produces_html_without_touching_engine_or_agent():
    snapshots = snapshot.build_global_snapshot()
    html = render_dashboard(snapshots)
    assert "<html" in html
    assert "Development HQ" in html
    assert "Investment HQ" in html
    # Boundary: 렌더러가 Engine/Agent 관련 어휘를 새로 만들어내지 않는지(스냅샷 값만 표시)
    assert "call_engine" not in html

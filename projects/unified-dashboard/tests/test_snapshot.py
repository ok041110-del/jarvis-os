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


def test_investment_hq_history_discovers_all_real_run_directories():
    """History Vertical Slice: _TEAM_RUNS의 팀당 단일 하드코딩과 달리,
    History는 dogfooding 디렉터리의 실제 ticker prefix run을 전부
    열거해야 한다(가상 run 생성 금지, 누락 금지)."""
    snap = snapshot.build_investment_hq_snapshot()

    dogfooding_dir = snapshot.REPO_ROOT / "hqs/investment/dogfooding"
    expected_dirs = set()
    for prefix in snapshot._TEAM_PREFIXES.values():
        expected_dirs |= {
            p.name for p in dogfooding_dir.iterdir() if p.is_dir() and p.name.startswith(f"{prefix}-")
        }

    actual_runs = {entry["run"] for entry in snap.history}
    assert actual_runs == expected_dirs


def test_investment_hq_history_entries_have_no_fabricated_fields():
    """실행 timestamp나 SUCCESS/FAILED 상태를 만들어내지 않는지 검증:
    스키마에 허용된 키만 있어야 하고, trader_decision.md가 없는 run은
    trader_decision이 None이어야 한다(빈 문자열이나 'UNKNOWN' 아님)."""
    snap = snapshot.build_investment_hq_snapshot()
    assert snap.history, "실제 9개 run이 있으므로 history가 비어있으면 안 됨"

    allowed_keys = {"team", "run", "family", "completed_steps", "trader_decision", "final_report", "commit_order"}
    for entry in snap.history:
        assert set(entry.keys()) == allowed_keys
        assert "timestamp" not in entry and "status" not in entry
        if "hq-verify" in entry["run"] or entry["run"].startswith("efa-2026-08"):
            # trader-verify가 아닌 run에는 trader_decision.md 자체가 없다.
            assert entry["trader_decision"] is None
        assert isinstance(entry["completed_steps"], int)
        assert isinstance(entry["final_report"], bool)


def test_investment_hq_history_family_derived_literally_from_dirname():
    """family는 디렉터리명에서 prefix를 뗀 나머지 그대로다 — 팀마다
    실제 문자열이 다를 수 있다는 것(efa는 hq-verify가 아님)을 검증해
    "존재하지 않는 의미 추론 금지" 원칙을 강제한다."""
    snap = snapshot.build_investment_hq_snapshot()
    families = {entry["run"]: entry["family"] for entry in snap.history}
    assert families["aapl-hq-verify"] == "hq-verify"
    assert families["aapl-trader-verify"] == "trader-verify"
    assert families["efa-2026-08"] == "2026-08"
    assert families["efa-2026-08"] != "hq-verify"  # 억지 통일 금지


def test_investment_hq_history_commit_order_is_git_backed_not_fabricated():
    """commit_order는 실제 git log(read-only)로 구한 순위이며, 실제
    커밋 순서(hq-verify -> run2 -> trader-verify, 이전 조사에서 확인된
    순서)와 일치해야 한다."""
    snap = snapshot.build_investment_hq_snapshot()
    by_run = {entry["run"]: entry["commit_order"] for entry in snap.history}
    assert by_run["aapl-hq-verify"] < by_run["aapl-hq-verify-run2"] < by_run["aapl-trader-verify"]
    assert by_run["pg-hq-verify"] < by_run["pg-hq-verify-run2"] < by_run["pg-trader-verify"]
    assert by_run["efa-2026-08"] < by_run["efa-2026-08-run2"] < by_run["efa-trader-verify"]


def test_dev_hq_snapshot_history_is_empty_without_fabrication():
    """Development HQ는 구조화된 run History Source가 없으므로 history를
    빈 리스트로 유지해야 한다(§8 조사 결론과 일치, 임의 구현 금지)."""
    snap = snapshot.build_dev_hq_snapshot()
    assert snap.history == []


def test_render_dashboard_produces_html_without_touching_engine_or_agent():
    snapshots = snapshot.build_global_snapshot()
    html = render_dashboard(snapshots)
    assert "<html" in html
    assert "Development HQ" in html
    assert "Investment HQ" in html
    # Boundary: 렌더러가 Engine/Agent 관련 어휘를 새로 만들어내지 않는지(스냅샷 값만 표시)
    assert "call_engine" not in html

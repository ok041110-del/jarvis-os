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
    """Execution Evidence — 전체 History Run 확장 Vertical Slice:
    execution 필드가 대표 run 1개가 아니라 실제 존재하는 9개 run
    전체의 checkpoints/manifest.json call_log를 그대로 옮긴 것인지
    검증한다(가상 데이터 생성 금지, run 누락 금지)."""
    import json

    snap = snapshot.build_investment_hq_snapshot()
    assert snap.execution, "실제 dogfooding manifest.json에 call_log가 있으므로 execution도 비어있으면 안 됨"

    dogfooding_dir = snapshot.REPO_ROOT / "hqs/investment/dogfooding"
    expected_total = 0
    expected_run_names = set()
    for prefix in snapshot._TEAM_PREFIXES.values():
        for run_dir in dogfooding_dir.iterdir():
            if not (run_dir.is_dir() and run_dir.name.startswith(f"{prefix}-")):
                continue
            expected_run_names.add(run_dir.name)
            manifest_path = run_dir / "checkpoints/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            expected_total += len(manifest.get("call_log", []))
    assert len(snap.execution) == expected_total

    actual_run_names = {entry["run"] for entry in snap.execution}
    assert actual_run_names == expected_run_names, "execution의 run이 실제 존재하는 run 디렉터리와 정확히 일치해야 함"

    # Execution과 History의 run 명칭이 동일한 디렉터리명 기준이어야 함(어긋나면 안 됨).
    history_run_names = {entry["run"] for entry in snap.history}
    assert actual_run_names == history_run_names

    for entry in snap.execution:
        assert set(entry.keys()) == {"team", "run", "role", "input_chars", "output_chars", "elapsed_sec"}
        assert isinstance(entry["run"], str) and entry["run"]
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

    allowed_keys = {
        "team",
        "run",
        "family",
        "completed_steps",
        "tasks",
        "trader_decision",
        "trader_decision_detail",
        "final_report",
        "progress_total",
        "progress_pct",
    }
    for entry in snap.history:
        assert set(entry.keys()) == allowed_keys
        assert "timestamp" not in entry and "status" not in entry
        if "hq-verify" in entry["run"] or entry["run"].startswith("efa-2026-08"):
            # trader-verify가 아닌 run에는 trader_decision.md 자체가 없다.
            assert entry["trader_decision"] is None
            assert entry["trader_decision_detail"] is None
        assert isinstance(entry["completed_steps"], int)
        assert isinstance(entry["final_report"], bool)
        assert isinstance(entry["tasks"], list)
        assert all(isinstance(t, str) for t in entry["tasks"])
        assert len(entry["tasks"]) == entry["completed_steps"]


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


def test_snapshot_module_does_not_use_subprocess():
    """Snapshot Boundary Review 결론: History 때문에 git 등 외부
    프로세스를 조회하지 않는다 — snapshot.py는 subprocess를 import하지
    않는다(AST 기반, 정규식 오탐 없이 실제 import 구문만 검사)."""
    modules = _imported_top_level_modules(PROTOTYPE_DIR / "snapshot.py")
    assert "subprocess" not in modules


def test_investment_hq_history_order_is_directory_scan_only():
    """정렬은 디렉터리명 오름차순(문자열 비교)뿐이다 — 우연히 실제
    계열 진행 순서(hq-verify -> run2 -> trader-verify)와 일치하지만,
    이는 git commit 조회가 아니라 `_discover_team_run_dirs`의 `sorted()`
    결과라는 것을 검증한다."""
    snap = snapshot.build_investment_hq_snapshot()
    runs_by_team: dict[str, list[str]] = {}
    for entry in snap.history:
        runs_by_team.setdefault(entry["team"], []).append(entry["run"])
    for team, runs in runs_by_team.items():
        assert runs == sorted(runs), f"{team}의 history 순서가 디렉터리명 오름차순이 아님"


def test_dev_hq_snapshot_history_is_empty_without_fabrication():
    """Development HQ는 구조화된 run History Source가 없으므로 history를
    빈 리스트로 유지해야 한다(§8 조사 결론과 일치, 임의 구현 금지)."""
    snap = snapshot.build_dev_hq_snapshot()
    assert snap.history == []


def test_investment_hq_history_tasks_match_raw_manifest_completed_steps_order():
    """Tasks/Progress Vertical Slice: `tasks`가 실제 manifest.json의
    `completed_steps`를 순서까지 그대로 옮긴 것인지 검증한다(완료
    도착 순서 보존, Wave 순서로 재정렬하지 않음)."""
    import json

    snap = snapshot.build_investment_hq_snapshot()
    dogfooding_dir = snapshot.REPO_ROOT / "hqs/investment/dogfooding"

    checked = 0
    for entry in snap.history:
        manifest_path = dogfooding_dir / entry["run"] / "checkpoints" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert entry["tasks"] == manifest.get("completed_steps", [])
        checked += 1
    assert checked == len(snap.history)


def test_investment_hq_progress_known_only_for_trader_decision_pattern():
    """`trader_decision` 단계가 실제 관측된 run(현재 trader-verify
    계열)에서만 progress_total/progress_pct가 채워지고, `synthesis`
    패턴 레거시 run(hq-verify 등)은 두 값 모두 None으로 남아
    "0%"와 "계산 불가"를 혼동하지 않는지 검증한다."""
    snap = snapshot.build_investment_hq_snapshot()
    assert snap.history, "실제 9개 run이 있으므로 history가 비어있으면 안 됨"

    saw_current_pattern = False
    saw_legacy_pattern = False
    for entry in snap.history:
        if "trader_decision" in entry["tasks"]:
            saw_current_pattern = True
            expected_total = snapshot._TEAM_TOTAL_STEPS[entry["team"]]
            assert entry["progress_total"] == expected_total
            assert entry["progress_pct"] == round(entry["completed_steps"] / expected_total * 100, 1)
        else:
            saw_legacy_pattern = True
            assert entry["progress_total"] is None
            assert entry["progress_pct"] is None

    assert saw_current_pattern, "trader-verify 계열 run이 최소 1개는 있어야 함"
    assert saw_legacy_pattern, "hq-verify/synthesis 레거시 run이 최소 1개는 있어야 함"


def _team_step_names_from_source(team_file: Path) -> set[str]:
    """`hqs/investment/teams/*.py`의 `run()`에 실제 존재하는 Task
    이름을 import 없이 AST로만 추출한다: Wave1/Wave2는 `wave1_jobs`/
    `wave2_jobs` dict 리터럴의 키, Wave3는 `run_step(cp, "이름", ...)`
    직접 호출의 문자열 리터럴이다. Trader Task(Wave3)는
    `hqs/investment/trader.py`의 `run_trader_decision(cp, trader_decision,
    ...)`를 거치며, 그 안의 `run_step(cp, "trader_decision", ...)` 호출은
    이 파일이 아니라 `trader.py`에 있어 여기서는 보이지 않는다 —
    `run_trader_decision(...)` 호출 자체를 `"trader_decision"` 리터럴 1개로
    센다(그 이름이 검증 전 저장을 막는 checkpoint 저장 전 게이트라는
    책임은 여전히 고정이다). `_TEAM_TOTAL_STEPS`가 실제 팀 코드와
    어긋나면(drift) 이 테스트가 실패해야 한다."""
    tree = ast.parse(team_file.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            target_names = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if target_names & {"wave1_jobs", "wave2_jobs"}:
                for key in node.value.keys:
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        names.add(key.value)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "run_step"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
        ):
            names.add(node.args[1].value)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "run_trader_decision"
        ):
            names.add("trader_decision")
    return names


def test_team_total_steps_literal_matches_actual_team_source():
    """anti-drift 회귀 테스트: `snapshot._TEAM_TOTAL_STEPS`(Boundary
    때문에 팀 코드를 import하지 못해 재선언한 리터럴)가 실제
    `hqs/investment/teams/*.py`의 Task 구성과 여전히 일치하는지
    정적 분석으로 확인한다 — 팀 코드에 분석 역할이 추가/삭제되면
    이 테스트가 즉시 실패해야 한다(조용한 stale 방지)."""
    team_files = {
        "Stock (AAPL)": "stock_team.py",
        "Dividend Stock (PG)": "dividend_stock_team.py",
        "ETF (EFA)": "etf_team.py",
    }
    for team_label, filename in team_files.items():
        team_file = snapshot.REPO_ROOT / "hqs/investment/teams" / filename
        actual_names = _team_step_names_from_source(team_file)
        assert len(actual_names) == snapshot._TEAM_TOTAL_STEPS[team_label], (
            f"{team_label}: 코드상 Task 수 {len(actual_names)}개({sorted(actual_names)}) != "
            f"snapshot._TEAM_TOTAL_STEPS {snapshot._TEAM_TOTAL_STEPS[team_label]}"
        )


def test_investment_hq_trader_decision_detail_matches_real_files_for_all_teams():
    """Trader Decision Rationale/Reassess Vertical Slice: 3개 실제 Team
    (`aapl`/`pg`/`efa`)의 `trader_decision.md` 원문에서 Direction/
    Rationale/Reassess when이 실제로 추출되는지 검증한다(fixture 가공
    없이 저장소의 실제 파일을 직접 재검증). aapl/pg는
    `Direction: HOLD**`, efa는 `Direction:** HOLD`로 Bold 위치가 달라도
    `action`은 기존과 동일하게 추출돼야 한다(하위 호환)."""
    snap = snapshot.build_investment_hq_snapshot()
    by_run = {entry["run"]: entry for entry in snap.history}

    for run_name in ("aapl-trader-verify", "pg-trader-verify", "efa-trader-verify"):
        entry = by_run[run_name]
        raw_text = (
            snapshot.REPO_ROOT / "hqs/investment/dogfooding" / run_name / "trader_decision.md"
        ).read_text(encoding="utf-8")

        detail = entry["trader_decision_detail"]
        assert detail is not None, f"{run_name}: trader_decision.md가 실제 존재하므로 None이면 안 됨"
        assert set(detail.keys()) == {"action", "rationale", "reassess_when"}

        # action은 기존 trader_decision 필드와 동일해야 한다(하위 호환 유지).
        assert detail["action"] == entry["trader_decision"]
        assert detail["action"] in {"HOLD", "BUY", "SELL"}

        # Rationale/Reassess는 실제 원문에서 가져온 부분 문자열이어야 한다
        # (요약·재작성 없이 그대로 노출, 가상 텍스트 생성 금지).
        assert detail["rationale"]
        assert detail["rationale"] in raw_text
        assert detail["reassess_when"]
        assert detail["reassess_when"] in raw_text


def test_investment_hq_trader_decision_detail_none_for_legacy_runs_without_fabrication():
    """trader_decision.md 자체가 없는 legacy `hq-verify`/`efa-2026-08`
    run은 `trader_decision_detail`이 `None`이어야 한다 — 빈 문자열이나
    `{}` 같은 가짜 placeholder를 만들지 않는다."""
    snap = snapshot.build_investment_hq_snapshot()
    legacy_runs = [
        entry
        for entry in snap.history
        if "hq-verify" in entry["run"] or entry["run"].startswith("efa-2026-08")
    ]
    assert legacy_runs, "실제 legacy run이 최소 1개는 있어야 함"
    for entry in legacy_runs:
        assert entry["trader_decision_detail"] is None


def test_render_dashboard_produces_html_without_touching_engine_or_agent():
    snapshots = snapshot.build_global_snapshot()
    html = render_dashboard(snapshots)
    assert "<html" in html
    assert "Development HQ" in html
    assert "Investment HQ" in html
    # Boundary: 렌더러가 Engine/Agent 관련 어휘를 새로 만들어내지 않는지(스냅샷 값만 표시)
    assert "call_engine" not in html

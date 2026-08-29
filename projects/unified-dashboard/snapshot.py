"""Unified Dashboard Prototype — Data Acquisition.

Global dashboard/Experimental Prototype Contract. Production
Contract가 아니다(docs/research/JARVIS-OS-V2.0-UNIFIED-DASHBOARD-
PROTOTYPE-0001.md 참조).

Boundary 검증 대상: 이 모듈은 hqs/development, hqs/investment의
어떤 Python 모듈도 import하지 않는다 — 기존 Evidence 파일(Markdown/
JSON)을 읽기만 한다. Agent/Engine을 호출하지 않는다.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Prototype 내부 Presentation State — Production Contract 아님.
PresentationState = str  # "NORMAL" | "WORKING" | "BLOCKED" | "DEFERRED" | "UNKNOWN"


@dataclass
class HQSnapshot:
    """Experimental Prototype Contract — DashboardSnapshot의 최소
    View Model. 공식 HQDashboardSnapshot(docs/research/JARVIS-OS-V2.0-
    UNIFIED-DASHBOARD-ARCHITECTURE-0001.md §6)을 Freeze하지 않는다.

    `execution`은 Investment HQ Execution Evidence Vertical Slice로
    추가된 Experimental 필드다 — 기존 `checkpoints/manifest.json`의
    `call_log`를 그대로 옮긴 것뿐이며, 이 필드가 있다고 해서
    `HQSnapshot`이 Public Contract로 승격되는 것은 아니다. 값이 없는
    HQ(Development HQ 등)는 빈 리스트를 유지한다(가상 데이터 생성 금지).

    `history`는 Investment HQ History Vertical Slice로 추가된
    Experimental 필드다 — `hqs/investment/dogfooding/` 아래 실제
    존재하는 run 디렉터리(팀 prefix로 스캔)를 run 단위로 요약한다.
    파일에 없는 절대 실행 시각·SUCCESS/FAILED 상태는 만들지 않는다.
    정렬은 디렉터리 스캔 순서(문자열 오름차순)일 뿐이다 — Snapshot
    Boundary Review(2026-08) 결론에 따라 git commit 순서 조회
    (subprocess)는 도입하지 않는다: History는 최종 Dashboard 필수
    기능이 아니라 Prototype 관찰용이고, subprocess는 "Evidence
    파일을 읽기만 한다"는 이 모듈의 Boundary를 불필요하게 넓히는
    비용이 이득보다 크다고 판단했다.

    `history[].tasks`는 Investment HQ Tasks/Progress Vertical Slice로
    추가된 Experimental 필드다 — 기존에 이미 읽던 `manifest.json`의
    `completed_steps`를 개수뿐 아니라 이름 리스트 그대로 옮긴 것이다.
    이 배열의 순서는 **완료 도착 순서**다(Wave1의 분석 단계들은
    `ThreadPoolExecutor`로 병렬 실행되므로 `checkpoint.py`가 저장을
    마친 순서일 뿐, `hqs/investment/teams/*.py`가 정의한 Wave 실행
    순서(Wave1→Wave2→Wave3→Wave4)와 다르다) — 가상의 시퀀스를
    부여하지 않는다.

    `history[].progress_total`/`progress_pct`는 같은 Vertical Slice로
    추가됐다 — `_TEAM_TOTAL_STEPS`(각 팀의 `teams/*.py`에 실제 존재하는
    Wave1 분석 역할 수 + 고정 4단계를 문자 그대로 옮긴 리터럴)를
    분모로 삼는다. 이 분모는 `trader_decision` 단계가 실제로 관측된
    run(현재 `trader-verify` 계열 패턴)에만 적용한다 — `synthesis`
    단계를 쓰던 레거시 run(`hq-verify` 등)은 Task 구성 자체가 달라
    같은 분모를 강제로 적용하면 틀린 값이 되므로, 두 필드 모두
    `None`으로 남겨 "정확히 계산할 수 없음"을 그대로 드러낸다."""

    identity: str
    status: PresentationState
    detail: list[str] = field(default_factory=list)
    deferred: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
    execution: list[dict] = field(default_factory=list)
    history: list[dict] = field(default_factory=list)


def _read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def build_dev_hq_snapshot() -> HQSnapshot:
    """hqs/development/의 기존 Freeze 문서·파일 존재만으로 상태를
    관찰한다. Stage/Agent 코드를 import하지 않는다."""

    freeze_doc = REPO_ROOT / "docs/architecture/core/DEVELOPMENT-HQ-V2.0-FREEZE-0001.md"
    text = _read_text(freeze_doc)

    if text is None:
        return HQSnapshot(identity="Development HQ", status="UNKNOWN", detail=["Freeze 문서를 찾을 수 없음"])

    passed_match = re.search(r"회귀\s*테스트\s*\|\s*(\d+)\s*passed", text)
    latest_validation = f"{passed_match.group(1)} passed" if passed_match else "UNKNOWN(문서에서 추출 실패)"

    agents_dir = REPO_ROOT / "hqs/development/mvp/agents"
    agent_files = sorted(p.stem for p in agents_dir.glob("*.py") if p.stem != "__init__") if agents_dir.is_dir() else []

    detail = [
        f"Phase: Stable v2.0 Freeze (RFC-0007 -> ADC-0005 -> ADR-0008 -> Stage 01~05 -> Integrated Workflow -> CLI)",
        f"Workflow: Stage 01~05 (01_repository_intelligence ~ 05_devops_release 명명, workflow.py로 연쇄)",
        f"Agent Roles: {', '.join(agent_files) if agent_files else 'UNKNOWN'}",
        f"Latest Validation: {latest_validation}",
        "Current Task: None (idle — 상시 Runtime 없음, 명시적 호출 시에만 실행됨, ADC-02 Open)",
    ]

    return HQSnapshot(
        identity="Development HQ",
        status="NORMAL",
        detail=detail,
        source_files=[str(freeze_doc.relative_to(REPO_ROOT)), str(agents_dir.relative_to(REPO_ROOT)) + "/*.py"],
    )


_DIRECTION_RE = re.compile(r"Direction:\**\s*([A-Za-z]{3,10})", re.IGNORECASE)

# 팀 식별에 실제로 쓸 수 있는 유일한 근거: dogfooding 디렉터리명이 전부
# "{ticker prefix}-..." 형태다(History Architecture Investigation §2에서
# 9개 디렉터리 전수 확인, 예외 없음). Representative run(detail/execution/
# status 계산용, 기존 동작 유지)은 team별 trader-verify 1개로 고정한다.
_TEAM_PREFIXES = {
    "Stock (AAPL)": "aapl",
    "Dividend Stock (PG)": "pg",
    "ETF (EFA)": "efa",
}
_TEAM_RUNS = {
    "Stock (AAPL)": "aapl-trader-verify",
    "Dividend Stock (PG)": "pg-trader-verify",
    "ETF (EFA)": "efa-trader-verify",
}

# 팀별 전체 Task 수 — `hqs/investment/teams/*.py`의 `run()`에 실제
# 존재하는 Wave1 분석 역할 수(dict 리터럴 키 개수) + 고정 4단계
# (bull_case, bear_case, trader_decision, final_report)를 그대로 옮긴
# 값이다(팀 코드를 import하지 않으므로 리터럴로 재선언, 회귀 테스트로
# drift 감지). `trader_decision` 단계가 실제 관측되는 현재
# `trader-verify` 계열 run에만 적용한다.
_TEAM_TOTAL_STEPS = {
    "Stock (AAPL)": 9,  # fundamental/technical/industry/news_event/sentiment(5) + bull_case + bear_case + trader_decision + final_report
    "Dividend Stock (PG)": 11,  # fundamental/dividend_quality/valuation/technical/industry/news_event/sentiment(7) + 4
    "ETF (EFA)": 10,  # composition/holdings_exposure/cost_tracking/performance_risk/distribution/macro(6) + 4
}


def _progress_for_run(team_label: str, tasks: list[str]) -> tuple[int | None, float | None]:
    """`trader_decision` 단계가 실제로 관측된 run에만 진행률을
    계산한다 — `synthesis` 패턴(레거시 `hq-verify` 등)은 Task 구성
    자체가 달라 같은 분모를 강제하지 않는다(존재하지 않는 기준
    임의 부여 금지)."""
    if "trader_decision" not in tasks:
        return None, None
    total = _TEAM_TOTAL_STEPS.get(team_label)
    if total is None:
        return None, None
    return total, round(len(tasks) / total * 100, 1)


def _discover_team_run_dirs(dogfooding_dir: Path, prefix: str) -> list[Path]:
    """ticker prefix(`{prefix}-...`)로 시작하는 실제 존재하는 run
    디렉터리를 전부 찾는다 — 하드코딩된 이름 하나만 보지 않는다."""
    if not dogfooding_dir.is_dir():
        return []
    return sorted(p for p in dogfooding_dir.iterdir() if p.is_dir() and p.name.startswith(f"{prefix}-"))


def _run_family(run_dir_name: str, prefix: str) -> str:
    """디렉터리명에서 prefix를 뗀 나머지를 그대로 계열명으로 쓴다 —
    팀마다 실제 문자열이 다를 수 있으므로(예: efa는 hq-verify가 아니라
    2026-08) 억지로 통일하지 않는다(존재하지 않는 의미 추론 금지)."""
    return run_dir_name[len(prefix) + 1 :]


def _read_team_run(run_dir: Path) -> dict:
    manifest_path = run_dir / "checkpoints" / "manifest.json"
    if not manifest_path.is_file():
        return {"completed_steps": [], "action": None, "final_report": False, "call_log": []}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    completed = manifest.get("completed_steps", [])
    call_log = manifest.get("call_log", [])

    action = None
    decision_text = _read_text(run_dir / "trader_decision.md")
    if decision_text:
        match = _DIRECTION_RE.search(decision_text)
        if match:
            action = match.group(1).upper()

    return {
        "completed_steps": completed,
        "action": action,
        "final_report": (run_dir / "final_report.md").is_file(),
        "call_log": call_log,
    }


def build_investment_hq_snapshot() -> HQSnapshot:
    """hqs/investment/dogfooding/*-trader-verify의 기존 checkpoint
    manifest.json·trader_decision.md만 읽는다. trader.py를 import
    하지 않는다(Boundary 검증 대상, Q3)."""

    dogfooding_dir = REPO_ROOT / "hqs/investment/dogfooding"
    detail = []
    source_files = []
    execution: list[dict] = []

    any_found = False
    for team_label, run_name in _TEAM_RUNS.items():
        run_dir = dogfooding_dir / run_name
        if not run_dir.is_dir():
            detail.append(f"{team_label}: UNKNOWN(실행 기록 없음)")
            continue
        any_found = True
        run = _read_team_run(run_dir)
        steps = len(run["completed_steps"])
        action = run["action"] or "UNKNOWN"
        report = "있음" if run["final_report"] else "없음"
        detail.append(f"{team_label}: Analysis/Bull-Bear/Trader {steps}단계 완료, Trader Decision={action}, Final Report={report}")
        source_files.append(str((run_dir / "checkpoints/manifest.json").relative_to(REPO_ROOT)))
        for call in run["call_log"]:
            execution.append(
                {
                    "team": team_label,
                    "role": call.get("role", "UNKNOWN"),
                    "input_chars": call.get("input_chars", 0),
                    "output_chars": call.get("output_chars", 0),
                    "elapsed_sec": call.get("elapsed_sec", 0),
                }
            )

    status: PresentationState = "NORMAL" if any_found else "UNKNOWN"

    history = _build_investment_history(dogfooding_dir)

    return HQSnapshot(
        identity="Investment HQ",
        status=status,
        detail=detail,
        deferred=["Portfolio", "Risk", "Execution (Trade Execution)"],
        source_files=source_files,
        execution=execution,
        history=history,
    )


def _build_investment_history(dogfooding_dir: Path) -> list[dict]:
    """팀별 prefix로 dogfooding 디렉터리를 스캔해 실제 존재하는 run을
    전부 History로 열거한다(하드코딩된 단일 run만 보던 기존 detail/
    execution과 달리, 9개 run 전부 대상). run family는 디렉터리명
    그대로, 정렬은 `_discover_team_run_dirs`가 반환하는 디렉터리명
    오름차순뿐이다 — git이나 다른 외부 프로세스를 조회하지 않는다
    (Snapshot Boundary Review 결론, 위 HQSnapshot docstring 참조)."""
    entries: list[dict] = []
    for team_label, prefix in _TEAM_PREFIXES.items():
        for run_dir in _discover_team_run_dirs(dogfooding_dir, prefix):
            run = _read_team_run(run_dir)
            tasks = run["completed_steps"]
            progress_total, progress_pct = _progress_for_run(team_label, tasks)
            entries.append(
                {
                    "team": team_label,
                    "run": run_dir.name,
                    "family": _run_family(run_dir.name, prefix),
                    "completed_steps": len(tasks),
                    "tasks": tasks,
                    "trader_decision": run["action"],
                    "final_report": run["final_report"],
                    "progress_total": progress_total,
                    "progress_pct": progress_pct,
                }
            )
    return entries


def build_global_snapshot() -> list[HQSnapshot]:
    return [build_dev_hq_snapshot(), build_investment_hq_snapshot()]

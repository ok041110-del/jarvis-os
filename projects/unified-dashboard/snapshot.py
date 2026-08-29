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
    HQ(Development HQ 등)는 빈 리스트를 유지한다(가상 데이터 생성 금지)."""

    identity: str
    status: PresentationState
    detail: list[str] = field(default_factory=list)
    deferred: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
    execution: list[dict] = field(default_factory=list)


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
_TEAM_RUNS = {
    "Stock (AAPL)": "aapl-trader-verify",
    "Dividend Stock (PG)": "pg-trader-verify",
    "ETF (EFA)": "efa-trader-verify",
}


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

    return HQSnapshot(
        identity="Investment HQ",
        status=status,
        detail=detail,
        deferred=["Portfolio", "Risk", "Execution (Trade Execution)"],
        source_files=source_files,
        execution=execution,
    )


def build_global_snapshot() -> list[HQSnapshot]:
    return [build_dev_hq_snapshot(), build_investment_hq_snapshot()]

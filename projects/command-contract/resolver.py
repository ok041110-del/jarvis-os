"""Command Resolver — Case A: User -> Command -> HQ (Task 없이).

Engine/Agent를 호출하지 않는다. `projects/unified-dashboard/`의
읽기 전용 Snapshot Builder만 재사용한다(Prototype 간 연결, Production
External Interface Contract 아님 — 작업 지시 §12).

HQ Business Logic을 이 모듈이 소유하지 않는다: HQ별 상태 해석은
전부 `unified-dashboard/snapshot.py`에 있고, 이 모듈은 "어떤 HQ를
호출할지"만 결정한다(Command Resolution 책임).
"""

from __future__ import annotations

import sys
from pathlib import Path

_DASHBOARD_PROTOTYPE_DIR = Path(__file__).resolve().parents[1] / "unified-dashboard"
sys.path.insert(0, str(_DASHBOARD_PROTOTYPE_DIR))

from snapshot import build_dev_hq_snapshot, build_investment_hq_snapshot  # noqa: E402

from command import Command, CommandResult  # noqa: E402

_HQ_KEYWORDS = {
    "development": ("dev", "development", "개발"),
    "investment": ("invest", "investment", "투자"),
}

_SUPPORTED_INTENTS = {"show_status"}

_SNAPSHOT_BUILDERS = {
    "development": build_dev_hq_snapshot,
    "investment": build_investment_hq_snapshot,
}


def _detect_hq(raw_input: str) -> str | None:
    lowered = raw_input.lower()
    for hq, keywords in _HQ_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return hq
    return None


def _detect_intent(raw_input: str) -> str | None:
    lowered = raw_input.lower()
    if "상태" in raw_input or "status" in lowered or "보여줘" in raw_input or "show" in lowered:
        return "show_status"
    if "실행" in raw_input or "execute" in lowered or "run" in lowered:
        return "execute_workflow"  # 인식은 되지만 이 Prototype이 지원하지 않는 intent
    return None


def parse_command(raw_input: str) -> Command:
    """User Input -> Command. 파싱 실패 시에도 Command 자체는
    생성된다(intent/target_hq가 None으로 남을 뿐) — 오류 판정은
    resolve()가 담당한다."""

    return Command(
        raw_input=raw_input,
        intent=_detect_intent(raw_input),
        target_hq=_detect_hq(raw_input),
    )


def resolve(command: Command) -> CommandResult:
    """Command -> HQ Target -> Read-only Snapshot -> Result.
    Task 계층을 거치지 않는다(Case A)."""

    if command.intent is None:
        return CommandResult(status="invalid", reason="unknown_command")
    if command.intent not in _SUPPORTED_INTENTS:
        return CommandResult(status="invalid", reason="unsupported_intent")
    if command.target_hq is None:
        return CommandResult(status="invalid", reason="unknown_hq")

    builder = _SNAPSHOT_BUILDERS.get(command.target_hq)
    if builder is None:
        return CommandResult(status="invalid", reason="unknown_hq")

    snapshot = builder()
    return CommandResult(
        status="ok",
        hq_identity=snapshot.identity,
        detail=list(snapshot.detail),
    )


def run_command(raw_input: str) -> CommandResult:
    """User Input을 한 번에 처리하는 진입점(Case A 전체 흐름)."""

    return resolve(parse_command(raw_input))

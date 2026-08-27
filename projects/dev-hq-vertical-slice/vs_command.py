"""Command — immutable Value Object. Development HQ 단독 범위(Multi-HQ 없음).

`command-contract` Prototype과 동일한 원칙(불변, 파싱 실패도 Command
자체는 생성됨)을 따르되, 이번엔 HQ 판별이 아니라 "Dev HQ의 어떤
Validation Action을 실행할지"만 판별한다 — 범위가 Dev HQ 하나로
좁혀졌으므로 HQ 판별 로직(`resolver._detect_hq`)은 재사용하지
않는다(불필요한 재사용은 과도한 결합).
"""

from __future__ import annotations

from dataclasses import dataclass

from vs_dev_hq_adapter import ACTIONS

_ACTION_KEYWORDS = {
    "ast_context": ("ast_context", "ast context", "ast 컨텍스트"),
    "stage_01": ("stage_01", "stage 1", "1단계"),
    "mvp_0001": ("mvp_0001", "mvp 워크플로", "mvp workflow"),
}


@dataclass(frozen=True)
class Command:
    raw_input: str
    action: str | None


def parse_command(raw_input: str) -> Command:
    lowered = raw_input.lower()
    for action, keywords in _ACTION_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return Command(raw_input=raw_input, action=action)
    return Command(raw_input=raw_input, action=None)


def is_known_action(action: str | None) -> bool:
    return action in ACTIONS

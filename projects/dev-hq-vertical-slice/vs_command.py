"""Command — immutable Value Object. Development HQ 단독 범위(Multi-HQ 없음).

command-contract와 같은 불변 원칙을 따르되, 범위가 Dev HQ로 좁혀졌으므로 HQ 판별 로직(resolver._detect_hq)은 재사용하지 않는다.
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

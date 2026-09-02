"""Trader 호출 출력의 REPORT/DECISION 분리·파싱 유틸리티(세 Team 공유).
Registry/Scheduler가 아니다 — 고정된 텍스트 처리만 한다."""

import re

from checkpoint import run_step

# Prototype 검증본과 동일 문구 — "not a trade order" 문장 대체용.
TRADER_DECISION_INSTRUCTION = (
    "\n\n추가로, 여기 주어진 정보만을 근거로 이 개별 증권에 대한 현재 시점의 방향성 입장을 결정하라. "
    "Portfolio 맥락, 기존 보유 포지션, 자본 배분, 포지션 규모는 가정하지 마라 — "
    "판단을 완성하는 데 그런 정보가 필요하다면 추측하거나 지어내지 말고 명시적으로 그렇다고 말하라. "
    "당신의 범위는 이 단일 증권의 현재 정보 기준 방향성 입장으로 한정된다 — "
    "당신은 Portfolio Manager가 아니며 Portfolio 수준의 판단을 시도해서는 안 된다.\n\n"
    "다음 정확한 헤더를 사용해 명확히 분리된 두 섹션으로만 답하라:\n\n"
    "## REPORT\n"
    "사람 독자에게 필요한 모든 것: 위에서 설명한 것과 동일한 종합"
    "(사실 대 해석, 충돌 지점, 미해결 질문)을 중립적이고 방향성 없는 산문으로 작성하라. "
    "이 섹션 어디에도 방향 판단을 두지 마라 — "
    "buy/sell/hold 지시가 전혀 없는 독립적 분석으로 읽혀야 한다.\n\n"
    "## DECISION\n"
    "- Direction: BUY / SELL / HOLD 중 정확히 하나를 선택하라\n"
    "- Rationale: 2-4문장, 오직 위 REPORT 섹션에만 근거하고 새로운 사실을 추가하지 마라\n"
    "- Reassess when: REPORT에서 해소될 경우 이 Direction을 가장 크게 바꿀 가능성이 있는, "
    "판단에 가장 결정적인 미해결 질문 하나를 명시하라"
)


class TraderOutputError(ValueError):
    """REPORT/DECISION 헤더 구조가 없을 때 발생. `run_trader_decision()`을 통해
    호출하면 `ContentFailureError`처럼 checkpoint 저장 전에 발생해 다음 실행에서
    자동 재시도된다 — `run_step()`에 원본 `trader_decision` 함수를 직접 넘기면
    검증이 저장 이후에 일어나 이 보장이 깨진다."""


_REPORT_HEADER = re.compile(r"^##\s*REPORT\s*$", re.MULTILINE)
_DECISION_HEADER = re.compile(r"^##\s*DECISION\s*$", re.MULTILINE)


def split_report_decision(raw: str) -> tuple[str, str]:
    """원본 출력을 (report_text, decision_text)로 나눈다 — 두 섹션을
    합치지 않는다."""
    report_match = _REPORT_HEADER.search(raw)
    decision_match = _DECISION_HEADER.search(raw)
    if not report_match or not decision_match or decision_match.start() <= report_match.start():
        raise TraderOutputError(
            "Trader output missing well-formed '## REPORT' / '## DECISION' "
            f"headers in order: {raw[:200]!r}"
        )
    report_text = raw[report_match.end():decision_match.start()].strip()
    decision_text = raw[decision_match.end():].strip()
    return report_text, decision_text


def run_trader_decision(cp, trader_decision_fn, bull_case: str, bear_case: str) -> str:
    """`trader_decision_fn(bull_case, bear_case)` 호출 결과를 checkpoint에
    저장하기 전에 `split_report_decision()`으로 형식을 검증한다. 세 Team
    (`stock_team.py`/`etf_team.py`/`dividend_stock_team.py`)이 각자
    `run_step(cp, "trader_decision", trader_decision, ...)`을 직접 호출하지
    않고 이 함수를 거쳐야 `TraderOutputError`가 저장 전에 발생해 다음
    실행에서 자동 재시도된다."""

    def _validated(b: str, c: str) -> str:
        raw = trader_decision_fn(b, c)
        split_report_decision(raw)
        return raw

    return run_step(cp, "trader_decision", _validated, bull_case, bear_case)


_DIRECTION_RE = re.compile(r"Direction:\**\s*([A-Za-z ]{3,20})", re.IGNORECASE)
_RATIONALE_RE = re.compile(r"Rationale:\**\s*(.+?)(?=\n-\s*\**Reassess|\Z)", re.IGNORECASE | re.DOTALL)
_REASSESS_RE = re.compile(r"Reassess when:\**\s*(.+)", re.IGNORECASE | re.DOTALL)
# set이 아닌 고정 순서 tuple — 후보 문자열에 방향 단어가 둘 이상 섞인
# 모호한 응답에서도 어떤 단어를 고를지가 set 순회 순서(프로세스마다
# 문자열 해시가 랜덤화돼 달라질 수 있음)에 좌우되지 않고 항상 동일하게
# 결정되게 한다.
_VALID_ACTIONS = ("BUY", "SELL", "HOLD")


def parse_decision(decision_text: str) -> dict:
    """action/rationale/reassessment_trigger를 추출한다. 필드가 없어도
    예외를 던지지 않고 `warnings`에 기록한다(Contract 미확정 반영)."""
    warnings: list[str] = []

    action = None
    direction_match = _DIRECTION_RE.search(decision_text)
    if direction_match:
        candidate = direction_match.group(1).strip().upper()
        # 지시문 재인용이 아닌 실제 선택 단어만 취한다.
        for word in _VALID_ACTIONS:
            if word in candidate:
                action = word
                break
    if action is None:
        warnings.append("action missing or unrecognized")

    rationale = None
    rationale_match = _RATIONALE_RE.search(decision_text)
    if rationale_match:
        rationale = rationale_match.group(1).strip()
    if not rationale:
        warnings.append("rationale missing")

    reassessment_trigger = None
    reassess_match = _REASSESS_RE.search(decision_text)
    if reassess_match:
        reassessment_trigger = reassess_match.group(1).strip()
    if not reassessment_trigger:
        warnings.append("reassessment_trigger missing")

    return {
        "action": action,
        "rationale": rationale,
        "reassessment_trigger": reassessment_trigger,
        "warnings": warnings,
    }

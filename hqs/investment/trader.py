"""Trader 호출 출력의 REPORT/DECISION 분리·파싱 유틸리티(세 Team 공유).
Registry/Scheduler가 아니다 — 고정된 텍스트 처리만 한다."""

import re

# Prototype 검증본과 동일 문구 — "not a trade order" 문장 대체용.
TRADER_DECISION_INSTRUCTION = (
    "\n\nIn addition, decide a present-moment directional stance for this "
    "individual security based only on the information given here. Do "
    "not assume any portfolio context, existing position, capital "
    "allocation, or position sizing — if such information would be "
    "needed to complete a judgment, say so explicitly instead of "
    "guessing or inventing it. Your scope is limited to this single "
    "security's current-information directional stance; you are not a "
    "portfolio manager and must not attempt portfolio-level judgments.\n\n"
    "Produce your answer in exactly two clearly separated sections using "
    "these exact headers:\n\n"
    "## REPORT\n"
    "Everything a human reader needs: the synthesis exactly as described "
    "above (facts vs. interpretation, conflicts, open questions), written "
    "as neutral, non-directional prose. Do not place a directional "
    "decision anywhere in this section — it must remain readable as a "
    "standalone analysis with no buy/sell/hold instruction embedded in "
    "it.\n\n"
    "## DECISION\n"
    "- Direction: pick exactly one of BUY / SELL / HOLD\n"
    "- Rationale: 2-4 sentences, grounded only in the REPORT section "
    "above, no new facts\n"
    "- Reassess when: state the single most decision-relevant open "
    "question from the REPORT that, if resolved, would most likely "
    "change this Direction"
)


class TraderOutputError(ValueError):
    """REPORT/DECISION 헤더 구조가 없을 때 발생 — `run_step()`이 저장 전에
    받으므로 `ContentFailureError`처럼 다음 실행에서 자동 재시도된다."""


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


_DIRECTION_RE = re.compile(r"Direction:\**\s*([A-Za-z ]{3,20})", re.IGNORECASE)
_RATIONALE_RE = re.compile(r"Rationale:\**\s*(.+?)(?=\n-\s*\**Reassess|\Z)", re.IGNORECASE | re.DOTALL)
_REASSESS_RE = re.compile(r"Reassess when:\**\s*(.+)", re.IGNORECASE | re.DOTALL)
_VALID_ACTIONS = {"BUY", "SELL", "HOLD"}


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

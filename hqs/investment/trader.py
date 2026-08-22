"""REPORT/DECISION 분리 및 파싱 — 세 Team이 공유하는 순수 텍스트 처리
유틸리티. `docs/research/INVESTMENT-HQ-SYNTHESIS-TRADER-EXPANSION-
PROTOTYPE-0001.md`(4회 실제 Engine 검증) 및 `INVESTMENT-HQ-TRADER-
DECISION-DISCRIMINATION-DOGFOODING-0001.md`(6회 실제 Engine 검증)에서
확정된 결과를 그대로 옮긴 것이다.

Registry/Scheduler가 아니다 — Team마다 다른 Engine 호출(analyst 지시문
등)을 대신 실행하거나 선택하지 않는다. 이 모듈은 "Trader 단일 호출의
출력 문자열을 REPORT/DECISION 두 부분으로 나누고, DECISION에서
action/rationale/reassessment_trigger를 뽑아내는 것"만 한다 —
`IMPLEMENTATION_RULES.md`가 금지하는 일반화된 조회 API나 동적 등록을
추가하지 않는다.

Contract는 Evidence-first다: `confidence`/`position_size`/
`time_horizon`/`risk_notes`는 Evidence 부족 또는 Portfolio 책임으로
전이됐다는 판정(`INVESTMENT-HQ-TRADER-NEED-REVALIDATION-0001` 등)에
따라 이 모듈에 없다.
"""

import re

# 기존 synthesis_judgment() 지시문(Team마다 "stock"/"ETF" 등 대상
# 명사만 다름)에 그대로 이어붙이는 Decision 책임 — 프롬프트 문구는
# Prototype 검증본과 동일(§0 "not a trade order" 문장만 제거하고
# 이 문구로 대체).
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
    """Trader 호출 결과가 REPORT/DECISION 헤더 구조 자체를 갖추지 못했을
    때 발생한다. `run_step()`이 이 예외를 `cp.save()` 이전에 받으므로
    체크포인트에 저장되지 않고, 다음 실행에서 그대로 재시도(Resume)
    대상이 된다 — `ContentFailureError`와 동일한 self-healing 성격."""


_REPORT_HEADER = re.compile(r"^##\s*REPORT\s*$", re.MULTILINE)
_DECISION_HEADER = re.compile(r"^##\s*DECISION\s*$", re.MULTILINE)


def split_report_decision(raw: str) -> tuple[str, str]:
    """Trader 호출의 원본 출력을 (report_text, decision_text)로 나눈다.
    호출부는 report_text만 Final Report에, decision_text만 Decision
    산출물에 쓴다 — 두 섹션을 하나로 합치지 않는다."""
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
    """DECISION 섹션에서 action/rationale/reassessment_trigger를
    최선의 노력으로 추출한다. 개별 필드가 없어도 예외를 던지지 않는다
    — 이는 Trader Contract Evidence가 아직 완전히 확정되지 않은
    상태(action만 강한 Evidence, 나머지는 Evidence-first로 보류)를
    반영한다. 대신 `warnings`에 기록해 호출부가 로그/call_log에 남길
    수 있게 한다."""
    warnings: list[str] = []

    action = None
    direction_match = _DIRECTION_RE.search(decision_text)
    if direction_match:
        candidate = direction_match.group(1).strip().upper()
        # "pick exactly one of BUY / SELL / HOLD" 같은 지시문 재인용이
        # 아니라 실제 선택된 단어만 취한다.
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

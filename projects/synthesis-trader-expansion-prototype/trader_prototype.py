"""Synthesis -> Trader 확장 Prototype.

격리된 Prototype 디렉토리(roadmap.md의 기존 관행: `projects/*-prototype/`).
`hqs/investment/teams/stock_team.py`의 `synthesis_judgment()`를 수정하지
않는다 — 기존 함수를 그대로 import해서 "원본 Synthesis"와 "확장된
Trader"를 같은 입력(Bull/Bear)에 대해 나란히 돌려 비교하기 위한
1회성 실험 스크립트다. 실행 후에도 `hqs/investment/`는 무수정으로
남는다(diff로 확인 가능).

Trader 확장 프롬프트는 기존 `synthesis_judgment()`의 지시문을 그대로
포함하고(종합 책임 유지, Q2), 그 뒤에 Decision 책임만 추가한다
(§4 최소 변경 원칙). confidence/time_horizon/risk_notes 등은 프롬프트
어디에도 요청하지 않는다(§6 Contract-First 금지).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "hqs" / "development" / "mvp"))
sys.path.insert(0, str(REPO_ROOT / "hqs" / "investment"))
sys.path.insert(0, str(REPO_ROOT / "hqs" / "investment" / "teams"))

from engine import call_engine  # noqa: E402
from stock_team import synthesis_judgment  # noqa: E402  (원본 그대로 재사용, 무수정)

_DATA_LIMITATION_NOTICE = (
    "You are given only the data explicitly provided below (collected via web "
    "search at a specific point in time, not live data). Do not invent numbers, "
    "dates, or facts not present in the provided data. If the data is "
    "insufficient or inconsistent for a judgment, say so explicitly rather than "
    "filling the gap."
)


def trader_expanded(bull_case: str, bear_case: str) -> str:
    """확장된 Trader — 기존 synthesis_judgment() 지시문 + Decision 책임만 추가.

    최소 변경 원칙(§3): 원본 지시문 문장(Bull/Bear 종합, 사실 vs 해석
    구분, 미해결 질문 도출)을 한 글자도 바꾸지 않고 그대로 포함한다.
    "not a trade order" 문장만 제거하고(그 자리에 Decision 책임을
    추가하는 것이 이 Prototype의 목적이므로), 그 외 원본 문장은
    그대로 유지한다.
    """
    instruction = (
        "You are synthesizing a Bull Case and a Bear Case for the same stock "
        "into a balanced judgment. Identify where they actually conflict on "
        "facts vs. where they interpret the same facts differently, and state "
        "which open questions would most change the conclusion.\n\n"
        "In addition, decide a present-moment directional stance for this "
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
    payload = f"[BULL CASE]\n{bull_case}\n\n[BEAR CASE]\n{bear_case}"
    prompt = f"TRADER:{instruction} {_DATA_LIMITATION_NOTICE}\n\n{payload}"
    return call_engine(prompt)


CASES = {
    "aapl": REPO_ROOT / "hqs/investment/dogfooding/aapl-hq-verify",
    "cat": REPO_ROOT / "projects/stock-analysis-cat/issues/0001-cat-analysis",
    "pg": REPO_ROOT / "hqs/investment/dogfooding/pg-hq-verify",
    "qqq": REPO_ROOT / "projects/etf-analysis-qqq/issues/0001-qqq-analysis",
    # Discrimination Dogfooding 추가 사례(가장 편향된 Bull/Bear 후보) — 동일 template, 무수정.
    "nvda": REPO_ROOT / "projects/stock-analysis-nvda/issues/0001-nvda-analysis",
    "jnj": REPO_ROOT / "projects/dividend-stock-analysis-jnj/issues/0001-jnj-analysis",
}


def main():
    out_dir = Path(__file__).resolve().parent / "results"
    out_dir.mkdir(exist_ok=True)
    only = sys.argv[1:] if len(sys.argv) > 1 else list(CASES)
    for name in only:
        case_dir = CASES[name]
        bull = (case_dir / "bull_case.md").read_text(encoding="utf-8")
        bear = (case_dir / "bear_case.md").read_text(encoding="utf-8")
        print(f"[{name}] calling expanded Trader...", flush=True)
        result = trader_expanded(bull, bear)
        (out_dir / f"{name}_trader_expanded.md").write_text(result, encoding="utf-8")
        print(f"[{name}] done, {len(result)} chars written", flush=True)


if __name__ == "__main__":
    main()

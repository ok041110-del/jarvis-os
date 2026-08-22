"""Risk -> Portfolio 변경 재검증 — 격리된 Prototype.

이전 Risk/Portfolio Boundary Dogfooding(§13 선행조건 2·4)을 그대로
따른다:

1. 정책을 명시적으로 위반하는 수준의 look-through 노출을 가진
   Portfolio State를 구성한다(실제 QQQ 공개 비중을 그대로 사용,
   신규 종목/시장 데이터 생성 없음 — 정책 숫자와 직접 보유 비중만
   이 실험을 위한 가상 설정값).
2. Risk 단계에 이번엔 "행동을 추천할 권한"을 명시적으로 부여한다
   (이전 실험과 반대).
3. Portfolio를 두 번 분리해서 묻는다 — PASS1(Risk 정보 없이 최초
   결론) → PASS2(Risk-only, 정책 위반 여부를 명시적으로 계산해
   확인하고 행동을 추천) → PASS3(PASS1의 결론과 PASS2의 Risk
   결과만 주고, 결론이 바뀌는지 순수하게 재질문).

`hqs/investment/`는 수정하지 않는다.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "hqs" / "development" / "mvp"))
from engine import call_engine  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"

# 실제 QQQ 공개 비중(AAPL~7.1-7.3%, NVDA~8.5-8.9%, 기존 bull_case.md)을
# 그대로 쓰되, Direct 비중과 QQQ 비중, 그리고 정책 숫자는 "정책을
# 명백히 위반하는 상황"을 만들기 위해 이번 실험용으로 가상 설정했다.
PORTFOLIO_STATE = """[PORTFOLIO STATE — hypothetical, constructed for this exercise]
Direct Holding: AAPL, 8% of portfolio value. Trader Decision: HOLD.
Direct Holding: NVDA, 8% of portfolio value. Trader Decision: HOLD.
ETF Holding: QQQ, 30% of portfolio value. Trader Decision: HOLD.
  QQQ's own disclosed composition (existing real ETF Team analysis, not invented):
  - AAPL: ~7.1-7.3% of QQQ's assets
  - NVDA: ~8.5-8.9% of QQQ's assets
STATED PORTFOLIO POLICY (explicit, configured for this portfolio):
  "Combined look-through exposure to any single underlying name (direct
  holding + indirect exposure via any ETF) must not exceed 10% of total
  portfolio value."
"""


def decisions_block(*cases: str) -> str:
    parts = []
    for c in cases:
        text = (RESULTS / f"{c}_trader_expanded.md").read_text(encoding="utf-8")
        idx = text.index("## DECISION")
        parts.append(f"[TRADER DECISION — {c.upper()}]\n{text[idx:].strip()}")
    return "\n\n".join(parts)


PASS1_PROMPT = (
    "PASS1-PORTFOLIO-INITIAL:Answer strictly a Portfolio composition "
    "question: given this portfolio state and these independent "
    "per-security Trader Decisions, how should this portfolio be composed "
    "or adjusted? Do not run a policy-compliance check yourself unless it "
    "is trivially obvious without combining numbers across ETF and direct "
    "holdings — this pass is about ordinary composition reasoning, not "
    "risk or compliance analysis. Do not invent facts beyond what is "
    "given.\n\n"
)

PASS2_PROMPT = (
    "PASS2-RISK-WITH-AUTHORITY:You are now the Risk reviewer, and unlike "
    "prior exercises, you ARE authorized to recommend a specific "
    "mitigating action if you find a real problem. Steps: (1) List each "
    "Exposure Path to AAPL and to NVDA separately (Direct, and "
    "Indirect-via-QQQ) without merging them. (2) Then, and only for the "
    "specific purpose of checking the stated policy, compute the combined "
    "look-through exposure for AAPL and for NVDA (direct % + ETF% x "
    "constituent%), label this clearly as 'policy-compliance calculation' "
    "(not a claim about 'true single exposure'), and state whether it "
    "breaches the stated 10% policy. (3) If it breaches, recommend a "
    "specific concrete action (e.g. trim which position, by roughly how "
    "much) that would bring the combined figure back under policy. Do not "
    "invent facts beyond what is given.\n\n"
)


def pass3_prompt(pass1_text: str, pass2_text: str) -> str:
    return (
        "PASS3-PORTFOLIO-RECONSIDER:Below are two prior, independent "
        "analyses of the same portfolio: PASS1 is a Portfolio-only "
        "composition conclusion produced with no risk/compliance "
        "analysis. PASS2 is a Risk reviewer's assessment, which was "
        "authorized to recommend action and did compute a policy-"
        "compliance check. Read both, then answer concretely: does "
        "PASS2's finding change PASS1's composition conclusion? Answer "
        "with an explicit before/after: what PASS1 concluded, what the "
        "conclusion is now after considering PASS2, and whether these two "
        "are actually different actions or the same action restated. Do "
        "not invent facts beyond what is given in PASS1 or PASS2.\n\n"
        f"[PASS1 — PORTFOLIO-ONLY CONCLUSION]\n{pass1_text}\n\n"
        f"[PASS2 — RISK ASSESSMENT WITH AUTHORITY TO RECOMMEND]\n{pass2_text}\n\n"
        f"{PORTFOLIO_STATE}"
    )


def main():
    RESULTS.mkdir(exist_ok=True)
    decisions = decisions_block("aapl", "nvda", "qqq")

    print("[pass1] portfolio-only initial...", flush=True)
    pass1 = call_engine(f"{PASS1_PROMPT}{decisions}\n\n{PORTFOLIO_STATE}")
    (RESULTS / "riskchanges_pass1_portfolio_initial.md").write_text(pass1, encoding="utf-8")
    print(f"[pass1] done, {len(pass1)} chars", flush=True)

    print("[pass2] risk-only with authority...", flush=True)
    pass2 = call_engine(f"{PASS2_PROMPT}{decisions}\n\n{PORTFOLIO_STATE}")
    (RESULTS / "riskchanges_pass2_risk_with_authority.md").write_text(pass2, encoding="utf-8")
    print(f"[pass2] done, {len(pass2)} chars", flush=True)

    print("[pass3] portfolio reconsider given pass1+pass2...", flush=True)
    pass3 = call_engine(pass3_prompt(pass1, pass2))
    (RESULTS / "riskchanges_pass3_portfolio_reconsider.md").write_text(pass3, encoding="utf-8")
    print(f"[pass3] done, {len(pass3)} chars", flush=True)


if __name__ == "__main__":
    main()

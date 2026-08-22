"""Risk / Portfolio Boundary Dogfooding — 격리된 Prototype.

`hqs/investment/`는 수정하지 않는다. 새로운 시장 데이터를 만들지
않는다 — Portfolio State는 이전 두 Dogfooding 문서(Portfolio Need,
ETF Look-through)에서 이미 쓴 값을 재사용한다. 이번 실험의 핵심은
Portfolio 질문과 Risk 질문을 **의도적으로 분리된 프롬프트**로 던져,
같은 입력에서 실제로 다른 판단이 나오는지 관찰하는 것이다 — 한쪽
프롬프트가 다른 쪽의 언어(Risk 프롬프트에 "매수/매도" 언급, Portfolio
프롬프트에 "위험" 언급)를 유도하지 않도록 명시적으로 금지한다.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "hqs" / "development" / "mvp"))
from engine import call_engine  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"

# Case C 포트폴리오 상태 재사용(ETF Look-through Dogfooding과 동일 값,
# 신규 생성 아님) — Direct AAPL/NVDA + ETF QQQ(내부에 AAPL/NVDA 포함).
PORTFOLIO_TECH = """[PORTFOLIO STATE — hypothetical, reused verbatim from prior Dogfooding]
Direct Holding: AAPL, 10% of portfolio value. Trader Decision: HOLD (see below).
Direct Holding: NVDA, 10% of portfolio value. Trader Decision: HOLD (see below).
ETF Holding: QQQ, 10% of portfolio value. Trader Decision: HOLD (see below).
  QQQ's own disclosed composition (existing real ETF Team analysis):
  - AAPL: ~7.1-7.3% of QQQ's assets
  - NVDA: ~8.5-8.9% of QQQ's assets
  - Top-5 holdings combined: ~30-33% of QQQ's assets
No stated portfolio policy on position limits or look-through exposure caps.
"""

# Negative control: 단일, 소규모, 무관련 포지션(이전 Portfolio Need Dogfooding에서 사용한 CAT 값 재사용)
PORTFOLIO_SINGLE = """[PORTFOLIO STATE — hypothetical, reused verbatim from prior Dogfooding]
Direct Holding: CAT, 2% of portfolio value. Trader Decision: HOLD (see below).
No other industrial/machinery holdings, no overlapping ETF exposure to CAT above 0.1%.
Stated policy: max 5% of portfolio value per single position (configured, explicit).
"""

# Cross-Team, non-ETF: 두 Dividend Stock 포지션(이전 Portfolio Need Dogfooding에서 상관관계 발견된 조합)
PORTFOLIO_DIVIDEND = """[PORTFOLIO STATE — hypothetical, reused verbatim from prior Dogfooding]
Direct Holding: PG, 10% of portfolio value. Trader Decision: HOLD (see below).
Direct Holding: JNJ, 8% of portfolio value. Trader Decision: HOLD (see below).
No stated portfolio policy on position limits or look-through exposure caps.
"""


def decisions_block(*cases: str) -> str:
    parts = []
    for c in cases:
        text = (RESULTS / f"{c}_trader_expanded.md").read_text(encoding="utf-8")
        idx = text.index("## DECISION")
        parts.append(f"[TRADER DECISION — {c.upper()}]\n{text[idx:].strip()}")
    return "\n\n".join(parts)


PORTFOLIO_ONLY_PROMPT = (
    "PORTFOLIO-ONLY:You are answering strictly a Portfolio composition "
    "question: 'Given this portfolio state and these independent "
    "per-security Trader Decisions, how should this portfolio be composed "
    "or adjusted going forward?' Answer only in terms of what to hold, "
    "trim, add to, or leave unchanged, and why, grounded only in the "
    "Decisions and portfolio state given. Do NOT use risk-assessment "
    "language (do not say whether something is 'risky', 'dangerous', "
    "'volatile', or evaluate whether a risk level is 'acceptable') — if "
    "you find yourself needing to say something is risky to justify a "
    "composition change, say instead exactly what fact you are relying on "
    "(e.g. 'X and Y overlap in the same underlying') without labeling it "
    "as a risk judgment. Do not invent facts beyond what is given.\n\n"
)

RISK_ONLY_PROMPT = (
    "RISK-ONLY:You are answering strictly a Risk assessment question: "
    "'Given this portfolio state, what risk(s) exist in the current "
    "composition, and is that risk level acceptable?' Do NOT recommend "
    "what to buy, sell, hold, trim, or add — do not make any composition "
    "or allocation decision. Only describe what risk(s) exist (e.g. "
    "concentration, correlation, uncertainty) and whether, in your "
    "judgment, the described risk level is tolerable or not, and why. If "
    "you find yourself wanting to say what action should be taken, stop "
    "and instead just describe the risk itself. Do not invent facts "
    "beyond what is given.\n\n"
)

STEP3_PROMPT = (
    "PORTFOLIO-THEN-RISK-SEQUENCE:Answer the following three questions in "
    "order, as three clearly separated sections with these exact headers. "
    "Do not skip ahead — answer STEP3-A using only portfolio-composition "
    "reasoning (no risk language), then STEP3-B using only risk-assessment "
    "reasoning given STEP3-A's answer (no new composition recommendation), "
    "then STEP3-C by explicitly comparing STEP3-A and STEP3-B: does the "
    "risk assessment in STEP3-B change, refine, or leave unchanged the "
    "portfolio composition conclusion from STEP3-A? Be concrete about "
    "whether the actual conclusion differs, not just whether new words "
    "were used. Do not invent facts beyond what is given.\n\n"
    "## STEP3-A (Portfolio composition, no risk language)\n"
    "## STEP3-B (Risk assessment only, no composition recommendation)\n"
    "## STEP3-C (Does STEP3-B change STEP3-A's conclusion? Concretely, "
    "yes/no and why)\n\n"
)


def run(name: str, prompt_body: str, portfolio: str, decisions: str) -> None:
    prompt = f"{prompt_body}{decisions}\n\n{portfolio}"
    result = call_engine(prompt)
    (RESULTS / f"riskboundary_{name}.md").write_text(result, encoding="utf-8")
    print(f"[{name}] done, {len(result)} chars", flush=True)


def main():
    RESULTS.mkdir(exist_ok=True)

    tech_decisions = decisions_block("aapl", "nvda", "qqq")
    single_decision = decisions_block("cat")
    dividend_decisions = decisions_block("pg", "jnj")

    run("step1_portfolio_only_tech", PORTFOLIO_ONLY_PROMPT, PORTFOLIO_TECH, tech_decisions)
    run("step2_risk_only_tech", RISK_ONLY_PROMPT, PORTFOLIO_TECH, tech_decisions)
    run("step3_sequence_tech", STEP3_PROMPT, PORTFOLIO_TECH, tech_decisions)

    run("negctrl_portfolio_only_single", PORTFOLIO_ONLY_PROMPT, PORTFOLIO_SINGLE, single_decision)
    run("negctrl_risk_only_single", RISK_ONLY_PROMPT, PORTFOLIO_SINGLE, single_decision)

    run("crossteam_risk_only_dividend", RISK_ONLY_PROMPT, PORTFOLIO_DIVIDEND, dividend_decisions)


if __name__ == "__main__":
    main()

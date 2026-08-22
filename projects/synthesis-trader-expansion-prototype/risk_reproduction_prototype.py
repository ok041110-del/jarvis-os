"""Risk -> Portfolio Decision Change Reproduction Dogfooding — 격리된 Prototype.

동일한 3-Pass 구조(PASS1 Portfolio-only / PASS2 Risk-only / PASS3
Risk-informed Portfolio)를 QQQ 사례(이전 실험, 재실행하지 않음)와는
다른 두 개의 독립 사례에 적용한다:

- Case 2(신규): PG+JNJ(Dividend Stock, ETF 없음) — "방어적 배당 슬리브"
  섹터/팩터 결합 노출 정책. 이전 QQQ 사례(ETF look-through)와는 다른
  종류의 Portfolio-level 제약(§4 "다른 Concentration policy").
- Case 3(신규, Negative Control): CAT 단독 — 명시적 정책 존재, 위반
  없음, 의미 있는 구조적 위험 없음(§11).

`hqs/investment/`는 수정하지 않는다. Exposure는 절대 일반 합산하지
않는다 — 정책 확인 목적의 계산만 "Policy Evaluation Calculation"으로
명시적으로 라벨링한다(§6).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "hqs" / "development" / "mvp"))
from engine import call_engine  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"

NO_SUM_RULE = (
    "STRICT RULE: Never merge different Exposure Paths into a single "
    "general-purpose number (e.g. do NOT silently compute 'Direct 10% + "
    "Indirect 0.71% = 10.71% total exposure' as if that were itself a new "
    "exposure figure). If, and only if, a stated policy explicitly "
    "requires checking a combined figure against a threshold, you may "
    "compute that ONE combined number, but you must label it explicitly "
    "as a 'Policy Evaluation Calculation' (not a new stored exposure "
    "value), separate from the list of independent Exposure Paths."
)


def decisions_block(*cases: str) -> str:
    parts = []
    for c in cases:
        text = (RESULTS / f"{c}_trader_expanded.md").read_text(encoding="utf-8")
        idx = text.index("## DECISION")
        parts.append(f"[TRADER DECISION — {c.upper()}]\n{text[idx:].strip()}")
    return "\n\n".join(parts)


PASS1_PROMPT = (
    "PASS1-PORTFOLIO-ONLY:Answer strictly a Portfolio composition "
    "question, using ONLY the portfolio state and Trader Decisions below: "
    "how should this portfolio be composed, maintained, or adjusted? Do "
    "not run any policy-compliance calculation yourself unless it is "
    "trivially obvious without combining figures across positions — this "
    "pass is ordinary composition reasoning, not risk/compliance "
    "analysis. " + NO_SUM_RULE + " Do not invent facts beyond what is "
    "given.\n\n"
)

PASS2_PROMPT = (
    "PASS2-RISK-ONLY:You are the Risk reviewer. Using the same portfolio "
    "state (do not assume anything not given), answer: what structurally "
    "important risk(s) exist in this composition, and is that risk level "
    "acceptable? If a stated policy is violated, say explicitly (a) what "
    "is violated, (b) which Exposure Path(s) are involved, and (c) what "
    "adjustment you judge is needed to address it. If nothing is "
    "violated and no structural risk is significant, say so plainly and "
    "explain why — do not manufacture a finding. " + NO_SUM_RULE + " Do "
    "not invent facts beyond what is given.\n\n"
)


def pass3_prompt(pass1_text: str, pass2_text: str) -> str:
    return (
        "PASS3-RISK-INFORMED-PORTFOLIO:Below are two prior, independent "
        "analyses of the same portfolio. PASS1 is a Portfolio-only "
        "composition conclusion produced with no risk analysis. PASS2 is "
        "an independent Risk assessment. Considering PASS2, does the "
        "original PASS1 Portfolio Decision get kept as-is, modified, or "
        "reversed? Classify your answer as exactly one of: NO CHANGE / "
        "MODIFICATION / REVERSAL, then explain concretely what changed "
        "(or did not) between PASS1's end-state and your final "
        "conclusion. Do not invent facts beyond what is given in PASS1 "
        "or PASS2.\n\n"
        f"[PASS1 — PORTFOLIO-ONLY CONCLUSION]\n{pass1_text}\n\n"
        f"[PASS2 — RISK ASSESSMENT]\n{pass2_text}\n\n"
    )


def run_case(name: str, portfolio_state: str, decisions: str) -> None:
    print(f"[{name}] PASS1...", flush=True)
    pass1 = call_engine(f"{PASS1_PROMPT}{decisions}\n\n{portfolio_state}")
    (RESULTS / f"riskrepro_{name}_pass1.md").write_text(pass1, encoding="utf-8")

    print(f"[{name}] PASS2...", flush=True)
    pass2 = call_engine(f"{PASS2_PROMPT}{decisions}\n\n{portfolio_state}")
    (RESULTS / f"riskrepro_{name}_pass2.md").write_text(pass2, encoding="utf-8")

    print(f"[{name}] PASS3...", flush=True)
    pass3 = call_engine(pass3_prompt(pass1, pass2))
    (RESULTS / f"riskrepro_{name}_pass3.md").write_text(pass3, encoding="utf-8")
    print(f"[{name}] done", flush=True)


# --- Case 2: PG + JNJ, Dividend Stock Cross-Team, ETF 없음, "방어적 배당
# 슬리브 결합 노출" 정책. 실제 Trader Decision(PG/JNJ, 이미 존재하는
# 실제 산출물) 재사용. 슬리브 상한(15%)과 실제 결합 비중(18%)은 정책
# 위반이 발생하도록 이번 실험을 위해 의도적으로 설계(synthetic control,
# §4 명시).
CASE2_PORTFOLIO = """[PORTFOLIO STATE — hypothetical, constructed for this exercise]
Direct Holding: PG, 10% of portfolio value. Trader Decision: HOLD.
Direct Holding: JNJ, 8% of portfolio value. Trader Decision: HOLD.
No ETF holdings in this portfolio (Cross-Team without ETF, per Dividend Stock Team results only).
STATED PORTFOLIO POLICY (explicit, configured for this portfolio):
  "Combined exposure to the 'defensive dividend compounder' sleeve
  (large-cap, multi-decade dividend-growth consumer-staples/healthcare
  names with overlapping investor bases and correlated rate/rotation
  sensitivity) must not exceed 15% of total portfolio value."
"""

# --- Case 3: CAT 단독, Negative Control. 실제 Trader Decision(CAT) +
# 실제 정책(5% 상한, Portfolio Need Dogfooding에서 이미 사용) 재사용 —
# 신규 데이터 생성 없음.
CASE3_PORTFOLIO = """[PORTFOLIO STATE — hypothetical, reused verbatim from prior Dogfooding]
Direct Holding: CAT, 2% of portfolio value. Trader Decision: HOLD.
No other industrial/machinery holdings, no overlapping ETF exposure to CAT above 0.1%.
STATED PORTFOLIO POLICY (explicit, configured for this portfolio):
  "No single position may exceed 5% of total portfolio value."
"""


def main():
    RESULTS.mkdir(exist_ok=True)
    run_case("case2_dividend_sleeve", CASE2_PORTFOLIO, decisions_block("pg", "jnj"))
    run_case("case3_negctrl_cat", CASE3_PORTFOLIO, decisions_block("cat"))


if __name__ == "__main__":
    main()

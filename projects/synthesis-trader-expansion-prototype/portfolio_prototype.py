"""Portfolio Need Dogfooding — STEP1/2/3 실험 스크립트.

격리된 Prototype 디렉토리. `hqs/investment/`는 수정하지 않는다(무수정
확인은 evidence 문서에 기록). 새로운 시장 데이터(raw_data)는 만들지
않는다 — 이 스크립트가 다루는 것은 실제 Trader Decision(기존
`results/*_trader_expanded.md`, 이미 실제 Engine 호출로 생성된 것)과
Portfolio State(계좌 구성 — 시장 데이터가 아니라 "얼마나 들고
있는가"라는 설정값)뿐이다. Portfolio State는 이 실험을 위해 명시적으로
가상(hypothetical)이라고 표시한다 — 실제 계좌 데이터가 아니다.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "hqs" / "development" / "mvp"))
from engine import call_engine  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"

HYPOTHETICAL_PORTFOLIO_STATE = """\
[HYPOTHETICAL PORTFOLIO STATE — for this architecture exercise only, not real account data]
Total investable capital: $100,000 (illustrative figure)
Current holdings (illustrative):
- AAPL: 500 shares, ~15% of portfolio value
- NVDA: 300 shares, ~12% of portfolio value
- QQQ: 200 shares, ~18% of portfolio value
- PG: cash-equivalent dividend sleeve, ~10% of portfolio value
- JNJ: cash-equivalent dividend sleeve, ~8% of portfolio value
- Cash: ~7%
- Remaining ~30% in unrelated, unspecified holdings
No stated policy limits (e.g. no "max 10% per position" rule has been configured).
"""

EXTRACTION_NOTE = (
    "Each Decision below was produced independently, per-security, with no "
    "portfolio context — this is stated explicitly inside each Decision's "
    "own rationale."
)


def load_decision(case: str) -> str:
    text = (RESULTS / f"{case}_trader_expanded.md").read_text(encoding="utf-8")
    # DECISION 섹션만 추출 (REPORT는 이 실험의 입력이 아님 — Trader가
    # 이미 종합한 최종 판단만 Portfolio 판단의 입력으로 쓴다).
    idx = text.index("## DECISION")
    return text[idx:].strip()


def step2_single_asset(case: str) -> str:
    decision = load_decision(case)
    prompt = (
        "PORTFOLIO-STEP2:You are given one security's Trader Decision "
        "(direction, rationale, reassess condition) and a hypothetical "
        "portfolio state. Answer plainly: given the portfolio state, is "
        "there any position-size or allocation judgment to make here, and "
        "if so, is it (a) a simple calculation (e.g. capital x fixed "
        "percentage), (b) applying a stated policy, or (c) a new judgment "
        "that a fixed calculation or policy could not have produced on its "
        "own? Explain in 3-5 sentences. Do not invent any new facts about "
        "the security itself beyond what the Decision states.\n\n"
        f"[TRADER DECISION — {case.upper()}]\n{decision}\n\n"
        f"{HYPOTHETICAL_PORTFOLIO_STATE}"
    )
    return call_engine(prompt)


def step3_multi_asset(cases: list[str]) -> str:
    decisions = "\n\n".join(f"[TRADER DECISION — {c.upper()}]\n{load_decision(c)}" for c in cases)
    prompt = (
        "PORTFOLIO-STEP3:You are given several securities' independent "
        "Trader Decisions (each produced in isolation, per-security, with "
        "no knowledge of each other or of any portfolio) and a hypothetical "
        "portfolio state. "
        + EXTRACTION_NOTE + " "
        "Answer plainly: after reading all of these together with the "
        "portfolio state, is there any judgment that needs to be made at "
        "the portfolio level that none of the individual per-security "
        "Decisions could have made on its own — even though every "
        "individual Decision here happens to be HOLD? If yes, describe "
        "exactly what that judgment is and why no individual Decision "
        "could have produced it. If no such judgment is needed beyond "
        "leaving each position unchanged, say so plainly and explain why. "
        "Do not invent any new facts about any security beyond what is "
        "stated in the Decisions below or the portfolio state. Do not "
        "decide position sizes or capital allocation — only describe "
        "whether such a judgment is needed and of what kind (simple "
        "calculation vs. policy application vs. a genuinely new synthesis "
        "of multiple assets).\n\n"
        f"{decisions}\n\n{HYPOTHETICAL_PORTFOLIO_STATE}"
    )
    return call_engine(prompt)


def main():
    RESULTS.mkdir(exist_ok=True)
    print("[step2] single-asset (AAPL) + portfolio state...", flush=True)
    (RESULTS / "portfolio_step2_aapl.md").write_text(step2_single_asset("aapl"), encoding="utf-8")
    print("[step3] multi-asset (AAPL+NVDA+QQQ, tech/AI overlap) + portfolio state...", flush=True)
    (RESULTS / "portfolio_step3_tech_overlap.md").write_text(
        step3_multi_asset(["aapl", "nvda", "qqq"]), encoding="utf-8"
    )
    print("[step3b] multi-asset (PG+JNJ, dividend sleeve, no overlap) + portfolio state...", flush=True)
    (RESULTS / "portfolio_step3_dividend_sleeve.md").write_text(
        step3_multi_asset(["pg", "jnj"]), encoding="utf-8"
    )
    print("done", flush=True)


if __name__ == "__main__":
    main()

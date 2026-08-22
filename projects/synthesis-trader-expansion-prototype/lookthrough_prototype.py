"""ETF Look-through Exposure Dogfooding — 격리된 Prototype.

`hqs/investment/`는 수정하지 않는다. 새로운 시장 데이터를 만들지
않는다 — 여기서 쓰는 ETF 구성종목 비중은 전부 기존 실제
`bull_case.md`/`holdings_exposure_analysis.md` 등에 이미 존재하던
수치를 그대로 인용한다. Portfolio State(직접 보유 여부)만 이 실험을
위한 가상 설정값이다.

핵심 규칙(사용자 지시 준수): 서로 다른 Exposure Path를 하나의 숫자로
합산하지 않는다 — 프롬프트 자체가 합산을 명시적으로 금지한다.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "hqs" / "development" / "mvp"))
from engine import call_engine  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"

NO_SUM_RULE = (
    "STRICT RULE: Never merge different Exposure Paths into a single "
    "combined number (e.g. do NOT compute 'Direct 10% + Indirect 0.8% = "
    "10.8% total'). Each Exposure Path (Direct Holding, ETF->Constituent "
    "Indirect Holding) must be reported as an independent, separate line — "
    "never summed, never converted into one score. Do not invent any "
    "holding percentages beyond what is given below."
)


def run(name: str, portfolio_state: str, question: str) -> str:
    prompt = (
        f"LOOKTHROUGH-EXPOSURE:{NO_SUM_RULE}\n\n{portfolio_state}\n\n{question}"
    )
    result = call_engine(prompt)
    (RESULTS / f"lookthrough_{name}.md").write_text(result, encoding="utf-8")
    print(f"[{name}] done, {len(result)} chars", flush=True)
    return result


QUESTION = (
    "Given only the portfolio state above (no other facts), answer: (1) "
    "List every distinct Exposure Path to each underlying security "
    "mentioned, as separate independent lines (never summed). (2) Is there "
    "any Portfolio-level judgment needed here beyond simply listing these "
    "Exposure Paths as data (a 'Data Join')? If yes, describe what new "
    "judgment is needed and why listing the paths alone would not be "
    "enough. If no, say plainly that this is a Data Join case with no "
    "further judgment needed, and explain why."
)


def main():
    RESULTS.mkdir(exist_ok=True)

    # Case C — Direct AAPL + Direct NVDA + QQQ(holds AAPL~7.1-7.3%, NVDA~8.5-8.9%, top-5~30-33%)
    # 수치 출처: projects/etf-analysis-qqq/issues/0001-qqq-analysis/bull_case.md (기존 실제 산출물)
    run(
        "case_c_qqq_overlap",
        """[PORTFOLIO STATE — hypothetical, for this exercise only]
Direct Holding: AAPL, 10% of portfolio value.
Direct Holding: NVDA, 10% of portfolio value.
ETF Holding: QQQ, 10% of portfolio value.
  QQQ's own disclosed composition (from existing real ETF Team analysis, not invented here):
  - AAPL: ~7.1-7.3% of QQQ's assets
  - NVDA: ~8.5-8.9% of QQQ's assets
  - Top-5 holdings combined: ~30-33% of QQQ's assets
No stated portfolio policy on position limits or look-through exposure caps.""",
        QUESTION,
    )

    # Case B — QQQ만 보유, AAPL/NVDA 직접 보유 없음
    run(
        "case_b_qqq_only",
        """[PORTFOLIO STATE — hypothetical, for this exercise only]
ETF Holding: QQQ, 10% of portfolio value.
  QQQ's own disclosed composition (from existing real ETF Team analysis, not invented here):
  - AAPL: ~7.1-7.3% of QQQ's assets
  - NVDA: ~8.5-8.9% of QQQ's assets
  - Top-5 holdings combined: ~30-33% of QQQ's assets
No direct holding of AAPL, NVDA, or any other individual security exists in this portfolio.
No stated portfolio policy on position limits or look-through exposure caps.""",
        QUESTION,
    )

    # Case A — Non-equity ETF(GLD, 실물 금 100%), 구조적으로 look-through 대상 자체가 없음
    run(
        "case_a_gld_no_lookthrough",
        """[PORTFOLIO STATE — hypothetical, for this exercise only]
ETF Holding: GLD, 10% of portfolio value.
  GLD's own disclosed composition (from existing real ETF Team analysis, not invented here):
  - 100% allocated to physical gold bullion held in a grantor trust.
  - No derivatives, no futures, no bonds, no equities of any kind.
No direct holding of any individual stock exists in this portfolio.
No stated portfolio policy on position limits or look-through exposure caps.""",
        QUESTION,
    )

    # 추가 다양성 — SCHD(Sector/Dividend Thematic ETF), 구성종목은 실제로 존재하나
    # 이 Portfolio의 다른 직접 보유 종목과 겹치지 않음(Case B 변형)
    run(
        "case_b2_schd_no_overlap",
        """[PORTFOLIO STATE — hypothetical, for this exercise only]
Direct Holding: JNJ, 8% of portfolio value.
ETF Holding: SCHD, 10% of portfolio value.
  SCHD's own disclosed composition (from existing real ETF Team analysis, not invented here):
  - 103 total holdings, largest single position 4.42%.
  - Top holdings after March 2026 reconstitution: Abbott Laboratories, UnitedHealth,
    and Merck (healthcare-weighted); JNJ is not named among SCHD's confirmed top holdings
    in the available data.
No stated portfolio policy on position limits or look-through exposure caps.""",
        QUESTION,
    )


if __name__ == "__main__":
    main()

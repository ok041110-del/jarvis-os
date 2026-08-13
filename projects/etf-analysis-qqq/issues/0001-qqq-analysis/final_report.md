# QQQ Research Report — Invesco QQQ Trust

*Compiled from a web-search data snapshot as of 2026-08-13. Not live data. All figures are drawn directly from the provided sourced sections; no numbers, dates, or facts have been invented, and gaps or inconsistencies are flagged explicitly rather than filled in.*

---

## 1. Composition

Invesco QQQ Trust, Series 1 tracks the **Nasdaq-100 Index** — the 100 largest non-financial companies listed on Nasdaq, selected and ranked by market capitalization, administered by Nasdaq, Inc.

- **Weighting methodology:** "Modified market-capitalization-weighted." Larger companies generally get proportionally larger weights, but a capping mechanism limits single-name concentration (commonly used to satisfy regulated-fund diversification requirements). The specific numeric weight caps are **not present in the data**.
- **Recent methodology change:** Effective **May 1, 2026**, the index changed how it ranks companies for eligibility/composition — using **total market capitalization (including unlisted shares)** rather than listed shares alone. The actual **weight calculation** still uses listed shares only; only the ranking/selection step changed. First fully applied at the **June 22, 2026** rebalancing.
- **Implication (as stated in source data):** This could, in principle, change which companies qualify or how they rank (e.g., companies with large unlisted/closely-held share counts would rank on a larger cap figure). The data does **not** specify which constituents were actually added, removed, or reranked as a result.
- **Rebalancing cadence:** Quarterly weight rebalancing; annual full reconstitution.

**Data limitations:** No numeric weight-cap thresholds provided; no holdings/sector percentages included in this section's source; no tracking error or volatility metrics; not cross-verified against Invesco's official fact sheet or SEC filings.

---

## 2. Holdings

QQQ shows meaningful single-name and top-heavy concentration, with magnitude varying by source.

- **Largest holding (NVIDIA):** 8.46% (Source A), ~8.7% (Source B), 8.9% (Source C).
- **Second largest (Apple):** 7.32% (A), ~7.1% (B), 7.2% (C) — these three are tightly consistent.
- **Top-5 concentration:** Source A: NVIDIA + Apple + Alphabet + Microsoft + Amazon.com = 8.46 + 7.32 + 6.44 + 5.93 + 4.68 = **32.83%**. Source B gives a similar but not identical list (omits Alphabet from the names shown) and states top-5 ≈ **30%** — a figure that doesn't fully reconcile since only four names are specified.
- **Top-10 concentration:** Source C states **47.3%** combined — a different lens/date than the top-5 figures, not cross-checkable holding-by-holding against A or B. Bridging Source A's top-5 (~32.8%) and Source C's top-10 (47.3%) would imply ranks 6–10 contribute ~14.5 points, but this is an inference across different sources/times, not a stated figure.

**Inconsistencies flagged:**
- Same-holding weights differ across sources (e.g., Microsoft 5.93% vs ~5.3% vs 5.0%), attributed to differing collection timestamps.
- Source B's top-5 list and its ~30% aggregate are not fully reconcilable (only four names given).
- No source provides a complete, consistent top-10 list with individual weights.
- The source data notes rebalancing/price movement mean these figures "may differ somewhat" from a precise mid-August 2026 snapshot.

**Bottom line:** Concentration is meaningful (largest holding ~8–9%, top-5 roughly 30–33%, top-10 near 47%), but precise, reconciled figures as of one date cannot be pinned down from this data.

---

## 3. Cost

- **Expense ratio: 0.18%**, confirmed as of the fund's **December 22, 2025** conversion from a Unit Investment Trust (UIT) structure to a standard open-end ETF. No pre-conversion comparison data provided. In dollar terms: $18/year per $10,000 invested; $180/year per $100,000.
- Described qualitatively as "low" for large index-tracking ETFs, but the data contains **no direct comparison figures** against category peers (e.g., competing Nasdaq-100 or S&P 500 ETFs), so a relative "low vs. high" judgment cannot be made from this data alone.
- **Tracking error:** **No specific figure is provided.** The only related content is a qualitative statement that high-liquidity ETFs like QQQ/VOO have very tight spreads that "generally support tight tracking" — this is not an actual tracking-error statistic, and tight spreads do not by themselves guarantee low tracking error. The source itself notes that confirming actual tracking error would require Invesco's official documentation or a separate data provider.

**Data limitations:** Not cross-verified against Invesco's official fact sheet or SEC filings; no quantitative tracking-error or volatility (std. dev., beta) figures; sources are investsnips.com, Invesco's official page, and seekingalpha.com (2026).

---

## 4. Performance

- **YTD returns (two non-reconcilable figures):** +18.11% (dividend-reinvested, as of **Aug 4, 2026**) vs. +20.19% (NAV basis, as of **June 30, 2026**). Different dates, different return bases — not restatements of the same quantity.
- **1-year (dividend-reinvested):** +28.94%.
- **Longer horizons:** 26.55% (3-year), 16.45% (5-year), 22.07% (10-year). **Whether these are annualized or cumulative is not specified in the source material** — a material gap that prevents any conclusion about compounded annual growth rate.
- **Q2 2026:** QQQ +27.54% (NAV) vs. S&P 500 total return +15.20% — roughly 12.3 percentage points of outperformance in the quarter, per the two reported figures.
- **Volatility:** No quantitative metrics (standard deviation, beta, Sharpe ratio, max drawdown) are present anywhere in the data. The only content is a qualitative characterization of "characteristically high volatility and concentration risk associated with the Nasdaq-100." This cannot substitute for a quantitative figure.

**Data limitations:** No tracking error data; two YTD figures on different dates/bases, unreconciled; annualization status of 3-/5-/10-year figures unstated; holdings/sector figures reported inconsistently elsewhere; snapshot as of Aug 13, 2026, not cross-verified against official filings.

---

## 5. Exposure

- **Sector concentration (Technology):** Three sources disagree materially — **57.8%** (Source A), **64.75%** (Source B, described as a 2026 Q2 average), **66.9%** (Source C). A ~9-point spread, large enough to shift the picture from "majority tech" to "supermajority tech." Cause of the discrepancy (measurement date, sector-classification methodology, or both) is **not confirmed** in the source material.
- **Rest of portfolio (Source C only):** After Technology (66.9%), Consumer Discretionary is next at 17.6%; every other sector is under 4%. Not cross-checkable against Sources A/B, which lack a full breakdown.
- **Vs. S&P 500:** Source B states QQQ's Technology weight (64.75%) is well above the S&P 500's (43.28%) for the same period — this comparison exists only in Source B.
- **Performance linkage:** Q2 2026 Technology-sector return within QQQ was 45.14%, vs. 29.07% within the S&P 500. No attribution analysis (isolating weighting effect from stock-selection effect) is provided — this is a directional observation only.
- **Geographic exposure:** **No data provided at all.** The Nasdaq-100's U.S.-listing basis would suggest U.S.-centric composition, but no country/region weightings or revenue-geography data exist in the source material — this is a data gap, not a supportable inference.

**Data limitations:** Sector figures from Fool.com, tradingsim.com, and an Invesco quarterly highlights reference, not cross-checked against an official fact sheet; the three Technology-weight figures conflict with no stated cause; no geographic data; no tracking error; no quantitative volatility metrics.

---

## 6. Distribution

- **Yield:** 0.42% dividend yield; **$3.03** trailing-twelve-month distributions per share — low in absolute terms, consistent with a growth/reinvestment-tilted, tech-heavy holding profile.
- **Frequency:** Quarterly. One specific instance provided: **Q2 2026 distribution of $0.813496/share**, ex-dividend date **2026-06-22**, payment date **2026-07-10**. Next ex-dividend date: **2026-09-21**, marked as expected/scheduled, not confirmed.
- **Trend:** **Cannot be characterized.** Only one individual quarterly amount is provided alongside the TTM aggregate ($3.03); without the other three quarters, no determination of rising/falling/flat distributions, or year-over-year yield comparison, is possible from this data.

**Data limitations:** Sourced from stockanalysis.com, wallstreethorizon.com, macrotrends.net, not verified against Invesco's official fact sheet or SEC filings; only a single quarter's amount provided; next ex-dividend date unconfirmed.

---

## 7. Macro

- **Rate policy backdrop:** On **June 17, 2026**, the FOMC held rates at **3.50–3.75%**, but committee sentiment skewed hawkish: **9 of 18** members projected additional hikes this year, and the median 2026 year-end dot plot rose from 3.4% (March) to **3.8%**. No data is provided on any FOMC meetings or policy developments between June and the August 13 snapshot date.
- **Three-scenario framework (reported estimates, not official Fed/Invesco figures):**
  - **Base Case (50%):** AI capex remains resilient, offsetting rate headwinds, but hawkish Fed signals cap the upside — Nasdaq-100 range-bound at **29,000–33,000**.
  - **Bull Case (25%):** Summer inflation data cools enough to remove further-hike risk; AI earnings surprises continue → Nasdaq-100 breaks 31,000, potentially extending above **35,000**.
  - **Bear Case (25%):** Fed actually hikes further; energy-driven inflation proves sticky → long-duration growth valuations compress, Nasdaq-100 retreats to **23,000–27,000**.
  - The two variables spanning all three scenarios are: (1) monetary policy path/inflation trajectory, and (2) AI-related earnings/capex momentum.
- **Current price context:** As of **Aug 11, 2026**, QQQ traded at **$720.87**, described qualitatively as in a "technically strong uptrend, trading above key support levels." **No conversion is provided between this ETF price and the Nasdaq-100 index scenario bands (23,000–35,000+)**, so it cannot be determined from this data which scenario path the current price is tracking toward.

**Data limitations:** Scenario probabilities are media/reporting estimates, not official; no data on FOMC or market developments after June 2026 (aside from the Aug 11 price point); no tracking error or quantitative volatility data; snapshot as of Aug 13, 2026 only.

---

## 8. Bull Case

1. **Demonstrated outperformance:** Across every measured window — YTD (+18.11% or +20.19% depending on basis/date), 1-year (+28.94%), and especially Q2 2026 (+27.54% NAV vs. S&P 500's +15.20%, ~12.3-point edge) — driven by QQQ's Technology sleeve returning 45.14% vs. 29.07% for the S&P 500's Technology sleeve in the same quarter.
2. **Low, recently-confirmed cost:** 0.18% expense ratio (confirmed at the Dec 22, 2025 UIT-to-ETF conversion), paired with qualitative "high liquidity/tight spreads" commentary.
3. **Disciplined index construction:** Capped modified-market-cap weighting with quarterly rebalancing and annual reconstitution provides systematic (not discretionary) diversification discipline; the June 2026 ranking-methodology change (total market cap including unlisted shares) can be read as the index evolving to capture true company scale.
4. **Ownership of AI-cycle leaders:** NVIDIA (~8.5–8.9%) and Apple (~7.1–7.3%) anchor a top-5 (~30–33%) and top-10 (~47.3%, one source) that provide dense, liquid exposure to the mega-caps most levered to AI infrastructure and platform-scale earnings.
5. **A specific favorable macro path exists in the data itself:** The Bull scenario (25%, media estimate) — cooling inflation removing hike risk plus continued AI earnings strength — pushing the Nasdaq-100 through 31,000 toward 35,000+, consistent with QQQ's Aug 11, 2026 "technically strong uptrend" description.
6. **Dependable distribution cadence:** Confirmed Q2 2026 payment ($0.813496/share) and a scheduled next ex-dividend date (Sept 21, 2026), even though yield is low (0.42%).

**Caveats the bull case must carry:** The two YTD figures aren't reconciled; annualization status of the 3-/5-/10-year returns is unknown; no risk-adjusted metrics exist to support a "good risk/reward" claim; sector and holdings concentration figures vary by source; the 25% bull-scenario probability is a media estimate with no stated basis for whether it is already priced into the current $720.87 level; no geographic exposure data exists to support any diversification claim.

---

## 9. Bear Case

1. **Extreme, compounding concentration:** NVIDIA (~8.5–8.9%) + Apple (~7.1–7.3%) alone approach 1/6 of the fund; top-5 ~30–33%; top-10 (one source) 47.3% — roughly half the fund riding on ten names.
2. **Severe, disputed sector concentration:** Technology at 57.8–66.9% (a 9-point unresolved spread) vs. the S&P 500's 43.28% — even the low end is 20+ points above the broad-market benchmark, with only Consumer Discretionary (17.6%, one source) as a secondary sector of scale and everything else under 4%.
3. **Direct vulnerability to the macro bear scenario:** With 9 of 18 FOMC members projecting further hikes (median dot up to 3.8%) as of June 2026, the data's own bear scenario (Fed hikes further, sticky energy inflation → valuation compression → Nasdaq-100 to 23,000–27,000) targets exactly this concentrated, high-multiple growth basket with no offsetting value/financial/defensive ballast. The bull path requires two favorable developments (inflation cooperates AND AI earnings continue); the bear path requires only that the Fed follow through on what nearly half the FOMC already signaled.
4. **No income cushion:** 0.42% yield / $3.03 TTM offers little offset if price appreciation stalls or reverses, particularly under the base case ("sideways, 29,000–33,000") or worse.
5. **Recent, opaque methodology and structural change:** The UIT-to-ETF conversion (Dec 22, 2025) and the index ranking-methodology change (May 1/June 22, 2026, total market cap including unlisted shares) both landed close together, and the data cannot specify what the ranking change actually did to constituents — a governance/composition uncertainty layered on a recent structural transition.
6. **No verifiable risk metrics exist anywhere in the data:** No tracking error, standard deviation, beta, Sharpe ratio, or max drawdown for QQQ. Headline outperformance (e.g., Q2 2026's +27.54% vs. +15.20%) cannot be assessed on a risk-adjusted basis — it may simply reflect higher beta-like sensitivity to a concentrated, rallying theme.
7. **Internally inconsistent return figures:** Two different YTD numbers on different bases/dates, and unknown annualization status for the multi-year figures, mean the "strong performance" narrative rests on figures the data itself does not reconcile.

**Caveats the bear case must carry:** None of the concentration figures are precisely pinned down (source variance in both holdings and sector weights); the bear macro scenario's 25% probability is a media estimate, not official; there is no tracking-error data, so no claim can be made that QQQ fails to track its index — only that the index itself is concentrated; all volatility claims are qualitative, not statistical.

---

## 10. Synthesis

**Where the two cases agree (facts, not interpretation):** Both draw on the identical dataset and do not dispute any raw figure. They agree on: the return figures (including both YTD numbers and their basis/date mismatch); holdings weights (NVIDIA ~8.5–8.9%, Apple ~7.1–7.3%, top-5 ~30–33%, top-10 47.3% per one source); the sector-weight range (57.8/64.75/66.9% vs. S&P 500's 43.28%); the 0.18% expense ratio and Dec 22, 2025 conversion date; the 0.42% yield / $3.03 TTM; the three-scenario macro framework and its probabilities (flagged by both as media estimates, not official); the June 2026 FOMC split (9/18, dot plot to 3.8%); the June 2026 index methodology change; and the complete absence of quantitative risk metrics (std. dev., beta, Sharpe, max drawdown, tracking error) anywhere in the source data. **There is no factual dispute between the two cases** — every number either matches or is flagged by both sides as internally inconsistent in the same way.

**Where they diverge:** Purely in interpretation of identical facts. Concentration (single-name, top-5/10, and sector) is read by the bull as dense, liquid exposure to AI-cycle leaders that has produced repeated, measurable outperformance; the bear reads the same concentration as a structural vulnerability with no offsetting ballast, particularly against the data's own bear macro scenario. The June 2026 methodology change is read as "capturing true scale" by the bull and as "opaque, unresolved effect on holdings" by the bear. Q2 2026 outperformance is read as evidence of edge by the bull and as unquantifiable, possibly just higher beta, by the bear absent risk-adjusted data.

**Open questions that would most change the conclusion (per the data's own gaps):**
1. Risk-adjusted performance data (beta, Sharpe, max drawdown, tracking error) — the single largest gap; without it, "strong returns" cannot be separated from "returns that look strong during a concentrated basket's up-cycle."
2. Where the current Nasdaq-100 level actually sits relative to the Base/Bull/Bear index-point bands — the data gives QQQ's price ($720.87, Aug 11, 2026) and a qualitative "uptrend" description but no translation to index-level positioning.
3. What the June 2026 index methodology change concretely did to constituents (additions/removals/reweighting) — unstated in the data.
4. Reconciliation of the sector-weight range (57.8–66.9%) and the holdings-weight range across sources — a 9-point spread on a load-bearing fact for both cases.
5. Whether the Fed has acted on, or moved away from, the hawkish June 2026 dot-plot signal since that meeting — no post-June FOMC data is provided.

**Bottom line on the data itself:** The bull and bear cases apply opposite risk framings to one shared, internally-imperfect dataset — they are not describing two different funds. Given the stated gaps (no risk-adjusted metrics, unreconciled sector/holdings figures, no scenario-relative price positioning, an unresolved recent methodology change, and a non-authoritative bull-scenario probability), **the data as provided is insufficient to adjudicate between the two cases.** It supports both the "structural tilt has produced real outperformance" and "structural tilt is unpriced concentration risk" readings equally well; resolving it would require exactly the risk and reconciliation data that neither case has.

---

## Disclaimer

This document is an **analysis exercise** built strictly from a specific, dated web-search data snapshot (as of 2026-08-13) provided for this exercise. It has not been cross-verified against Invesco's official fact sheet, SEC filings, or any live/real-time market data, and it does not reflect any developments after that date. Multiple figures within the underlying data are inconsistent, unreconciled, or incomplete (as flagged throughout), and no quantitative risk metrics (tracking error, standard deviation, beta, Sharpe ratio, or maximum drawdown) were available for any section. **This report is not investment advice, financial advice, or a trade recommendation, and should not be relied upon as the basis for any investment decision.** Consult a qualified financial professional and primary-source, up-to-date data before making any investment decision.

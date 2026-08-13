# AGG (iShares Core U.S. Aggregate Bond ETF) — Research Report

*Compiled from web-search data collected as of 2026-08-13 (underlying iShares Fact Sheet figures dated 2026-06-30). This report integrates six analytical sections into one document. It does not invent any figures, dates, or facts beyond what was supplied, and it flags data gaps and inconsistencies explicitly rather than resolving them.*

---

## 1. Composition

AGG tracks the **Bloomberg U.S. Aggregate Bond Index**, described in the source material as a broad benchmark for the U.S. investment-grade bond market rather than a sector-specific index. The data does not provide the index's own internal sector/duration/credit breakdown, so only the fund's own holdings data (Section 2) can be used to characterize composition.

AGG is managed via a **sampling strategy**, not full replication — a contrast the source data draws explicitly against the full-replication structure of equity ETFs referenced elsewhere (QQQ, SCHD). Sampling is used because the underlying index holds a very large number of bonds (AGG itself holds roughly **13,224 individual securities**), many of which are illiquid or costly to trade; the data explicitly states the sampling approach is designed to avoid lower-liquidity bonds in the index.

The data identifies **tracking error** as the structural consequence of sampling versus full replication — the fund's return may deviate from the index's because it does not hold every constituent. However, **no numeric tracking-error figure for AGG is present anywhere in the source data.** The data also notes that BND and LAG track the same benchmark and are described as having lower expense ratios than AGG in the composition write-up specifically — though no comparative expense figures for BND/LAG are given anywhere, which is an internal tension worth flagging: the Cost/Tracking section (Section 3) states the opposite framing (AGG described as cheaper than BND/LAG). **These two sections of the source data are not consistent with each other on this point, and this report does not attempt to resolve which framing is correct.**

**Explicit limitations:** No primary iShares fact sheet or Bloomberg methodology document was cross-checked. Sector/duration/credit breakdowns of the index itself (as opposed to the fund's holdings) are not available. Dividend yield is reported inconsistently (3.85% / 4.04% / 4.07%). YTD return (-0.47%) has no stated as-of date. Holdings/AUM figures are dated 2026-06-30, roughly 1.5 months before the 2026-08-13 data snapshot.

---

## 2. Holdings / Exposure

Because AGG holds ~13,224 bonds, single-name concentration is not a meaningful risk lens for this fund (unlike an equity ETF's top-10-holdings metric). The relevant lenses are sector, credit quality, and maturity.

**Sector/asset-type composition:**
| Sector | Weight |
|---|---|
| U.S. Treasuries | 46.26% |
| MBS Pass-Through (agency) | 23.43% |
| Industrial (corporate) | 14.28% |
| Financial Institutions (corporate) | 7.90% |
| Utility | 2.53% |
| CMBS | 1.39% |

Treasuries + agency MBS ≈ **70%** of the fund. Corporate credit (Industrial + Financial + Utility) sums to ≈ **24.71%**. Additional smaller allocations exist but are not itemized in the data.

**Credit quality:** AAA 2.21%, AA 73.60%, A 11.85%, BBB 11.63%; **no BB-or-below exposure reported.** This is an investment-grade-only profile. However, the data flags an **unresolved internal inconsistency**: AA (73.60%) is far larger than the Treasury weighting (46.26%), while AAA is only 2.21%, despite Treasuries being conventionally treated as AAA-equivalent in many frameworks. The source data does not explain this, and no attempt is made here to speculate on the rating methodology behind it.

**Maturity structure:** 7–10yr (23.23%), 3–5yr (21.11%), 5–7yr (13.93%), 1–2yr (11.98%) — these four buckets sum to ≈70.25% of the fund. **Roughly 30% of the maturity distribution (other bands, e.g., 0–1yr, 10–20yr, 20+yr) is not covered in the data provided**, so a complete maturity/duration picture cannot be constructed from holdings data alone.

---

## 3. Cost / Tracking

**Expense ratio:** AGG's expense ratio is **0.03%**, below QQQ (0.18%) and SCHD (0.06%) in the comparison set. The data also describes AGG as cheaper than BND and LAG, though (as noted in Section 1) no comparative BND/LAG figures are actually provided anywhere in the source material, so this cost-leadership claim cannot be quantified or fully verified — and one section of the data (Composition) describes the relationship in the opposite direction. This contradiction is left unresolved.

**Tracking error:** **No numeric tracking-error figure exists in the data for AGG** (nor for QQQ or SCHD, per the source material). The only substantive point the data supports is a structural/qualitative one: because AGG uses sampling rather than full replication, and because sampling specifically avoids lower-liquidity index constituents, the construction method itself is a plausible mechanism for tracking deviation — distinct from cost- or securities-lending-based explanations offered elsewhere in the dataset for other funds.

**Bottom line:** The data supports a clear, low stated expense ratio (0.03%). It does not support any quantitative statement about actual tracking performance.

---

## 4. Performance / Risk

**Returns:** YTD return of **-0.47%** (as-of date unspecified) versus a trailing 1-year total return of **+2.36%** including dividends. The data does not provide an income/price breakdown to fully reconcile these two figures.

**Yield metrics:** 30-day SEC Yield **4.51%** and Yield to Maturity **4.38%**, both as of 2026-06-30 — reasonably close to each other. Separately, dividend yield is reported inconsistently across sources (3.85% / 4.04% / 4.07%), an open data-quality issue not resolved in the source material.

**Duration/rate sensitivity:** Effective Duration **5.80 years**, Weighted Average Maturity **8.11 years**. The data translates this to an estimated **~5.85% price move for a 1-percentage-point change in interest rates** (linear duration estimate; no convexity or curve-scenario data provided).

**Volatility/correlation:** 3-year standard deviation **5.51%**, roughly half of SCHD's reported 11.10% in the same dataset (QQQ's volatility is only described qualitatively, not numerically, so a full three-way comparison isn't possible). 3-year equity beta **0.23** — low but non-zero correlation with equities, unexplained further in the data.

**Gaps:** No tracking-error figure; unspecified YTD as-of date; inconsistent dividend yield; ~6-week lag between fact-sheet data (2026-06-30) and snapshot date (2026-08-13); secondary (non-primary-source) data only; a macro note about rate-hike likelihood flagged as possibly overlapping with similarly worded SCHD material, uncorroborated.

---

## 5. Distribution

AGG pays **monthly** (versus quarterly for QQQ/SCHD). Most recent actual distribution: **$0.330/share, paid 2026-05-06**. Next ex-dividend date **2026-08-03** with an estimated forward distribution of **$0.3307/share** — roughly stable, but only two data points, insufficient to establish a trend.

**Yield figures are explicitly inconsistent across sources:**
- 3.85% (as of 2026-08-04)
- 4.04% (annualized from an expected annual distribution of $3.94/share)
- 4.07% (annualized from the most recent distribution)

These differ by ~20 basis points due to differing methodology/dates and were **not cross-verified** against iShares' official fact sheet. No single "correct" figure can be identified from this data; AGG's yield should be treated as approximately high-3% to just-above-4%, methodology-dependent.

**Relative positioning:** AGG's yield (~4% by any of the three measures) is the highest among the three funds referenced, above SCHD (~3%) and QQQ (0.42%) — consistent with its bond-fund nature, though the data offers no duration/credit/rate explanation for the differential beyond reporting the comparison.

---

## 6. Macro

**Rate environment:** The 10-year Treasury has held largely within a **4.0%–4.5%** range since March 2026, with forecasts of **4.25%–4.50% by year-end** and explicitly flagged **upside risk**. Since Agg-index constituents price off the Treasury curve plus spreads, this range-bound-but-upside-skewed backdrop implies limited price-return tailwind from falling yields and continued exposure to further-increase drag.

**Fed policy — explicitly unresolved conflict:** The data states policy-on-hold is the prevailing base case, but also notes market participants increasingly flagging **rate-hike risk**. The source material itself flags this hike-risk narrative as only loosely corroborated (possibly echoing similarly worded, differently sourced SCHD material) and not independently cross-verified. This report does not resolve the conflict; it is left open per the source data.

**Upside-pressure factors cited (unquantified):** inflation persistence, fiscal/deficit concerns, rising global bond yields, oil prices. No specific figures (inflation print, deficit number, oil price level) are given for any of these.

**Duration-positioning commentary:** A general market-commentary note that running duration shorter than benchmark is "currently preferred" appears in the data. This is explicitly **not** a statement about AGG's own duration or the Bloomberg Agg index, and should not be read as such — as an index fund, AGG has no discretion to shorten duration regardless of this commentary.

**Gaps:** Non-primary-source web snapshot (2026-08-13); unverified hike-risk claim; unquantified inflation/fiscal/global-yield/oil factors; no credit-spread or MBS-specific data provided.

---

## 7. Bull Case

1. **Cost structure:** 0.03% expense ratio, cheapest of the three funds compared (QQQ 0.18%, SCHD 0.06%), plus a (unverified, and internally inconsistent with Section 1/3 framing) claim of being cheaper than BND/LAG.
2. **Credit quality:** Zero reported BB-or-below exposure; ~13,224 bonds eliminates single-name risk.
3. **Government/agency backing:** ~70% combined Treasury + agency MBS reduces issuer-solvency risk relative to corporate-heavy funds.
4. **Lower volatility, low equity correlation:** 3-yr std dev 5.51% (about half of SCHD's 11.10%); beta 0.23.
5. **Competitive, monthly income:** Highest yield of the three funds compared by any of the reported measures (3.85–4.07%, or 4.51% SEC yield); monthly cadence aids cash-flow planning; the two available distribution data points are roughly stable.
6. **Positive 1-year total return (+2.36%)** despite negative YTD price action (-0.47%), consistent with income carrying the fund through recent price softness.
7. **Income thesis does not require rate cuts:** at 4.51% SEC yield, a "hold" rate environment alone can sustain the income stream without needing a rate-cutting catalyst.
8. **Sampling framed as a liquidity-quality filter** — a deliberate avoidance of the least-liquid, worst-execution segment of the bond universe, rather than simply an unexplained source of deviation.

**Caveats explicitly carried forward:** no tracking-error evidence exists to prove the cost advantage translates to close index-matching; yield cannot be pinned to one number; the income-carry case is contingent on rates not rising further, which the macro data leaves unresolved; the AA/AAA/Treasury credit-quality discrepancy is unexplained.

---

## 8. Bear Case

1. **Negative price return in an unfavorable rate backdrop:** -0.47% YTD, with the 10-year yield range skewed toward the upside (4.25–4.50% year-end forecast, upside risk flagged) and four cited (unquantified) upward-pressure factors on long yields.
2. **Meaningful, unhedged duration risk:** 5.80-year effective duration (~5.85% price sensitivity per 1-point rate move); as an index fund, AGG cannot tactically shorten duration even though broader market commentary (not AGG-specific) currently favors doing so.
3. **Unquantified structural tracking error:** sampling avoids low-liquidity bonds by design, but no track record (i.e., no actual tracking-error figure) exists anywhere in the data to bound how large the resulting deviation has been.
4. **Inconsistent yield/distribution figures:** three yield numbers spanning ~20bps with no reconciliation; only two distribution data points, insufficient to confirm a stable payout trend.
5. **Unexplained credit-quality inconsistency:** AA (73.60%) vastly exceeds AAA (2.21%) despite a 46.26% Treasury weighting — a possible data-quality or methodology-transparency concern, unresolved.
6. **Cost-leadership claim not fully verifiable:** no comparative BND/LAG expense figures are actually provided, and one section of the source data even frames the comparison in the opposite direction.
7. **Compounding data-quality risk:** secondary, non-primary-sourced, ~6-week-stale snapshot; ~30% of maturity-bucket distribution missing; possibly duplicated/uncorroborated macro commentary.

**Caveats explicitly carried forward:** the rate-hike risk is flagged in the source material itself as unverified, not confirmed; the actual size of tracking error and the true BND/LAG fee comparison remain unknown; these are presented as legitimate uncertainty-based risk considerations, not settled negative facts.

---

## 9. Synthesis

**Where bull and bear agree on facts:** Every specific figure appears identically in both cases — expense ratio (0.03%), duration (5.80 yrs / ~5.85% sensitivity), YTD (-0.47%), 1-year return (+2.36%), the three yield figures plus SEC yield (4.51%) and YTM (4.38%), the credit-quality breakdown, Treasury weighting (46.26%), the sampling construction method, the absence of a tracking-error figure, the two-point distribution history, and the 10-year Treasury range. **No factual contradictions exist between the two cases within Sections 7–8** — the disagreement is entirely about interpretation and emphasis, not the underlying numbers. (Note: a genuine inconsistency does exist *between* Sections 1 and 3 on the BND/LAG cost comparison, as flagged above — this is a source-data conflict, not a bull/bear interpretive difference.)

**Same facts, opposite readings:**
- *Sampling:* bull = deliberate liquidity filter; bear = unquantified tracking-deviation source.
- *Negative YTD / positive 1-yr:* bull = income carried the fund; bear = negative price return is the more informative signal given an upside-skewed rate backdrop.
- *Duration:* bull = manageable contingency if rates hold; bear = largest identifiable risk, unmitigable by an index fund.
- *Multiple yield figures:* bull = attractive under any measure; bear = no single reliable number exists.
- *Two-point distribution history:* bull = "stable"; bear = insufficient to establish a trend.
- *Cost leadership vs. BND/LAG:* bull credits the qualitative claim; bear notes it's unverified (and, per Section 1, even internally contradicted).

**Unresolved data problem both sides flag but neither settles:** the AA (73.60%) vs. AAA (2.21%) vs. Treasury (46.26%) credit-quality discrepancy. Its resolution could meaningfully shift confidence in the credit-quality narrative in either direction.

**Open questions that would most change the conclusion:**
1. AGG's actual tracking error (no figure exists in the data).
2. Whether the Fed holds or hikes, and where the 10-year yield settles within/above the 4.0–4.5% range — the dominant swing factor for near-term price return given the 5.80-year duration.
3. What explains the AA/AAA/Treasury credit-quality discrepancy.
4. BND's and LAG's actual expense ratios (unavailable, and the source data is internally inconsistent on this comparison).
5. A longer distribution history and a single reconciled yield methodology.

**Bottom line:** The two largest points of leverage for a directional judgment — tracking error and the direction of rates — are both explicitly absent or unresolved in the data provided. The dataset supports identifying where more information would be decisive; it does not support a confident directional conclusion in either direction.

---

## Disclaimer

**This document is an analysis exercise only, based strictly on a fixed, point-in-time set of secondary web-search data (snapshot date 2026-08-13; underlying fact-sheet figures dated 2026-06-30). It has not been cross-verified against iShares' official fact sheet, Bloomberg's index methodology, or any primary source. It contains known data gaps, inconsistencies (including an unresolved conflict on the BND/LAG cost comparison and an unexplained credit-quality discrepancy), and unverified claims that are explicitly flagged throughout rather than resolved. This is NOT investment advice, a research recommendation, or a trade recommendation, and no buy/sell/hold judgment is intended or should be inferred. Any investment decision should rely on current, primary-source data and, where appropriate, independent professional advice.**

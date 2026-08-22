## (1) Exposure Paths — Listed Separately (Direct vs. Indirect-via-QQQ)

**AAPL**
- Direct: 8% of portfolio value (direct AAPL holding, Trader Decision: HOLD)
- Indirect-via-QQQ: QQQ = 30% of portfolio × AAPL ≈7.1–7.3% of QQQ's assets = **2.13%–2.19% of portfolio value**

**NVDA**
- Direct: 8% of portfolio value (direct NVDA holding, Trader Decision: HOLD)
- Indirect-via-QQQ: QQQ = 30% of portfolio × NVDA ≈8.5–8.9% of QQQ's assets = **2.55%–2.67% of portfolio value**

These are kept separate deliberately: the direct holding and the QQQ-embedded slice are different instruments with different liquidity/trading mechanics, even though both ultimately create economic exposure to the same underlying company.

## (2) Policy-Compliance Calculation (direct % + ETF% × constituent%)

*Labeled explicitly as a policy-compliance calculation — an arithmetic check against the stated look-through rule, not a claim about "true" single-name risk equivalence between a direct share and an ETF slice.*

**AAPL:** 8% + (30% × 7.1–7.3%) = 8% + 2.13–2.19% = **10.13%–10.19%**
→ Policy threshold: 10%. **Breach: yes, by ~0.13–0.19 percentage points.**

**NVDA:** 8% + (30% × 8.5–8.9%) = 8% + 2.55–2.67% = **10.55%–10.67%**
→ Policy threshold: 10%. **Breach: yes, by ~0.55–0.67 percentage points.**

Both names breach the stated 10% combined look-through policy under the given data. NVDA's breach margin is roughly 3–4x larger than AAPL's.

## (3) Recommended Action to Restore Policy Compliance

Since QQQ itself carries its own independent HOLD decision and trimming it would move exposure to every constituent at once (an indiscriminate, larger-blast-radius lever), the more surgical fix — consistent with the policy being about *this portfolio's* combined exposure to *these specific names* — is to trim each direct position by the amount needed to offset its own indirect slice, using the midpoint of the given constituent ranges:

- **AAPL:** trim the direct AAPL position from 8% to **~7.8% of portfolio value** (a cut of roughly 0.15–0.2 percentage points of total portfolio, ≈2% of the current AAPL position size), bringing combined exposure to ~9.95–10.0%.
- **NVDA:** trim the direct NVDA position from 8% to **~7.3–7.4% of portfolio value** (a cut of roughly 0.6–0.7 percentage points of total portfolio, ≈7–8% of the current NVDA position size), bringing combined exposure to ~9.9–10.0%.

Alternative lever (noted, not recommended as primary): reducing QQQ itself from 30% to ~27.8% of portfolio would independently bring AAPL's combined figure to just under 10%, but would need a larger QQQ cut (to ~26.4%) to simultaneously fix NVDA, and would also shrink exposure to every other QQQ constituent — a blunter instrument than trimming the two named direct positions.

This recommendation is a mechanical policy-compliance sizing adjustment only; it does not revisit or override the HOLD directional calls above, which were made on current-information/no-portfolio-context grounds.

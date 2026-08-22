## PORTFOLIO COMPOSITION — PASS 1

**Inputs taken as given:** three independent, per-security HOLD decisions (AAPL, NVDA, QQQ), each explicitly scoped to that security in isolation with no portfolio context assumed. Current state: AAPL 8% direct, NVDA 8% direct, QQQ 30% (holding AAPL ~7.1–7.3% and NVDA ~8.5–8.9% of its own assets).

**Composition reasoning:**

Each Trader Decision is a per-security stance, not a sizing instruction — HOLD means "no directional edge to act on for this name," which translates at the portfolio level to "no change to this position's target weight based on new information." Since all three decisions are HOLD, ordinary composition logic gives a single conclusion: leave the current weights as they are.

- **AAPL (8% direct):** HOLD → no trim, no add. Maintain 8%.
- **NVDA (8% direct):** HOLD → no trim, no add. Maintain 8%.
- **QQQ (30%):** HOLD → no trim, no add. Maintain 30%, and no change to QQQ's own internal composition is implied or available — that's set by the ETF, not by this portfolio's decisions.

No decision here calls for rebalancing between the three holdings either: nothing points to reallocating from QQQ into the direct names or vice versa, since all three came back HOLD independently and none was compared against the others on relative attractiveness.

**Composition result: no changes.** Portfolio stays AAPL 8% / NVDA 8% / QQQ 30% (+ remaining 54% in other/unlisted holdings, unspecified here).

**Out of scope for this pass:** whether AAPL's and NVDA's look-through exposure via QQQ pushes their combined single-name exposure past the stated 10% policy cap is a cross-holding compliance calculation, not ordinary composition reasoning — flagged as a candidate for a dedicated policy-compliance check, not resolved here.

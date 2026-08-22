## (1) Exposure Paths (each independent, none summed)

**Direct Holding paths:**
- Direct Holding → AAPL: 10% of portfolio value
- Direct Holding → NVDA: 10% of portfolio value

**ETF Holding path:**
- ETF Holding → QQQ: 10% of portfolio value

**ETF→Constituent Indirect Holding paths** (each = QQQ's 10% portfolio weight × QQQ's disclosed constituent weight; reported as its own line, not merged with any Direct line):
- Indirect (via QQQ) → AAPL: 10% × ~7.1–7.3% ≈ ~0.71–0.73% of portfolio value
- Indirect (via QQQ) → NVDA: 10% × ~8.5–8.9% ≈ ~0.85–0.89% of portfolio value
- Indirect (via QQQ) → Top-5 QQQ constituents (combined, undifferentiated): 10% × ~30–33% ≈ ~3.0–3.3% of portfolio value

That's six distinct lines total: 2 Direct, 1 ETF, 3 Indirect. AAPL and NVDA each have two separate lines (one Direct, one Indirect) that stay separate by rule — not a "5 lines because AAPL/NVDA repeat" collapse.

## (2) Is Portfolio-level judgment needed beyond the Data Join?

**Yes.** Listing the paths is necessary but not sufficient. Two things require judgment beyond mechanical listing/multiplication:

1. **Overlap flagging (correlation risk):** AAPL and NVDA each sit on *two* independent paths (Direct + Indirect-via-QQQ) to the same underlying security. Noticing that this pattern exists and is worth surfacing to a risk reviewer — i.e., "these two paths converge on the same name" — is an interpretive judgment about correlated/concentrated exposure, not something the raw data states on its own. The data only gives disjoint numbers; recognizing their relevance *as a pattern* is judgment.

2. **Materiality with no stated policy:** There is no stated position limit or look-through cap. That means nothing in the data tells you whether any of these exposures (or the overlap pattern) is "fine" or "a problem requiring escalation." Deciding whether the Direct 10% AAPL line, the ~0.7% Indirect AAPL line, or the ~30–33% QQQ top-5 concentration line is material enough to flag is a risk-materiality judgment call that has to be made independently of the numbers themselves — the numbers alone can't answer "so what."

So this is **not** a pure Data Join case: producing the six lines above is a Data Join, but forming a view on whether the AAPL/NVDA overlap and the QQQ concentration are noteworthy (given the absence of any stated threshold) requires an additional, separate portfolio-level judgment step.

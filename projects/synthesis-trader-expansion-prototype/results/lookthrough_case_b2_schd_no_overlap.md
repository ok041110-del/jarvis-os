**1. Exposure Paths (independent, unsummed):**

- **Direct Holding — JNJ:** 8% of portfolio value.
- **Indirect Holding — SCHD (ETF wrapper):** 10% of portfolio value.
- **Indirect Holding — SCHD → JNJ (look-through):** Not computable. JNJ is not named among SCHD's confirmed top holdings in the data given, and no per-constituent weight for JNJ within SCHD is provided. This path exists conceptually but has no stated percentage — it cannot be assumed to be 0%, nor can it be estimated, since the data only confirms Abbott Laboratories, UnitedHealth, and Merck as top holdings.

No other underlying securities are named in the data, so no further paths can be listed.

**2. Is a Portfolio-level judgment needed beyond the Data Join?**

Yes. Listing the paths alone is not enough — a judgment is needed, for two distinct reasons:

- **Missing data ≠ zero.** The SCHD→JNJ path can't be reported as a number because the constituent weight isn't in the data. A judgment call is required on how to *treat* that gap (e.g., flag as "unknown/unconfirmed" vs. requesting the full SCHD holdings list vs. bounding it using the 4.42% max-single-position disclosure as an upper limit). Silently omitting the path or silently treating it as 0% would both be judgment calls in disguise — the prompt forbids inventing a number, but *some* explicit stance on the gap is still required.

- **No aggregation policy exists.** Even if the SCHD→JNJ weight were known, the portfolio has no stated position-limit or look-through-cap policy. So even with complete data, there's no rule available to say whether combined JNJ exposure (direct + look-through, tracked separately per the strict rule) is "acceptable" — that would require a Portfolio-level judgment about risk tolerance/concentration limits that the data doesn't supply. This is a genuine gap in inputs, not something resolvable by better data-joining alone.

So this is **not** a pure Data Join case: it requires (a) an explicit judgment on how to represent the unresolvable SCHD→JNJ path, and (b) an acknowledgment that no concentration-limit policy exists to evaluate the paths against, even once listed.

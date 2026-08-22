**1. Exposure Paths (each reported independently, never summed):**

- **Exposure Path — Direct Holding:** None. No direct holding of any individual stock or security exists in this portfolio.
- **Exposure Path — ETF Holding (Direct):** GLD, 10% of portfolio value.
- **Exposure Path — ETF→Constituent Indirect Holding:** GLD → Physical gold bullion (held in grantor trust), 100% of GLD's composition. This is an indirect exposure line via the ETF wrapper — not merged with the 10% GLD figure above, and not converted into a portfolio-level "% of total portfolio in gold" number.

No other underlying securities are mentioned (GLD's disclosed composition explicitly contains no derivatives, futures, bonds, or equities), so no further constituent-level lines exist.

**2. Is Portfolio-level judgment needed beyond a Data Join?**

No — as given, this is a **Data Join case**. The two facts (10% GLD allocation; GLD is 100% physical bullion in trust) are simply reported side by side as independent lines. No synthesis, weighting, or conversion is required to answer "what are the exposure paths," because:

- There's only one non-empty path chain (portfolio → GLD → bullion), so there's no aggregation-across-paths decision to make (e.g., no case of the same underlying security reachable via two different paths that would raise a "do we combine or not" question).
- The instructions explicitly forbid computing a merged number, so producing one isn't a legitimate output regardless.
- No portfolio policy on look-through caps or position limits is stated, so there is no threshold to evaluate exposure against — nothing to judge "acceptable" or "breached."

The only thing that *would* require judgment (rather than data-joining) is if the task asked something evaluative — e.g., "is this concentration acceptable," "does this breach any limit," or "should this be flagged as a risk." None of those questions were asked here, and none of the inputs needed to answer them (a policy/limit) were supplied. So as posed, listing the paths is the complete and sufficient answer.

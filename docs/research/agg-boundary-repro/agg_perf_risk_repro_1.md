## Performance and Risk Analysis: iShares Core U.S. Aggregate Bond ETF (AGG)

**Historical Performance**

The data shows a mixed short-term performance picture. Year-to-date total return is reported at -0.47%, while the trailing 1-year return (including dividends) is +2.36%. Taken together, these two figures imply that the fund experienced losses earlier in the measurement window preceding the current YTD period, followed by gains sufficient to produce a positive 1-year figure — but the underlying data does not specify the exact date ranges for either figure, so this trajectory cannot be verified in detail. Notably, the source material explicitly flags that the YTD figure's cutoff date is unspecified and may vary depending on the source, which limits confidence in comparing it directly to the 1-year figure or to any other benchmark period.

**Yield Profile**

The fund's 30-day SEC Yield is reported at 4.51% as of 2026-06-30, alongside a Yield to Maturity of 4.38%. These two figures are reasonably close, which is broadly consistent with what one would expect for an investment-grade aggregate bond index fund, though the data does not explain the methodology differences that account for the small gap between them. Separately, dividend yield is reported inconsistently across sources — 3.85%, 4.04%, and 4.07% — a discrepancy the source material itself flags. This inconsistency should be treated as a real limitation: it is not clear which figure (if any) reflects the most current or most methodologically comparable measure, and no reconciliation is provided.

**Interest-Rate Sensitivity (Duration Risk)**

This is the most quantitatively detailed part of the dataset. The fund's Effective Duration is 5.80 years, with a Weighted Average Maturity of 8.11 years — the gap between the two being typical for a bond fund holding a mix of maturities with prepayment, call, and cash-flow timing effects factored into the duration calculation. Based on this duration, the source reports that a 1 percentage-point move in interest rates would be expected to move the fund's price by approximately 5.85% in the opposite direction. This is described as a duration-based estimate rather than an observed or backtested figure, and duration-based linear approximations of this kind become progressively less accurate for larger rate moves (a limitation inherent to the metric, not stated explicitly in the source but worth noting given the data provided assumes linearity). No convexity figure is given, so the degree to which the actual price sensitivity might deviate from this linear estimate — particularly for large rate swings — cannot be assessed from this data.

**Volatility and Market Correlation**

The 3-year standard deviation is 5.51%, and the 3-year equity beta is 0.23. The low beta suggests the fund's returns have historically shown limited correlation with equity markets, consistent with its identity as an investment-grade bond index fund rather than a growth- or equity-linked instrument. However, beta to equities does not capture the fund's primary risk driver, which — per the duration and rate-sensitivity data above — appears to be interest-rate risk rather than equity-market risk. The standard deviation figure is given without a comparison benchmark or peer figure in this dataset, so it is not possible to assess from the provided data alone whether 5.51% represents high, low, or typical volatility for a fund of this duration and credit composition.

**Explicitly Noted Data Limitations**

The source material itself flags several gaps and should be treated with corresponding caution:

- No tracking error figure was found for AGG in the underlying search (a gap noted as consistent with the same absence for the comparison funds referenced, QQQ and SCHD).
- The dividend yield figures (3.85% / 4.04% / 4.07%) conflict across sources without reconciliation.
- The YTD return's cutoff date is not specified, making it unclear how it should be interpreted relative to the 1-year return figure.
- The underlying figures were not cross-checked against iShares' official Fact Sheet PDF or the Bloomberg U.S. Aggregate Bond Index methodology documentation — they derive from web search summaries of stockanalysis.com, ytdreturn.com, and portfolioslab.com.
- There is a noted but unverified similarity between commentary in a "macro" section referenced for this fund and separate commentary referenced for SCHD; these come from different sources and time points and have not been cross-validated, so any implied macro narrative should not be treated as confirmed.
- The data reflects a search snapshot from 2026-08-13, while some figures (notably the SEC Yield) are sourced from a Fact Sheet dated 2026-06-30 — roughly six weeks earlier — introducing a timing lag between different figures cited in the same analysis.

Given these gaps — particularly the unreconciled dividend-yield figures, the unspecified YTD cutoff date, and the absence of tracking-error and convexity data — this dataset supports a general characterization of AGG as a fund with moderate interest-rate duration risk and low historical equity correlation, but it is not sufficient to make more precise or comparative quantitative claims beyond what is stated above.

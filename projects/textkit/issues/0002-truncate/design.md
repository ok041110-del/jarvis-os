# Design: Add truncate() to textkit

## Design: `truncate()` for textkit

**Approach**

Implement as a single pure function in a new module `src/textkit/truncate.py`, with no import of or dependency on `slugify.py` — same "one function per module" layout the package already uses. The function body is a straightforward two-branch structure: a length check, then either a passthrough or a slice-and-concatenate. No helper functions, no class, no configuration object — the signature given in the requirement (`text: str, max_len: int, suffix: str = "..."`) is the complete public surface.

Core logic, resolving the open questions from the requirement doc:

1. `len(text) <= max_len` → return `text` unchanged. This is checked first and short-circuits everything else, so a `text` that already ends with `...` is never touched.
2. Otherwise, validate feasibility: if `max_len < len(suffix)`, raise `ValueError` with a message naming both values (e.g. `f"max_len ({max_len}) is shorter than suffix length ({len(suffix)})"`) — this single check also covers `max_len < 0` when `suffix` is non-empty, since any non-negative `len(suffix)` is `> max_len` in that case. For the residual case `suffix == "" and max_len < 0`, add an explicit `max_len < 0` guard so negative `max_len` is *always* rejected regardless of suffix — this closes the gap the requirement doc flagged in risk #1, rather than leaving it to silently slice into a shorter-than-expected (but not obviously wrong) empty-ish string.
3. Otherwise return `text[:max_len - len(suffix)] + suffix`. When `suffix == ""` this degrades to plain `text[:max_len]` for free, with no special-casing needed. When `max_len == len(suffix)` the slice is `text[:0]` = `""`, so the result is exactly `suffix`, also for free.

So the only explicit branch beyond the main two is the validation raise — everything else falls out of the arithmetic naturally, which keeps the implementation as small as `slugify.py`'s.

**Responsibilities**

- Own only the truncation decision and the exact-length guarantee (`len(result) <= max_len` always; `len(result) == max_len` whenever truncation actually occurs).
- Not responsible for: unicode grapheme/width awareness, word-boundary trimming, stripping trailing whitespace before appending the suffix, or validating argument types. These are explicitly out of scope per the requirement, matching `slugify.py`'s stdlib-only, ASCII-length-based simplicity.
- The docstring carries the contract: one-line summary, a short "Args/Returns" block, an explicit statement of the `ValueError` condition, and 2–3 worked examples at the boundary (`len(text) == max_len`, `len(text) == max_len + 1`, `max_len == len(suffix)`) so the off-by-one risk the requirement flagged is documented, not just tested.

**Risks**

- **Off-by-one in the slice bound** is the main implementation risk called out in the requirement — mitigated by keeping the arithmetic in one place (`max_len - len(suffix)`) and covering the three boundary cases in both docstring examples and unit tests, rather than trusting the formula unverified.
- **Negative `max_len` with empty `suffix`** is the one edge case that doesn't fall out of the `max_len < len(suffix)` check automatically; the design adds a small, separate guard for it. Worth flagging explicitly during review since it's easy to drop this second check as "redundant" with the first.
- **Scope creep**: since this mirrors `slugify.py`, the main ongoing risk is someone later bolting on word-boundary or unicode-width awareness as a "small addition" — the design intentionally keeps the function single-purpose so that any such request becomes a new function/parameter discussion rather than a silent behavior change.

**Test plan (for the follow-up implementation step)**

- `len(text) <= max_len` → unchanged, including exact equality.
- `len(text) == max_len + 1` → one-char-over boundary.
- `max_len == len(suffix)` → returns bare suffix.
- `suffix == ""` → plain truncation.
- `max_len < len(suffix)` → raises `ValueError`.
- `max_len < 0, suffix == ""` → raises `ValueError`.
- Non-str `text` / non-int `max_len` → left unasserted or asserted only as "raises some exception," not pinned to a specific type, consistent with letting stdlib operations fail organically.

This is ready for implementation as-is unless you want to adjust the negative-`max_len`-with-empty-suffix behavior (e.g., clamp to `""` instead of raising) — that's the one place the requirement doc left slightly open and I picked "always raise" for consistency with the rest of the fail-fast contract.


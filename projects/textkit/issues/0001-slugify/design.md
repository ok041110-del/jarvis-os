# Design: Add slugify() to textkit

## Design: `slugify()` for textkit

**Approach**

Implement `slugify` as a single pure function using the `re` module, avoiding a hand-rolled character-by-character loop. The core is a two-step regex pipeline rather than four discrete passes, since steps 2 and 3 collapse naturally into one substitution:

1. Lowercase via `text.lower()`.
2. A single `re.sub(r'[^a-z0-9]+', '-', lowered)` handles both "replace non-alphanumeric" and "collapse runs of hyphens" in one pass — because the pattern matches *runs* of one-or-more disallowed characters and replaces each run with a single hyphen, there's no need for a separate collapse step afterward. This is simpler and cheaper than replacing character-by-character then collapsing.
3. `.strip('-')` on the result handles leading/trailing trim.

Note the character class here is `[a-z0-9]`, an explicit ASCII literal set — not `str.isalnum()` and not a Unicode-aware regex class like `\w`. This directly resolves the Unicode ambiguity flagged in the risk analysis: by hardcoding the ASCII range instead of relying on Python's locale/Unicode-sensitive `isalnum()`, accented and non-ASCII alphanumeric characters (é, ñ, CJK, etc.) are guaranteed to fall into "non-alphanumeric" and become hyphens, consistent with the "ASCII-only, no transliteration" scope decision. This sidesteps the correctness risk around case-folding edge cases entirely, since the regex is applied after lowering and only ever matches literal ASCII bytes.

**Responsibilities**

- The function is self-contained: input in, string out, no side effects, no I/O, no shared state — fits cleanly as a leaf utility in whatever module textkit uses for text-transform helpers (e.g. alongside other normalization functions, not bundled with unrelated concerns like URL building or file I/O).
- Signature: `def slugify(text: str) -> str`, with a short docstring stating (a) ASCII-only scope, (b) that non-ASCII alphanumerics are treated as separators, and (c) that it does not validate input type — a non-`str` argument is the caller's responsibility and will raise naturally (e.g. `AttributeError` on `.lower()`) rather than being caught and re-raised as something friendlier. No defensive `isinstance` check, since that would be validating a contract the type signature already states.
- Test responsibility: cover the two named edge cases explicitly (empty string → empty string; all-non-alphanumeric input like `"!!!"` → empty string), plus a couple of representative cases (mixed case, internal punctuation/whitespace collapsing to one hyphen, leading/trailing symbols being stripped) to pin down the regex behavior rather than relying on the edge cases alone.

**Risks**

- **Scope creep pressure**: the most likely follow-up ask is Unicode transliteration (é → e) once someone feeds it a non-English title. Documenting the ASCII-only decision in the docstring up front makes this a deliberate, visible tradeoff rather than a silent gap discovered later.
- **Regex correctness is the only real failure surface**: since the whole function reduces to one `re.sub` and one `strip`, the main implementation risk is getting the character class or quantifier wrong (e.g. forgetting the `+` and losing the collapse behavior, or misordering `.lower()` after the substitution instead of before). This is cheap to catch with the test cases above.
- **No behavior contract for non-str/None**: acceptable per the stated scope, but worth a one-line docstring note so it's a documented assumption rather than an implicit one.

This is low-risk, low-surface-area work — ready to implement as soon as this design is confirmed.


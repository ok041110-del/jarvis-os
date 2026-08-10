# Validation: Add truncate() to textkit

## Code Review

A few real issues here:

**Validation is bypassed on the "no truncation needed" path.** The docstring's `Raises` section states unconditionally that `ValueError` is raised "if `max_len` is negative, or if `max_len` is shorter than `len(suffix)`." But both checks live *after* the `if len(text) <= max_len: return text` early return. So `truncate("hi", 2, suffix="...")` (where `max_len=2 < len(suffix)=3`) silently returns `"hi"` instead of raising, because the text already fits. This contradicts the documented contract — callers relying on the docstring to guarantee validation regardless of input length will be surprised. Either the docstring should clarify the checks only apply when truncation is actually needed, or the validation should be moved to the top of the function so it's unconditional.

**Validate-before-use ordering is fragile as a general pattern.** Even though it happens to be safe today (since `len(text)` can never be negative, so a negative `max_len` can never satisfy the early-return branch), doing input validation *after* logic that depends on the unvalidated input is a risky pattern. It works now only by a coincidence of `len()`'s return type; it's easy for a future edit to break silently. Idiomatic style would validate `max_len` and `suffix` first, then proceed.

**Truncation is character/code-point based, not grapheme- or width-aware.** Slicing with `text[:n]` can split a multi-codepoint grapheme cluster (combining characters, emoji with ZWJ sequences, flag sequences, etc.), producing malformed or visually broken output at the truncation boundary. This may be acceptable for the intended use case, but it's worth noting as a limitation since the docstring doesn't mention it.

**Minor:** the `suffix` parameter isn't validated for type/content beyond its length — e.g., nothing stops a caller from passing a `suffix` longer than `text` itself when no truncation is needed (harmless), but combined with the first issue, the function's guarantees around `suffix` fitting within `max_len` are weaker than advertised.


## Test Execution

Based on the code and review findings, here's a proposed test suite for `truncate`:

**Basic behavior**
1. `truncate("hello", 5)` → `"hello"` (exact fit, no truncation)
2. `truncate("hi", 10)` → `"hi"` (text shorter than max_len)
3. `truncate("hello!", 5)` → `"he..."` (truncation with default suffix)
4. `truncate("", 5)` → `""` (empty text)
5. `truncate("", 0)` → `""` (empty text, zero max_len)

**Boundary/off-by-one on length**
6. `truncate("hello", 4)` → result length exactly 4, e.g. `"h..."`
7. `truncate("x" * 100, 10)` → result has length exactly 10

**Custom suffix**
8. `truncate("hello world", 8, suffix="…")` → single-char suffix, verify correct slice length
9. `truncate("hello world", 5, suffix="[cut]")` → `max_len == len(suffix)`, result equals suffix exactly with no original text
10. `truncate("hi", 5, suffix="")` → empty suffix behaves as plain slicing, no `ValueError` since `len(suffix) == 0`

**Validation — exercising the bug found in review**
11. `truncate("hi", 2, suffix="...")` → **documents current (buggy) behavior**: `max_len < len(suffix)` but text already fits, so no `ValueError` is raised, returns `"hi"`. This test should be written to pin down/expose the contract violation the review flagged — likely as an expected-failure or explicitly asserting the surprising pass-through, so it forces a decision (fix code vs. fix docstring) rather than staying silently inconsistent.
12. `truncate("hello world", 2, suffix="...")` → truncation *is* needed and `max_len < len(suffix)`, so `ValueError` should be raised
13. `truncate("hello world", -1)` → truncation needed and `max_len` negative → `ValueError` raised
14. `truncate("hi", -1)` → **same bug class as #11**: text fits despite negative `max_len`, so no `ValueError` is raised; document/pin this too
15. `truncate("hello world", 3, suffix="...")` → `max_len == len(suffix)` and truncation needed → `ValueError` (since check is `max_len < len(suffix)`, this should NOT raise — verify boundary is inclusive, result is just the suffix)

**Suffix longer than text edge cases**
16. `truncate("ab", 10, suffix="......................")` → suffix longer than max_len but text fits within max_len → returns `"ab"` unchanged (no validation triggered)

**Unicode / multi-codepoint (documents known limitation from review)**
17. `truncate("café" + "x" * 10, 6)` — combining/accented characters near the truncation boundary; assert current code-point-based slicing behavior (not asserting "correctness" of grapheme handling, just pinning documented behavior)
18. `truncate("👨‍👩‍👧‍👦" + "hello", 5)` — multi-codepoint emoji (ZWJ sequence) straddling the slice boundary; assert it may split the sequence, documenting the limitation rather than asserting visual correctness

**Type/argument sanity**
19. `truncate("hello", 5, suffix="...")` called with keyword vs positional suffix — confirm signature behaves identically either way (basic API test, low priority)

**Idempotency**
20. Truncating an already-truncated result again with the same `max_len` returns the same string (`truncate(truncate(text, n), n) == truncate(text, n)`)

Priority: tests #6, #7, #11–15 are the most important since they directly probe the validation-ordering bug the review identified — they'll either pin the current buggy contract or fail once it's fixed, which is exactly the signal needed to confirm a fix.


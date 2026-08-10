# Planning: Add truncate() to textkit

## Requirement Analysis: `truncate()` for textkit

**Goal**

Add a `truncate(text: str, max_len: int, suffix: str = "...") -> str` function to the `textkit` package, alongside the existing `slugify.py`, that shortens a string to fit within a maximum length while appending a suffix (ellipsis by default) to signal truncation occurred.

**Scope**

- New module, e.g. `src/textkit/truncate.py`, mirroring `slugify.py`'s style: pure standard library, no external dependencies, a single small top-level function with a docstring describing behavior and edge cases (not implementation).
- Behavior to define precisely:
  - If `len(text) <= max_len`: return `text` unchanged (no suffix appended even if `text` already ends similarly to `suffix`).
  - If `len(text) > max_len`: return `text[:max_len - len(suffix)] + suffix`, so the final returned string's length is exactly `max_len`.
  - Edge case `max_len < len(suffix)`: must be explicitly defined rather than left to silently produce a malformed (over-length or negatively-sliced) result. Raising `ValueError` is the suggested approach, consistent with failing fast on unsatisfiable constraints — the alternative (silently returning something longer than `max_len`, or clamping) would violate the "exact max_len" contract and should be rejected.
  - `max_len == len(suffix)` should be valid and simply return `suffix` alone (empty text slice).
  - No type validation beyond what standard library operations naturally enforce (matches `slugify`'s convention of letting `AttributeError`/`TypeError` surface naturally rather than adding explicit `isinstance` checks) — e.g. non-str `text` or non-int `max_len` will raise organically via slicing/`len()`.
- No dependency on `slugify.py`; the two live in the same package independently, matching the existing module-per-function organization.
- Out of scope: multi-byte/grapheme-aware truncation (e.g., emoji, combining characters, CJK display-width), word-boundary-aware truncation, and locale-specific ellipsis handling — the function operates on Python string length (code points) only, same level of simplicity as `slugify`'s ASCII-only, non-Unicode-aware design.

**Risks / open questions to resolve before implementation**

1. **Negative or zero `max_len`**: should this also raise `ValueError` (arguably covered by the `max_len < len(suffix)` check when `suffix` is non-empty, but if `suffix=""` and `max_len` is negative, slicing silently produces unexpected results) — the spec should state whether `max_len < 0` is always an error regardless of `suffix`.
2. **Empty `suffix`**: valid and should degrase gracefully to plain truncation (`text[:max_len]`), but this should be stated explicitly to avoid ambiguity.
3. **Off-by-one risk in implementation**: the "cut length = `max_len - len(suffix)`" rule is simple but easy to get wrong (e.g., using `max_len` instead of `max_len - len(suffix)` as the slice bound) — worth a docstring example and test cases at the boundary (`len(text) == max_len`, `len(text) == max_len + 1`, `max_len == len(suffix)`).
4. **Exception type choice**: `ValueError` is idiomatic for "argument value is invalid given other arguments," consistent with Python stdlib conventions (e.g., `str.ljust` doesn't hit this case, but `ValueError` is the standard choice over a custom exception) — no external dependency needed, so this fits the stdlib-only constraint.
5. **Consistency with `slugify.py`'s minimalism**: avoid adding configurability beyond what's requested (e.g., no `truncate_words` mode, no Unicode-width awareness) unless the user asks — keep the function single-purpose.

No code changes are proposed here per the request; this is purely the requirement description for review before implementation.


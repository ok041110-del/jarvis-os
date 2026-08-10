# Planning: Add slugify() to textkit

## Requirement Analysis: `slugify()` for textkit

**Goal**
Add a pure Python utility function, `slugify(text: str) -> str`, to the textkit project that converts an arbitrary input string into a URL-safe "slug" — the kind of string commonly used in URL paths, filenames, or identifiers (e.g., for blog post titles or resource names).

**Functional behavior**
The function must perform four transformations in sequence:
1. Lowercase the entire input string.
2. Replace every character that is not alphanumeric (i.e., not `[a-z0-9]` after lowercasing) with a hyphen (`-`).
3. Collapse any run of consecutive hyphens into a single hyphen.
4. Strip any leading or trailing hyphens from the result.

**Edge cases**
- An empty input string must return an empty string.
- An input containing no alphanumeric characters at all (e.g., `"!!!"`) must also return an empty string — this falls out naturally from the transformation rules (everything becomes hyphens, which then get stripped), but should be explicitly covered by tests since it's a named requirement.

**Scope**
- Single function, no new classes or configuration.
- Standard library only — no dependencies (e.g., `re` and `str` methods are sufficient; no need for `python-slugify` or similar packages).
- The request only specifies ASCII alphanumeric handling implicitly ("영숫자" / alphanumeric with no mention of Unicode/accent normalization). Scope should be limited to ASCII behavior unless the user clarifies otherwise — no transliteration of accented characters (e.g., `é` → `e`) is requested, so such characters would simply be treated as non-alphanumeric and replaced with a hyphen.
- Out of scope: length limits/truncation, custom separator characters, Unicode normalization/transliteration, stopword removal — none of these were requested.

**Risks / open questions**
- **Unicode ambiguity**: `str.isalnum()` in Python returns `True` for many non-ASCII characters (e.g., `é`, `ñ`, CJK characters), which could produce slugs containing non-ASCII bytes — arguably not "URL-safe" in the strict sense. The requirement doesn't clarify whether non-ASCII alphanumerics should be preserved, transliterated, or stripped. This should be clarified or explicitly documented as an assumption before implementation.
- **Regex vs. manual implementation**: Using `re.sub` is the natural standard-library approach; care is needed to ensure the "non-alphanumeric" character class matches Python's own definition of alphanumeric consistently with the lowercasing step (case-folding edge cases, e.g., German ß, are unlikely to matter here but are a minor correctness risk if Unicode input is in scope).
- **No type/behavior for non-str input**: The signature assumes `text: str`; the requirement doesn't specify behavior for `None` or non-string input, so this is presumably out of scope (caller responsibility) but worth a brief docstring note.
- **Low overall risk**: This is a small, pure, side-effect-free function with well-specified behavior and clear test cases (including the two explicit edge cases), so implementation risk is low once the Unicode-scope question is settled.


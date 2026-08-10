# Validation: Add slugify() to textkit

## Code Review

A few points worth flagging:

**Collision risk**: The function silently collapses distinct inputs to the same slug. `"café"` and `"caf"` both become `"caf"` since accented characters are dropped as separators rather than transliterated (e.g. to `"cafe"`). Similarly `"foo_bar"`, `"foo bar"`, and `"FOO BAR"` all normalize to `"foo-bar"`. If slugs are used as unique identifiers (URLs, filenames, dict keys) without an uniqueness check downstream, this can cause silent overwrites/collisions.

**Empty-string output**: Input that is entirely non-ASCII-alphanumeric (e.g. `"!!!"`, `"日本語"`, `"   "`) produces `""` after the strip. There's no guard against this, so callers relying on a non-empty slug (e.g. as a URL path segment or filename) could get unexpected empty values or downstream errors.

**Underscore handling**: `_` is treated as a separator and replaced with `-`, which may be surprising — many "slugify" implementations preserve underscores or treat them as word characters. This is a design choice worth confirming matches intended semantics, not necessarily wrong, but easy to get bitten by if callers pass snake_case identifiers expecting them preserved.

**No length limit**: Very long input text produces an arbitrarily long slug, which could be an issue if the result is stored in a fixed-width DB column or used in a URL with length constraints.

**Multiple non-alphanumeric runs of different characters collapse identically**: e.g. `"a---b"`, `"a b"`, `"a??b"` are indistinguishable in the output (`"a-b"`), which is likely intended given the docstring, but reinforces the collision concern above if slugs need to be reversible or distinguishable.

None of these are outright crashes (the non-str case is explicitly documented as intentional), but the collision/empty-output risks are the kind of thing that bite in production if slugs are assumed unique or non-empty.


## Test Execution

## Proposed test cases for `slugify`

**Basic / happy path**
- `"Hello World"` → `"hello-world"`
- `"already-a-slug"` → `"already-a-slug"` (idempotent)
- `"  leading and trailing spaces  "` → `"leading-and-trailing-spaces"`

**Collision cases (documenting current — possibly undesired — behavior)**
- `"café"` → `"caf"` (accent dropped, not transliterated)
- `"caf"` → `"caf"` (collides with above)
- `"foo_bar"`, `"foo bar"`, `"FOO BAR"` → all → `"foo-bar"`
- `"a---b"`, `"a b"`, `"a??b"` → all → `"a-b"`
- `"Naïve"` vs `"Naive"` → both collapse toward the same/near-same slug

**Empty / all-separator input**
- `""` → `""`
- `"!!!"` → `""`
- `"   "` (whitespace only) → `""`
- `"日本語"` (CJK, no ASCII alnum) → `""`
- `"___"` (underscores only) → `""`

**Underscore handling**
- `"snake_case_name"` → `"snake-case-name"` (confirm underscore is treated as separator, not preserved)
- `"_leading_underscore"` → `"leading-underscore"` (stripped, not just replaced)

**Numbers and mixed alnum**
- `"Product123"` → `"product123"`
- `"123 456"` → `"123-456"`
- `"v2.0.1"` → `"v2-0-1"`

**Edge separators**
- `"---hello---"` → `"hello"` (strip leading/trailing dashes after collapse)
- `"a-"`, `"-a"` → `"a"`
- `"a" + "-"*50 + "b"` → `"a-b"` (long run of separators collapses to one)

**Length**
- Very long input (e.g. 10,000 chars) → confirm no length limit is enforced, output length matches expectation (documents the "no length limit" review point rather than asserting a cap)

**Type errors (documented behavior, not a bug)**
- `slugify(None)` → raises `AttributeError`
- `slugify(123)` → raises `AttributeError`

**Mixed Unicode + ASCII**
- `"Héllo Wörld"` → `"h-llo-w-rld"` or similar (accented chars act as separators mid-word — verify exact collapse behavior, since consecutive accented chars could produce multiple dashes vs. one)
- `"100% done"` → `"100-done"`

If useful, I can also write these out as actual `pytest` parametrized test code.


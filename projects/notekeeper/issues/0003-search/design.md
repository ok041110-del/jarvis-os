# Design: Add search_notes() to notekeeper

## Design: `search_notes()` for notekeeper

### Approach

`search_notes` is a pure function living in a new module, `src/notekeeper/search.py`. It takes the store and two optional filters, pulls the full note list once via `store.list()`, and applies a single-pass filter using a small in-line predicate per note — no intermediate data structures, no re-implementation of storage access.

Concretely, the flow is:

1. Call `store.list()` once to get the source sequence (respecting insertion order).
2. For each note, evaluate up to two independent boolean conditions:
   - **Text condition** (only if `query is not None`): `query.lower()` is a substring of `note.title.lower()` or `note.body.lower()`.
   - **Tag condition** (only if `tag is not None`): `tag.lower()` equals `t.lower()` for some `t` in `note.tags`.
3. A note is kept if all *supplied* conditions hold. `None` filters are simply skipped rather than defaulted to "match everything" via a placeholder — this avoids awkward sentinel logic and keeps the AND-combination trivial to reason about (skipped conditions don't affect the AND).
4. Return the kept notes as a new `list`, in the same relative order they came out of `store.list()`.

No filtering framework, no query objects, no comprehension-of-comprehensions cleverness — this is a straight `for`/`if` loop (or an equivalent single list comprehension with a local helper function for readability), because the logic is simple enough that an abstraction would cost more clarity than it buys.

### Responsibilities

- **`search.py` owns**: interpreting the two filter parameters, case-insensitive comparison logic, AND-combination, and result-order preservation.
- **`NoteStore` owns**: everything about how notes are stored and iterated. `search_notes` treats `store.list()` as an opaque, already-ordered sequence and asserts nothing about its backing structure beyond "iterable of `Note`."
- **Caller owns**: deciding what `query`/`tag` values to pass; `search_notes` does no input normalization beyond its own case-folding (e.g., it won't strip whitespace from `query`).

This keeps a clean layering: storage (`NoteStore`) → stateless filtering (`search.py`) → whatever consumes the filtered list (CLI/API, out of scope here).

### Risks and edge cases (decisions made explicit)

- **`None` vs `""`**: `None` means "no filter on this axis" (condition skipped). `""` is a real value — for `query=""`, every note passes (empty string is a substring of anything); for `tag=""`, only notes with a literal `""` entry in `tags` pass. This is a natural consequence of the implementation, not a special case to code around.
- **Case folding**: both sides of every comparison are lowercased at the point of comparison (not pre-lowercased and cached), since notes are small in number and premature optimization here would add state for no measurable benefit.
- **Non-string tags**: not guarded against. If `Note.tags` contains a non-string, `.lower()` will raise `AttributeError` naturally — consistent with the rest of the codebase's informal typing, and preferable to swallowing the error and silently mis-filtering.
- **No mutation**: the function only reads `note.title`, `note.body`, `note.tags` and builds a new list; it never writes to a `Note` or to `store`.
- **Order preservation**: because filtering is a single forward pass with no sort/group/set operations, `store.list()`'s order is preserved automatically — this falls out of the implementation rather than needing an explicit sort-by-nothing step.

### What's deliberately not built

No indexing, caching, tokenization, or scoring. No new `NoteStore` methods. No handling for multi-tag queries or fuzzy matching. The function is intentionally a thin, stateless filter — matching the requirement's explicit scope boundary — so it stays easy to verify by inspection (roughly a dozen lines) and doesn't create a second, competing notion of "how notes are queried" alongside `NoteStore`.


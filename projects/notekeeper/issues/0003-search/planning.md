# Planning: Add search_notes() to notekeeper

## Requirement Analysis: `search_notes()` for notekeeper

**Goal**

Add a pure, read-only search capability over notes already held in a `NoteStore`. The function `search_notes(store, query=None, tag=None) -> list[Note]` lets callers filter the full note collection by free-text substring match (title/body) and/or exact tag match, combined with AND semantics when both are supplied.

**Scope**

- New file `src/notekeeper/search.py` containing a single function, no new classes.
- Data access is restricted to `store.list()` — the function must not touch `store._notes`, the filesystem, or add any new persistence/query method to `NoteStore`. This keeps `NoteStore` as the sole owner of storage concerns and `search.py` as a stateless filter layer on top of it.
- Filtering semantics:
  - `query`: case-insensitive substring match against `title` OR `body`.
  - `tag`: case-insensitive exact match against any element of `tags` (not a substring match on tags).
  - Both given → logical AND (note must satisfy both).
  - Neither given → return all notes unchanged (in `store.list()`'s order, not sorted or deduplicated).
- Result ordering must mirror `store.list()`'s iteration order — since that's backed by a `dict[str, Note]`, order is insertion order, and `search_notes` must not reorder (no sorting by title, date, relevance, etc.).
- Stdlib only — no external dependencies (no `re` needed either; `in` / `.lower()` suffice; using `re` wouldn't be an "external library" but is unnecessary for pure substring/equality checks, so plain string methods are the natural fit).

**Out of scope**

- No ranking/relevance scoring, no fuzzy or tokenized search, no pagination, no case-sensitive option, no multi-tag queries (only single `tag` param per the signature), no CLI/API wiring — this is just the filter function itself.
- No changes to `Note` or `NoteStore`.

**Risks / edge cases to get right**

- **Empty/whitespace string vs `None`**: an empty-string `query=""` or `tag=""` is technically "given" (not `None`) — needs a clear decision on whether `""` should match everything (substring of everything is trivially true, so this falls out naturally) or be treated as "no filter." The spec only distinguishes on `None`, so `""` should behave as a real filter (matches everything for substring; for tag, an empty tag would only match if a note literally has `""` in its tags list — an unlikely but valid edge case, not something to special-case away).
- **Case sensitivity**: must lowercase both sides consistently (`query.lower() in title.lower()`), and same for tags — a note's stored tags may have mixed case, and so may the query tag.
- **`tags` field looseness**: `Note.tags` is untyped (`field(default_factory=list)`), so nothing guarantees list elements are strings; a non-string tag would raise on `.lower()`. Given the existing codebase's informal typing, this is an acceptable/expected risk rather than something `search_notes` needs to guard against — but worth flagging as an assumption (tags are always strings) rather than silently swallowing errors.
- **Mutating vs. copying**: must return a new list (filtered), not mutate `store`'s internal state or the notes themselves.
- **No new abstractions**: the instructions explicitly forbid inventing new storage-access logic — the temptation to add indexing/caching for performance should be resisted since it's unneeded for this scope and would violate the "use `store.list()`" constraint.

This is a small, well-bounded filtering utility; the main correctness risks are around case-insensitivity consistency and preserving `store.list()`'s order rather than any architectural complexity.


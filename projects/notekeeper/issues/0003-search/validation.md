# Validation: Add search_notes() to notekeeper

## Code Review

Here's my review of `search_notes`:

**Inefficiency (minor perf bug):** `q = query.lower()` and `t = tag.lower()` are computed *inside* the `for note in store.list()` loop even though `query` and `tag` are loop-invariant. For any non-trivial `store.list()`, this repeats the same string-lowering work on every iteration for no reason — it should be hoisted above the loop.

**Inconsistent handling of empty-string filters:** `query=""` and `tag=""` are both truthy checks bypassed by `is not None`, so they're treated as "active" filters, but they behave very differently in practice. An empty `query` matches every note (since `"" in anything` is always `True`), silently returning everything as if no filter were applied — that's probably not what a caller expects from passing `query=""`. An empty `tag`, by contrast, will only match notes that literally have an empty-string tag, which in practice means it matches nothing. This asymmetry is a latent footgun for callers who don't distinguish `None` from `""` (e.g., an empty search box in a UI).

**Fragility around `None`/non-string fields:** The function assumes `note.title`, `note.body`, and every element of `note.tags` are non-None strings, since it calls `.lower()` on them unconditionally. If `NoteStore`/`Note` doesn't strictly guarantee that (e.g., an optional body field, or a tag list that can contain `None`), this will raise `AttributeError` at runtime. Nothing in the shown code enforces or documents that invariant.

**Case-folding correctness:** Using `.lower()` for case-insensitive comparison is a common but imperfect choice for Unicode text (e.g., German ß, Turkish dotless i); `.casefold()` is the more robust choice for case-insensitive matching. Minor, but worth knowing if notes can contain non-ASCII text.

**Style/typing nit:** The return type is bare `list` rather than `list[Note]` (or whatever the note type is), which loses type-checker value given the function otherwise uses modern `str | None` syntax.

**Implicit AND semantics undocumented:** When both `query` and `tag` are provided, a note must satisfy both to be included. That's a reasonable default, but it's not stated anywhere (docstring or otherwise), so callers have to read the implementation to know it's AND rather than OR.


## Test Execution

## Proposed test cases for `search_notes`

**Basic filtering behavior**
1. `query=None, tag=None` → returns all notes from `store.list()`, unmodified order.
2. `query="foo"` matches a note by title only (substring in title, not in body).
3. `query="foo"` matches a note by body only (substring in body, not in title).
4. `query="foo"` matches a note where the term appears in both title and body — note appears once, not duplicated.
5. `query="nomatch"` → returns empty list.
6. `tag="work"` matches a note whose `tags` contains exactly `"work"`.
7. `tag="work"` does not match a note whose tags contain `"work-related"` (no partial/substring tag matching).
8. `tag="nomatch"` → returns empty list.
9. `query` and `tag` both provided, note satisfies only `query` → excluded (confirms AND semantics).
10. `query` and `tag` both provided, note satisfies only `tag` → excluded.
11. `query` and `tag` both provided, note satisfies both → included.
12. `query` and `tag` both provided, no notes satisfy both → empty list even if each filter alone would match something.

**Case-insensitivity**
13. `query="FOO"` matches a note containing `"foo"` (and vice versa) in title.
14. `tag="Work"` matches a note tagged `"work"` (and vice versa).
15. Mixed-case query matches mixed-case content, e.g. `query="FoO"` vs body `"...fOo..."`.
16. (Documents current behavior, not a bug fix) Unicode case-folding edge case, e.g. German `"straße"` vs `"STRASSE"` — expected to currently *fail* to match with `.lower()`, capturing the review's noted limitation as a known-behavior regression test.

**Empty-string filter asymmetry (from review)**
17. `query=""` → returns all notes (every note matches, since `"" in s` is always `True`) — locks in current documented behavior.
18. `tag=""` → returns empty list (no note has an empty-string tag) unless a note explicitly has `""` in its tags list, in which case it should match — locks in the asymmetry the review flagged.
19. `tag=""` where a note's `tags` list literally contains `""` → that note is included.

**Store contents / edge cases on the store side**
20. `store.list()` returns an empty list → `search_notes` returns `[]` regardless of filters.
21. A note with an empty `tags` list ([]) → never matched by any non-None `tag` filter, always passes when `tag=None`.
22. A note with duplicate tags (e.g. `["work", "work"]`) → still matched correctly by `tag="work"`, no duplicate entries in results.
23. Query substring spanning a boundary that only matches when title+body are considered separately (e.g. query is split across title and body but not contiguous in either) → should NOT match, since check is per-field, not concatenated.

**Fragility around None/non-string fields (from review — regression/documentation tests)**
24. Note with `body=None` (if the schema allows it) and `query` provided → currently raises `AttributeError`; test should assert this current failure mode (or be updated once fixed) so a silent behavior change is caught.
25. Note with a `None` element inside `tags` and `tag` provided → currently raises `AttributeError`; same rationale as above.

**Return type / integrity**
26. Result list contains the actual note objects from the store (identity-preserving, e.g. `result[0] is original_note`), not copies.
27. Order of returned notes matches the order returned by `store.list()` (filtering doesn't reorder).

**Performance/hoisting regression guard (optional, from review)**
28. If `q = query.lower()` / `t = tag.lower()` are hoisted out of the loop as suggested, add a test with a custom `NoteStore`/mock whose notes assert `query`/`tag` aren't re-lowered per iteration (e.g. via a call-counting stand-in for `.lower()`) — mainly useful if the refactor is applied, to prevent regressing back into the loop.


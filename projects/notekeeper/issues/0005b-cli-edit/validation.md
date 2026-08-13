# Validation: Add edit subcommand to notekeeper CLI

## Code Review

## Review

**Unverified relative imports (cannot confirm against the real project):**
- `from .models import Note` — I cannot verify that `models.py` exists as a sibling file, that it defines `Note`, or that `Note.new(title, body, tags)` exists with this exact classmethod signature and returns an object exposing `.id`, `.title`, `.body`, `.tags`, `.created_at`. This must be checked against the actual `models.py`.
- `from .search import search_notes` — I cannot verify `search.py` exists or that `search_notes` takes positional arguments in the order `(store, query, tag)` as called in `_cmd_search`. If the real signature differs (e.g. keyword-only, different order), this call breaks at runtime.
- `from .store import NoteStore, NoteStoreError` — I cannot verify `store.py` exists or that `NoteStore` has a one-arg constructor taking a path, and methods `add`, `list`, `get`, `update(note_id, title=..., body=..., tags=...)`, and `delete` with these exact names/keyword args and return semantics (e.g., that `get`/`delete` return `None`/falsy on "not found" rather than raising). These are all assumptions baked into the CLI that must be checked against the real module.

**Exception handling gap.** `main()` only catches `NoteStoreError` around both store construction and `args.func(args, store)`. Any other exception — e.g. a `ValueError` raised by `Note.new` on invalid input, or an unexpected exception from `search_notes` — will propagate as a raw, unhandled traceback to the user instead of the clean `Error: ...` message the rest of the CLI is designed to produce. Since `Note.new`'s validation behavior is unverified (per above), this is a real risk, not just theoretical.

**`tags=None` vs `tags=[]` sentinel convention in `_cmd_edit`.** `tags = None if args.tags is None else _parse_tags(args.tags)` relies on `store.update` treating `None` as "leave tags unchanged" and `[]` (from `--tags ""`) as "clear all tags." This convention is never documented in this file and depends entirely on the unverified `NoteStore.update` implementation correctly distinguishing "not provided" from "provided but empty." If `update` instead treats `None` as "clear tags," editing a note without touching `--tags` would silently wipe its tags.

**Potential crash in `_cmd_show`.** `', '.join(note.tags)` assumes `note.tags` is always an iterable of strings (never `None`). Since `Note`'s definition is unverified, if tags can ever be `None` (e.g., on a malformed/legacy stored note), this raises a `TypeError`.

**Line-based output fragility.** `_format_note_line` joins `note.id` and `note.title` with a tab and relies on newline-per-record output (used by `list` and `search`). If a title can contain a tab or newline character (nothing here prevents that on `add`/`edit`), the output becomes ambiguous for any downstream script parsing it line-by-line. Minor, but worth a guard or explicit escaping if this output is meant to be machine-parsed.

**Dead/unused import.** `from __future__ import annotations` is imported, but no function in this file uses type annotations at all (`_parse_tags(raw)`, `_cmd_add(args, store)`, etc. are all unannotated). Either the annotations were intended and never added, or the import is vestigial — worth cleaning up either way.

**No case normalization on tags.** `_parse_tags` dedupes by exact string match only, so `"Work"` and `"work"` are treated as distinct tags. This may be intentional, but it's a plausible source of tag fragmentation if not deliberate.

**Minor: empty title/body not rejected.** `add` and `edit` accept empty-string `title`/`body` without validation at the CLI layer; whether that's acceptable depends entirely on the unverified `Note`/`NoteStore` validation, which isn't visible here.


## Test Execution

## Proposed test cases

**`--store` precedence (the bug this file was patched for)**
1. `notekeeper --store X.json add "t" "b"` → store path used is `X.json`.
2. `notekeeper add "t" "b" --store X.json` → store path used is `X.json`.
3. `notekeeper --store X.json add "t" "b" --store Y.json` → later value wins (`Y.json`).
4. `notekeeper add "t" "b"` (no `--store` anywhere) → falls back to default `"notes.json"`.
5. Same precedence checks repeated for at least one other subcommand (e.g. `list` or `delete`) to confirm `sub_store_parent`'s `SUPPRESS` default works uniformly, not just for `add`.

**`_parse_tags`**
6. `raw=None` → `[]`.
7. `raw=""` → `[]`.
8. `raw="a,b,c"` → `["a", "b", "c"]`.
9. `raw="a, b ,c"` (whitespace around entries) → `["a", "b", "c"]` (stripped).
10. `raw="a,a,b"` (exact duplicate) → `["a", "b"]` (order-preserving dedup).
11. `raw="a,,b"` (empty segment from double comma) → `["a", "b"]`.
12. `raw="a,A"` → `["a", "A"]` (case treated as distinct — documents current no-normalization behavior).
13. `raw=","` → `[]`.

**`_format_note_line`**
14. Note with normal title → `"{id}\t{title}"`.
15. Note with empty-string title → output is `"{id}\t"`.

**`add` command**
16. `add "Title" "Body"` with no `--tags` → note created with `tags=[]`; printed line is the note id; exit code 0.
17. `add "Title" "Body" --tags "x,y"` → note created with `tags=["x","y"]`.
18. `add` output on stdout is exactly the new note's `id` (nothing else).

**`list` command**
19. Empty store → `list` prints nothing, exit code 0.
20. Store with multiple notes → one line per note in the order `store.list()` returns them.

**`show` command**
21. Existing id → prints Title/Body/Tags/Created in that exact order/format, exit 0.
22. Tags formatted as comma-space-joined string, e.g. `Tags: x, y`.
23. Note with zero tags → `Tags: ` (empty after colon), no crash.
24. Nonexistent id → stderr message `Note not found: {id}`, exit code 1, nothing on stdout.

**`search` command**
25. `search "query"` with no `--tag` → calls `search_notes(store, query, None)` and prints matching lines.
26. `search` with no query (`nargs="?"`) and `--tag x` → query is `None`, tag filter applied.
27. `search` with neither query nor tag → both `None`, whatever `search_notes` defines as "match all"/"match none" is reflected in output.
28. No matches → prints nothing, exit code 0 (not treated as an error).

**`edit` command**
29. `edit ID --title "New"` (no `--body`, no `--tags`) → `store.update` called with `title="New", body=None, tags=None`.
30. `edit ID --tags "a,b"` → `tags=["a","b"]` passed through (not `None`).
31. `edit ID --tags ""` → `tags=[]` passed through (distinct from omitting `--tags` entirely) — directly tests the `None` vs `[]` sentinel convention flagged in the review.
32. `edit ID` with none of `--title/--body/--tags` given → all three passed as `None`.
33. Editing nonexistent id → stderr `Note not found: {note_id}`, exit code 1.
34. Successful edit → prints the note's id, exit 0.

**`delete` command**
35. Existing id → `store.delete` called, exit code 0, no stdout output.
36. Nonexistent id → stderr `Note not found: {id}`, exit code 1.

**Error handling**
37. `NoteStore(path)` constructor raises `NoteStoreError` → `main()` catches it, prints `Error: {e}` to stderr, returns 1 (not raised).
38. `args.func(args, store)` raises `NoteStoreError` mid-command → same catch/format/exit-1 behavior.
39. A non-`NoteStoreError` exception raised inside `args.func` (e.g. simulate with a monkeypatched command handler raising `ValueError`) propagates uncaught out of `main()` — documents current (arguably gap) behavior rather than asserting it's desired.

**Argument parsing / CLI-level**
40. No subcommand given → `argparse` errors (exit code 2, `required=True` on subparsers) rather than silently doing nothing.
41. Unknown subcommand → argparse error, exit code 2.
42. `-h`/`--help` at top level and at each subcommand level → exits 0 and shows help (basic smoke test that `parents=` wiring didn't break help text, e.g. `--store` appearing only once per subcommand, not duplicated/conflicting).
43. `search` called with a query string that looks like an option (e.g. `notekeeper search --tag work` with no positional query) doesn't misparse `--tag`'s value as the query.

**End-to-end `main(argv)` integration**
44. Full round trip: `main(["--store", tmp_path, "add", "T", "B", "--tags", "x"])` then `main(["--store", tmp_path, "list"])` against a real temp file — verifies id flows through and the store persists between invocations (exercises actual `NoteStore` rather than a mock, catching integration issues the review flagged as "unverified").
45. `main(None)` (reads `sys.argv`) at least doesn't crash when argv is monkeypatched to a valid command — sanity check on the `argv=None` default path.


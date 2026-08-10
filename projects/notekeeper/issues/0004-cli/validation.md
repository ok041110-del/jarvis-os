# Validation: Add a CLI to notekeeper

## Code Review

## Review

**Argument-order bug in the CLI structure.** `--store` is declared only on the top-level parser, before the subparsers are added. With `argparse`, global options defined on the parent parser must appear *before* the subcommand name — `notekeeper --store foo.json add "t" "b"` works, but the far more natural `notekeeper add "t" "b" --store foo.json` will fail with "unrecognized arguments." This is a common argparse footgun and will surprise users; either add `--store` to each subparser too, or clearly document the required ordering.

**Overly narrow exception handling in `main`.** Only `NoteStoreError` is caught around both `NoteStore(args.store)` construction and `args.func(args, store)`. Any other exception — a malformed JSON store file raising `json.JSONDecodeError`, a permissions error, a bug in `search_notes`, etc. — will propagate as a raw Python traceback instead of a clean CLI error message. For a user-facing CLI this is a real robustness risk; either broaden what's caught or ensure `NoteStore`/command functions never raise anything else.

**Delimiter injection in `_format_note_line`.** Output is built as `f"{note.id}\t{note.title}"` and printed one line per note. If a title contains a tab or newline character (nothing in `_cmd_add` prevents this), the tab-separated output for `list`/`search` becomes misaligned or spans extra lines, which is a problem if any downstream tooling parses this output.

**No input validation on `add`.** `args.title` and `args.body` are passed straight to `Note.new` with no check for empty/whitespace-only strings. Depending on what `Note.new` does, this could silently create junk notes with empty titles.

**Tag handling is case-sensitive and unnormalized.** `_parse_tags` dedupes exact string matches only, so `"Work"` and `"work"` are treated as distinct tags. Combined with `--tag` filtering in search (implementation not shown), this could easily lead to notes that "should" match a tag filter not being found. Worth confirming this is intentional rather than an oversight.

**Potential `None` tags in `_cmd_show`.** `', '.join(note.tags)` will raise `TypeError` if `note.tags` is ever `None` rather than an empty list. Depends on the `Note` model's guarantees, but there's no defensive handling here.

**Minor:** `NoteStore` is constructed unconditionally for every command, including read-only ones like `list`/`show`/`search`. If construction has side effects (e.g., creating the store file if missing), running `show` or `search` on a nonexistent store path would silently create an empty one — worth confirming that's desired behavior.


## Test Execution

## Proposed Test Cases

### `_parse_tags`
1. `None` input → returns `[]`
2. Empty string `""` → returns `[]`
3. Single tag, no commas → `["work"]`
4. Multiple tags: `"work,home,urgent"` → `["work", "home", "urgent"]`
5. Whitespace around tags: `" work , home "` → `["work", "home"]`
6. Duplicate tags preserved order, deduped: `"work,work,home"` → `["work", "home"]`
7. Case-sensitive duplicates NOT deduped: `"Work,work"` → `["Work", "work"]` (documents current case-sensitive behavior per review)
8. Empty segments skipped: `"work,,home,"` → `["work", "home"]`
9. All-empty/whitespace segments: `" , , "` → `[]`
10. Tag containing internal whitespace: `"my tag"` → `["my tag"]` (preserved, not split)

### `_format_note_line`
11. Normal title/id → `"{id}\t{title}"`
12. Title containing a tab character → verify output (documents/locks in current behavior, whether broken or fixed)
13. Title containing a newline character → verify output spans lines or is escaped
14. Empty-string title → `"{id}\t"`
15. Unicode title (emoji, non-ASCII) → renders correctly

### `_cmd_add`
16. Basic add: title + body, no tags → prints note id, note stored with empty tags list
17. Add with `--tags "a,b,c"` → note stored with parsed tag list
18. Add with empty-string title (`""`) → current behavior (creates note or rejects — pin down actual behavior)
19. Add with whitespace-only title (`"   "`) → current behavior
20. Add with empty-string body → succeeds, body stored as `""`
21. Return code is `0` on success
22. Printed id matches `note.id` exactly and is the only stdout content
23. Add then immediately `show` — round-trip verifies title/body/tags/created persisted correctly
24. Add with duplicate tags via `--tags` → stored tags deduped

### `_cmd_list`
25. Empty store → no output, return `0`
26. Single note → one formatted line printed
27. Multiple notes → one line per note, in the order `store.list()` returns
28. Return code always `0` regardless of note count

### `_cmd_show`
29. Existing id → prints Title/Body/Tags/Created in that exact order/format, returns `0`
30. Nonexistent id → prints `"Note not found: {id}"` to stderr, returns `1`, nothing on stdout
31. Note with empty tags list → `"Tags: "` (empty string after colon), no crash
32. Note with multiple tags → joined with `", "`
33. Note with a tag containing a comma → output ambiguity (documents current join behavior)
34. `note.tags is None` (if reachable via store/model) → confirm whether it raises `TypeError` or is guarded

### `_cmd_search`
35. Query matches multiple notes → each printed as formatted line
36. Query matches nothing → no output, return `0`
37. No query, no `--tag` (both `None`) → delegate behavior to `search_notes` (e.g., returns all notes)
38. Query only, no `--tag`
39. `--tag` only, no query
40. Both query and `--tag` combined
41. `--tag` filter case sensitivity — tag `"Work"` filtered by `--tag work` (per review, confirm mismatch behavior)
42. Query with special regex-like characters (`.`, `*`, `%`) doesn't crash if `search_notes` does substring/regex matching

### `_cmd_delete`
43. Existing id → deletes, returns `0`, no output
44. Nonexistent id → prints `"Note not found: {id}"` to stderr, returns `1`
45. Delete then `list`/`show` on same id → confirms note is actually gone
46. Delete twice on same id → second call returns `1` (not found)

### `build_parser` / argument parsing
47. `--store` before subcommand: `notekeeper --store foo.json add "t" "b"` → works, uses `foo.json`
48. `--store` after subcommand: `notekeeper add "t" "b" --store foo.json` → currently fails with argparse error (locks in the bug from the review; becomes a regression test once fixed)
49. No `--store` given → defaults to `"notes.json"`
50. No subcommand given → argparse errors (`required=True`) with nonzero exit
51. Unknown subcommand → argparse error, nonzero exit
52. `add` missing required `title`/`body` positional → argparse error
53. `show`/`delete` missing required `id` → argparse error
54. `search` with no positional query at all → `args.query is None`, doesn't error (since `nargs="?"`)

### `main` / top-level error handling
55. `NoteStore` construction raises `NoteStoreError` → caught, prints `"Error: {e}"` to stderr, returns `1`
56. Command function raises `NoteStoreError` mid-execution → caught, same formatted output, returns `1`
57. Store file contains malformed JSON → currently propagates as uncaught `json.JSONDecodeError` (documents the gap raised in review; should become "caught and returns 1" after a fix)
58. Store path points to a directory or unwritable location (permission error) → currently uncaught, propagates raw traceback
59. `main(argv=[...])` with explicit argv list works the same as reading `sys.argv`
60. `main()` return value is used as process exit code (e.g., via `sys.exit(main())`) — verify `0`/`1` returned, not raised

### Read-only commands and store side effects
61. Running `list`/`show`/`search` against a nonexistent store path — verify whether `NoteStore` construction creates the file as a side effect (per review's "minor" point); assert on file's existence/non-existence after the call

### End-to-end / integration
62. Full workflow: `add` → `list` shows it → `search` by query finds it → `search` by `--tag` finds it → `show` displays it → `delete` removes it → `list` no longer shows it → `show` returns not-found
63. Two notes added with same title but different bodies → both appear distinctly in `list` with different ids


# Validation: Add NoteStore (JSON-file persistence) to notekeeper

## Code Review

## Review

**Error-handling inconsistency vs. documented contract.** `NoteStoreError`'s docstring promises it's raised when the file is "missing, unreadable, or corrupted," but `load()` only wraps `json.JSONDecodeError` and `(KeyError, TypeError)` from `Note.from_dict`. A permission error, the path being a directory, or other `OSError` variants from `self.path.open()` will propagate as raw low-level exceptions instead of the documented `NoteStoreError`, which will surprise callers who catch only the latter.

**In-memory/disk inconsistency on save failure.** `add()` and `delete()` mutate `self._notes` *then* call `save()`. If `save()` raises partway (disk full, permission denied, non-serializable note content, missing parent directory, etc.), the in-memory dict has already diverged from what's on disk — the mutation isn't rolled back. A caller who catches the exception and continues using the store will now be operating on state that doesn't match the persisted file, and the next restart will silently lose or resurrect data.

**No concurrency protection.** There's no locking around either the in-memory dict or the file. Two `NoteStore` instances (or threads) pointed at the same path can race: both read the same on-disk state, both mutate their own in-memory copies, and whichever calls `save()` last wins — silently discarding the other's writes, since each `save()` does a full rewrite from its own `_notes` rather than merging. If this store is meant to be used from a multi-threaded/multi-process context (e.g., a web server), this is a real data-loss risk.

**Every mutation does a full synchronous rewrite.** `add()`/`delete()` each trigger a complete `json.dump` of the entire note collection plus an `os.replace`. For bulk operations (e.g., importing many notes) this is O(n²) disk I/O overall and could be a real performance bottleneck; there's no batch/bulk API or way to defer saving.

**Durability gap in `save()`.** The tmp file is written and closed, then `os.replace`d in — but there's no `f.flush()`/`os.fsync()` before the rename. The `open`/`write`/close sequence gets data into the OS buffer, not necessarily onto disk, so a crash or power loss between write and rename can still leave the store in an unexpected state despite the atomic-rename pattern. This weakens the "explicit disk synchronization" guarantee implied by the class docstring.

**Orphaned tmp file on partial failure.** If `json.dump` raises mid-write (e.g., a `Note.to_dict()` produces non-serializable content), `tmp_path` is left behind on disk with partial or no content and is never cleaned up.

**No validation of `note.id`.** `add()` uses `note.id` as the dict key unconditionally; duplicate, `None`, or empty-string IDs will silently overwrite existing notes with no warning or error, which could mask bugs upstream.

**Minor style note.** The `list()` method shadows the builtin `list` within the class namespace; harmless here since it's only accessed via `self.list(...)`/instance, but worth naming something like `all()` or `list_notes()` for clarity, especially since `list(...)` (the builtin) is also used inside the method body.


## Test Execution

## Proposed Test Cases for `NoteStore`

### Core CRUD behavior
1. **`test_add_persists_note_to_disk`** — add a note, create a new `NoteStore` on the same path, confirm the note is loaded back with identical fields.
2. **`test_add_overwrites_existing_note_with_same_id`** — add two notes sharing an `id`; confirm the second replaces the first (in memory and after reload).
3. **`test_get_returns_none_for_missing_id`** — `get()` on an empty/non-matching store returns `None`.
4. **`test_get_returns_correct_note`** — add multiple notes, verify `get()` returns the right one by id.
5. **`test_delete_returns_true_and_removes_note`** — add then delete; `delete()` returns `True`, `get()` afterward returns `None`, and the note is absent after reload from disk.
6. **`test_delete_returns_false_for_missing_id`** — deleting a nonexistent id returns `False` and leaves the store/file unchanged.
7. **`test_list_returns_all_notes`** — add several notes, confirm `list()` contains exactly them (order-insensitive check or documented order).
8. **`test_list_empty_store`** — `list()` on a fresh store returns `[]`.

### Initialization / load behavior
9. **`test_init_with_nonexistent_path_starts_empty`** — constructing with a path that doesn't exist yields an empty store and does not create the file until `save()`/`add()` is called.
10. **`test_init_with_existing_valid_file_loads_notes`** — pre-write a valid JSON note list, construct `NoteStore`, confirm notes are loaded.
11. **`test_load_with_empty_json_array`** — file containing `[]` loads to an empty store without error.
12. **`test_load_raises_notestoreerror_on_invalid_json`** — file with malformed JSON (`"{not json"`) raises `NoteStoreError` on construction/`load()`.
13. **`test_load_raises_notestoreerror_on_missing_required_fields`** — JSON array with an item missing a required `Note` field raises `NoteStoreError` (covers `KeyError`).
14. **`test_load_raises_notestoreerror_on_wrong_item_type`** — JSON array containing a non-dict item (e.g. a string or int) raises `NoteStoreError` (covers `TypeError`).
15. **`test_load_raises_on_json_top_level_not_a_list`** — file containing a valid JSON object/scalar instead of a list (e.g. `{}` or `42`) — confirm current behavior (does it raise `NoteStoreError`, or some other error/silently misbehave?).
16. **`test_load_replaces_rather_than_merges_in_memory_state`** — populate `_notes` in memory, call `load()` again with different on-disk content, confirm in-memory state is fully replaced, not merged.

### `save()` mechanics
17. **`test_save_writes_valid_json_matching_notes`** — call `save()` directly, read the file back with `json.load`, confirm structure/content matches `to_dict()` output of all notes.
18. **`test_save_is_atomic_no_leftover_tmp_file_on_success`** — after a normal `save()`, confirm no `*.tmp` file remains alongside the target file.
19. **`test_save_overwrites_existing_file_completely`** — pre-populate file with notes A, B; store only has note C; `save()` results in a file containing only C (full rewrite, not merge).
20. **`test_save_creates_parent_file_if_missing`** — path's file doesn't exist yet; `save()` creates it.
21. **`test_save_with_empty_notes_writes_empty_array`** — deleting all notes then saving results in `[]` on disk.

### Round-trip fidelity
22. **`test_round_trip_preserves_unicode_content`** — note with non-ASCII/emoji content survives save/load unchanged (`ensure_ascii=False` behavior).
23. **`test_round_trip_multiple_notes_preserves_all_fields`** — add several distinct notes with varied field values, reload, assert full equality.

### Sequencing / multiple operations
24. **`test_multiple_adds_then_deletes_converge_to_expected_state`** — interleave several `add`/`delete` calls, confirm final `list()` and on-disk state match expectations.
25. **`test_reinitializing_store_reflects_latest_saved_state`** — after several operations on one `NoteStore` instance, construct a second instance on the same path and confirm it sees the up-to-date state.

### Failure-path / edge behavior called out by the review (documenting current, possibly undesired, behavior)
26. **`test_load_raises_raw_oserror_on_permission_denied`** — file exists but is unreadable (chmod 000); confirm what's actually raised (currently an uncaught `OSError`, not `NoteStoreError`) — locks in current behavior or catches a regression once fixed.
27. **`test_load_raises_when_path_is_a_directory`** — `self.path` points at a directory; confirm current raised exception type.
28. **`test_add_leaves_memory_ahead_of_disk_when_save_fails`** — monkeypatch/force `save()` to raise (e.g. non-serializable note content, or patch `json.dump` to raise); confirm `_notes` still contains the added note even though the file wasn't updated (documents the in-memory/disk divergence).
29. **`test_delete_leaves_memory_ahead_of_disk_when_save_fails`** — same as above but for `delete()`: force `save()` to fail after removal, confirm note is gone from `_notes` but still present on disk.
30. **`test_save_failure_leaves_orphaned_tmp_file`** — force `json.dump` to raise partway (e.g. a note whose `to_dict()` returns non-serializable data), confirm a `*.tmp` file is left on disk and the original file is untouched.
31. **`test_add_with_duplicate_id_silently_overwrites`** — construct two distinct `Note` objects sharing an `id`, add both, confirm the second silently replaces the first with no error/warning.
32. **`test_add_with_empty_string_id`** — add a note with `id=""`; confirm it's stored/retrievable under that key (documents current unvalidated behavior).
33. **`test_add_with_none_id_raises_or_stores_under_none`** — add a note whose `id` is `None`; confirm/document what happens (TypeError from dict key use elsewhere? silently stored under key `None`?).

### Concurrency (documenting the known gap)
34. **`test_concurrent_stores_last_writer_wins_and_drops_other_writes`** — open two `NoteStore` instances on the same path, add different notes to each without reloading between, save both; confirm the second `save()` silently discards the first instance's notes (demonstrates the lost-update race named in the review).

### Performance/API shape (lower priority, optional)
35. **`test_bulk_add_triggers_save_per_call`** — spy/count calls to `save()` (or file mtime/write count) while adding N notes, confirming one full rewrite per `add()` — documents the O(n²) behavior rather than asserting it's desirable.

---
Items 26–35 are primarily **characterization tests** — they lock in and document the current behavior the review flagged as problematic (inconsistent error types, memory/disk divergence, no dup-id validation, no concurrency safety), rather than asserting it's correct. If those issues get fixed, these tests should be updated to assert the corrected behavior instead.


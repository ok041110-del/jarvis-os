# Planning: Add update() to NoteStore

## Requirement Analysis: Add `update()` to `NoteStore`

**Goal**
Extend `notekeeper`'s `NoteStore` (in `src/notekeeper/store.py`) with an in-place edit capability. Callers should be able to patch a note's `title`, `body`, and/or `tags` by `note_id`, with the change persisted to disk, without touching any of the six existing methods (`__init__`, `add`, `get`, `delete`, `list`, `save`, `load`) — those must remain byte-for-byte unchanged.

**Scope**
- One new public method: `update(note_id: str, title: str | None = None, body: str | None = None, tags: list[str] | None = None) -> Note | None`.
- Lookup: if `note_id` is absent from `self._notes`, return `None` and leave state and disk file untouched (no save call).
- Partial update semantics: only the fields passed as non-`None` are overwritten; any field left as `None` retains its current value. This means there's no way to explicitly clear a field to empty/`None` via this API — a caller wanting to blank out `body`, for instance, cannot distinguish "leave as-is" from "set to empty" unless an empty string is treated as a valid non-`None` value (which it is, per the signature).
- Immutable fields: `id` and `created_at` must never change, regardless of input.
- Persistence: on a successful update, the in-memory `Note` is replaced/mutated and `self.save()` is called so the change is flushed to the backing JSON file (mirroring the pattern in `add`/`delete`).
- Return value: the updated `Note` instance on success.

**Design questions the implementer will need to resolve (not specified by the issue)**
1. Whether `Note` is a mutable class (in-place field assignment) or frozen/immutable (e.g., a frozen dataclass requiring `dataclasses.replace` or reconstruction) — this isn't shown in the excerpt and determines the implementation shape. Need to check `models.py`.
2. Whether an `updated_at`/`modified_at` timestamp field exists on `Note` and should be refreshed — the issue doesn't mention one, so absent evidence in `models.py`, it should likely be left alone (not invented).
3. No validation rules are specified for `title`/`body`/`tags` (e.g., empty string, empty list) — the issue implies none beyond "if not None, use it," so no extra validation should be added.

**Risks**
- Accidentally modifying one of the frozen six methods while adding the new one (the issue explicitly forbids this — a diff review should confirm only additive changes).
- If `Note` is immutable, a naive attempt to mutate its fields directly will fail at runtime; the fix must construct a new `Note` (preserving `id`/`created_at`) and reassign it into `self._notes[note_id]`.
- Partial-update-via-`None`-sentinel is inherently unable to represent "explicitly set to empty," which is a known limitation of this signature style but matches what was requested — worth flagging, not solving unilaterally.
- `save()` writes the whole store atomically (temp file + `os.replace`), so the persistence risk is low, but the update must mutate the dict entry before calling `save()`, or the write will silently persist stale data.


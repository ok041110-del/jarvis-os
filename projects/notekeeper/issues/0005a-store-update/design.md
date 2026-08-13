# Design: Add update() to NoteStore

## Design: `NoteStore.update()`

**Approach**

Add `update()` as a new method on `NoteStore`, positioned after the existing six methods so the diff is purely additive. It follows the same request → mutate-in-memory → persist pattern already used by `add`/`delete`:

1. **Lookup.** Check `note_id in self._notes` (or use `.get()` and check for `None`). If absent, return `None` immediately — no mutation, no `save()` call. This is the single early-exit branch.
2. **Merge fields.** For each of `title`, `body`, `tags`, use the incoming value if it is not `None`, otherwise fall back to the existing value on the stored `Note`. This is a straightforward `new_value = param if param is not None else existing.field` for each of the three mutable fields.
3. **Reconstruct or mutate.** Depending on how `Note` is defined in `models.py`:
   - If `Note` is a plain/mutable class or a non-frozen dataclass, assign the merged fields directly onto the existing instance (`note.title = ...`, etc.), leaving `id` and `created_at` untouched by simply never writing to them.
   - If `Note` is a frozen dataclass (or otherwise immutable), build a replacement via `dataclasses.replace(existing, title=new_title, body=new_body, tags=new_tags)`, which by construction carries over every field not explicitly overridden — so `id` and `created_at` are preserved automatically. Reassign the result into `self._notes[note_id]`.

   This is the one branch point genuinely uncertain from the issue text alone; it should be resolved by reading `models.py` before writing code, not guessed.
4. **Persist.** Call `self.save()` after the in-memory state reflects the change, mirroring `add`/`delete`. Since `save()` presumably serializes the full `self._notes` mapping atomically, correctness here just requires that the dict entry is updated *before* `save()` runs.
5. **Return.** Return the updated `Note` instance.

**Responsibilities**

- `update()` owns: lookup, partial-merge logic, immutability of `id`/`created_at`, and triggering persistence.
- It explicitly does *not* own: validation of field contents (no rules specified — don't invent any), timestamp bookkeeping (no `updated_at` field evidenced in `models.py` — don't invent one), or any change to serialization/`save()`/`load()` internals.
- No new helper methods or abstractions are needed for a single merge-and-persist operation — inlining the three-field merge directly in `update()` is proportionate to the task; a generic "patch" helper would be premature.

**Risks**

- **Touching the frozen six.** The strongest constraint in the issue is that `add`, `get`, `delete`, `list`, `save`, `load`, and `__init__` stay byte-for-byte identical. The implementation must be self-contained within the new method, with zero incidental reformatting of neighboring code (e.g. import ordering, blank lines). Worth a diff review before finishing.
- **Wrong mutability assumption.** Guessing `Note`'s shape instead of reading `models.py` risks either an `AttributeError` (assigning to a frozen dataclass field) or writing unnecessary reconstruction code for a mutable class. This should be checked first, not inferred from the issue text.
- **Save-before-mutate ordering bug.** Since `save()` likely dumps the entire `self._notes` state, calling it before the dict entry is updated would silently persist the old note with no error — an easy but hard-to-notice mistake.
- **`None`-as-sentinel limitation.** Because `None` means "leave unchanged," there is no way for a caller to intentionally blank a field (e.g., clear `body` to `""` is fine since `""` is not `None`, but there's no way to distinguish "don't touch tags" from "set tags to `[]`" — actually `[]` is also non-`None` so it's fine; the real gap is only for fields where the caller might want to set the value to `None` itself, which doesn't apply here since none of `title`/`body`/`tags` are `Optional` in the domain model). This is inherent to the requested signature and shouldn't be "fixed" unilaterally (e.g., by adding sentinel objects) without the requester asking for it.
- **Aliasing on `tags`.** If a mutable list is passed in and stored by reference rather than copied, later external mutation of the caller's list would silently alter store state. Whether to defensively copy (`list(tags)`) depends on conventions already established in `add()` — should match whatever `add()` does with `tags`, not introduce a new convention.


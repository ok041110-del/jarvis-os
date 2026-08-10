# Validation: Add Note data model to notekeeper

## Code Review

## Issues found

**Critical bug — class won't even load.** In the `Note` dataclass, `tags: list = field(default_factory=list)` (a field with a default) appears before `created_at: str` (a field without a default). Standard `dataclass` field ordering requires all fields without defaults to precede fields with defaults; as written this raises `TypeError: non-default argument 'created_at' follows default argument` the moment the module is imported. Either move `created_at` above `tags`, or give `tags` a keyword-only/last position.

**Unused import.** `Any` from `typing` is imported but never referenced anywhere in the file.

**Weakly-typed collection field.** `tags: list` uses the bare `list` type instead of something like `list[str]`, so type checkers get no element-type information despite the class otherwise using string-typed fields consistently.

**`from_dict` has no defensive handling.** It indexes `data["id"]`, `data["title"]`, etc. directly, so any missing key raises a raw `KeyError` with no context about which field was absent or that deserialization failed. There's also no type/format validation on `created_at` (e.g., that it's a valid ISO-8601 string) or on `tags` (e.g., that it's actually a list of strings rather than some other iterable of arbitrary objects) — malformed input dicts will silently produce a `Note` with bad data until something downstream trips on it.

**`created_at` stored as `str` rather than `datetime`.** This pushes parsing/timezone-awareness responsibility onto every caller that wants to do date arithmetic or comparisons, and nothing enforces that a manually constructed `Note` (bypassing `.new()`) has a valid ISO timestamp in that field.

**No validation in `new`/`__init__`.** `title`/`body` can be empty strings or non-string objects with no complaint, and `tags` isn't checked to ensure its elements are strings — `list(tags)` will happily wrap any iterable of any element type.


## Test Execution

## Proposed Test Cases for `Note`

### Construction / field ordering (regression guard for the critical bug)
1. **Module import succeeds** — `import` the module / instantiate `Note` with all fields positionally and by keyword; asserts the dataclass definition itself doesn't raise `TypeError` at class-creation time (guards against the non-default-after-default regression resurfacing).
2. **Positional and keyword instantiation both work** — construct `Note("id1", "t", "b", ["x"], "2026-08-10T00:00:00+00:00")` and again with all-keyword args; both should produce equal objects.

### `Note.new()`
3. **Creates a valid UUID `id`** — `Note.new("t", "b")`; assert `uuid.UUID(note.id)` doesn't raise.
4. **Two calls to `new()` produce distinct ids** — no collision on repeated calls.
5. **`created_at` is a valid ISO-8601 UTC string** — assert `datetime.fromisoformat(note.created_at)` parses and `.tzinfo` is not `None`.
6. **`created_at` is monotonically increasing (or equal) across sequential calls** — `Note.new(...)` twice, assert the second timestamp isn't earlier than the first.
7. **`tags=None` (default) yields `[]`**, not `None`.
8. **`tags` passed as a list is copied, not aliased** — pass a list, mutate the original after construction, assert `note.tags` is unaffected (and vice versa).
9. **`tags` accepts arbitrary iterables** (tuple, generator, set) and converts them to a `list`.
10. **Empty `title`/`body` strings are accepted** (documents current permissive behavior — no validation exists yet).

### `to_dict()`
11. **Round-trips all five fields with correct keys** — `to_dict()` on a `Note.new(...)` result contains exactly `id, title, body, tags, created_at` with matching values.
12. **Returned `tags` list is a copy** — mutate the dict's `"tags"` after calling `to_dict()`, assert `note.tags` is unchanged.
13. **`to_dict()` output is JSON-serializable** — `json.dumps(note.to_dict())` doesn't raise (guards the value-object's main use case).

### `from_dict()`
14. **Round-trip identity**: `Note.from_dict(note.to_dict()) == note` for a `Note.new(...)` instance.
15. **Round-trip identity for a hand-built dict** with arbitrary `id`/`created_at` strings.
16. **Missing required key raises `KeyError`** — separately omit each of `id`, `title`, `body`, `tags`, `created_at` and assert a `KeyError` is raised (documents current behavior; also the seam to re-target if the review's suggested wrapping/validation is added later).
17. **`tags` value that's a tuple/set is converted to a `list`** on the resulting `Note`.
18. **`tags` value that's not iterable (e.g. `None` or an `int`) raises `TypeError`** — documents current unguarded `list(data["tags"])` behavior.
19. **Extra/unexpected keys in the input dict are ignored** without error.
20. **Resulting `tags` is an independent copy** of the input dict's list (mutate input after call, assert `note.tags` unaffected).

### Equality / dataclass behavior
21. **Two `Note`s with identical field values compare equal** (`__eq__` from `@dataclass`).
22. **Two `Note`s differing only in `tags` order or content compare unequal**.


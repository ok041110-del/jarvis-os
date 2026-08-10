# Implementation: Add search_notes() to notekeeper

실제 저장 위치: `src/notekeeper/search.py`

```python
"""Stateless filtering over a NoteStore."""

from notekeeper.store import NoteStore


def search_notes(store: NoteStore, query: str | None = None, tag: str | None = None) -> list:
    results = []
    for note in store.list():
        if query is not None:
            q = query.lower()
            if q not in note.title.lower() and q not in note.body.lower():
                continue
        if tag is not None:
            t = tag.lower()
            if not any(t == existing.lower() for existing in note.tags):
                continue
        results.append(note)
    return results
```

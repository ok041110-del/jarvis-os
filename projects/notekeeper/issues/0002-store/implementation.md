# Implementation: Add NoteStore (JSON-file persistence) to notekeeper

실제 저장 위치: `src/notekeeper/store.py`

**참고**: 아래는 최초 Implementation 산출물이다(역사적 기록, 수정하지
않음). 실제 결함(잘못된 import 대상, 부모 디렉토리 미생성)과 그
수정은 `fix-cycle.md`에 기록되어 있다 — 실제 최종 코드는
`fix-cycle.md`가 기술하는 버전이다.

```python
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, Union

from .note import Note


class NoteStoreError(Exception):
    """Raised when the note store's backing file is missing, unreadable, or corrupted."""


class NoteStore:
    """In-memory cache of Note objects with explicit disk synchronization."""

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        self._notes: dict[str, Note] = {}
        if self.path.exists():
            self.load()

    def add(self, note: Note) -> None:
        self._notes[note.id] = note
        self.save()

    def get(self, note_id: str) -> Optional[Note]:
        return self._notes.get(note_id)

    def delete(self, note_id: str) -> bool:
        if note_id not in self._notes:
            return False
        del self._notes[note_id]
        self.save()
        return True

    def list(self) -> list[Note]:
        return list(self._notes.values())

    def save(self) -> None:
        data = [note.to_dict() for note in self._notes.values()]
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.path)

    def load(self) -> None:
        with self.path.open("r", encoding="utf-8") as f:
            try:
                raw = json.load(f)
            except json.JSONDecodeError as e:
                raise NoteStoreError(f"Corrupted note store file: {self.path}") from e

        notes: dict[str, Note] = {}
        try:
            for item in raw:
                note = Note.from_dict(item)
                notes[note.id] = note
        except (KeyError, TypeError) as e:
            raise NoteStoreError(f"Corrupted note store file: {self.path}") from e

        self._notes = notes
```

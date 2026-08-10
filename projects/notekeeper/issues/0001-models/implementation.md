# Implementation: Add Note data model to notekeeper

실제 저장 위치: `src/notekeeper/models.py`

**참고**: 아래는 최초 Implementation 산출물이다(역사적 기록, 수정하지
않음). real Review가 찾은 실제 결함(dataclass 필드 순서 — import 자체가
실패)과 그 수정은 `fix-cycle.md`에 기록되어 있다 — 실제 최종 코드는
`fix-cycle.md`가 기술하는 버전이다.

```python
"""Value object for a single note, with dict round-trip serialization."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class Note:
    id: str
    title: str
    body: str
    tags: list = field(default_factory=list)
    created_at: str

    @classmethod
    def new(cls, title, body, tags=None):
        return cls(
            id=str(uuid4()),
            title=title,
            body=body,
            tags=list(tags) if tags is not None else [],
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "tags": list(self.tags),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            body=data["body"],
            tags=list(data["tags"]),
            created_at=data["created_at"],
        )
```

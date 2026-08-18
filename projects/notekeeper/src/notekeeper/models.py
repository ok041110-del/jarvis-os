from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Note:
    id: str
    title: str
    body: str
    created_at: str
    tags: list = field(default_factory=list)

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

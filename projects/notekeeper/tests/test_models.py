import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from notekeeper.models import Note


def test_new_generates_uuid_id():
    import uuid

    note = Note.new("Title", "Body")
    uuid.UUID(note.id)  # does not raise


def test_new_ids_are_distinct():
    a = Note.new("t", "b")
    b = Note.new("t", "b")
    assert a.id != b.id


def test_new_created_at_is_valid_iso8601_utc():
    note = Note.new("t", "b")
    parsed = datetime.fromisoformat(note.created_at)
    assert parsed.tzinfo is not None


def test_new_defaults_tags_to_empty_list():
    note = Note.new("t", "b")
    assert note.tags == []


def test_new_tags_not_shared_between_instances():
    a = Note.new("t", "b")
    b = Note.new("t", "b")
    a.tags.append("x")
    assert b.tags == []


def test_new_copies_passed_tags_list():
    original = ["a", "b"]
    note = Note.new("t", "b", tags=original)
    original.append("c")
    assert note.tags == ["a", "b"]


def test_to_dict_has_expected_keys():
    note = Note.new("Title", "Body", tags=["x"])
    d = note.to_dict()
    assert set(d.keys()) == {"id", "title", "body", "tags", "created_at"}


def test_to_dict_is_json_serializable():
    import json

    note = Note.new("Title", "Body", tags=["x"])
    json.dumps(note.to_dict())  # does not raise


def test_from_dict_round_trip():
    note = Note.new("Title", "Body", tags=["x", "y"])
    restored = Note.from_dict(note.to_dict())
    assert restored == note


def test_from_dict_missing_key_raises_keyerror():
    import pytest

    data = {"id": "1", "title": "t", "body": "b", "tags": []}  # missing created_at
    with pytest.raises(KeyError):
        Note.from_dict(data)

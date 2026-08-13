import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from notekeeper.models import Note
from notekeeper.store import NoteStore, NoteStoreError


def test_init_with_nonexistent_path_starts_empty(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    assert store.list() == []


def test_add_persists_and_reloads(tmp_path):
    path = tmp_path / "notes.json"
    store = NoteStore(path)
    note = Note.new("Title", "Body")
    store.add(note)

    reloaded = NoteStore(path)
    assert reloaded.get(note.id) == note


def test_get_returns_none_for_missing_id(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    assert store.get("does-not-exist") is None


def test_delete_returns_true_and_removes(tmp_path):
    path = tmp_path / "notes.json"
    store = NoteStore(path)
    note = Note.new("Title", "Body")
    store.add(note)

    assert store.delete(note.id) is True
    assert store.get(note.id) is None
    assert NoteStore(path).get(note.id) is None


def test_delete_returns_false_for_missing_id(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    assert store.delete("does-not-exist") is False


def test_list_returns_all_added_notes(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    a = Note.new("A", "a")
    b = Note.new("B", "b")
    store.add(a)
    store.add(b)
    assert {n.id for n in store.list()} == {a.id, b.id}


def test_add_overwrites_existing_id(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    note = Note.new("A", "a")
    store.add(note)
    note.title = "Changed"
    store.add(note)
    assert len(store.list()) == 1
    assert store.get(note.id).title == "Changed"


def test_corrupted_json_raises_notestoreerror(tmp_path):
    path = tmp_path / "notes.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(NoteStoreError):
        NoteStore(path)


def test_malformed_entry_raises_notestoreerror(tmp_path):
    import json

    path = tmp_path / "notes.json"
    path.write_text(json.dumps([{"id": "1"}]), encoding="utf-8")  # missing required fields
    with pytest.raises(NoteStoreError):
        NoteStore(path)


def test_save_creates_missing_parent_directories(tmp_path):
    path = tmp_path / "sub" / "dir" / "notes.json"
    store = NoteStore(path)
    store.add(Note.new("A", "a"))
    assert path.exists()


def test_empty_json_array_loads_to_empty_store(tmp_path):
    path = tmp_path / "notes.json"
    path.write_text("[]", encoding="utf-8")
    store = NoteStore(path)
    assert store.list() == []


def test_update_missing_id_returns_none(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    assert store.update("does-not-exist", title="x") is None


def test_update_only_title(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    note = Note.new("Title", "Body", tags=["a"])
    store.add(note)

    updated = store.update(note.id, title="New Title")
    assert updated.title == "New Title"
    assert updated.body == "Body"
    assert updated.tags == ["a"]


def test_update_only_body(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    note = Note.new("Title", "Body")
    store.add(note)

    updated = store.update(note.id, body="New Body")
    assert updated.title == "Title"
    assert updated.body == "New Body"


def test_update_only_tags(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    note = Note.new("Title", "Body", tags=["a"])
    store.add(note)

    updated = store.update(note.id, tags=["x", "y"])
    assert updated.tags == ["x", "y"]
    assert updated.title == "Title"


def test_update_no_fields_leaves_note_unchanged(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    note = Note.new("Title", "Body", tags=["a"])
    store.add(note)

    updated = store.update(note.id)
    assert updated.title == "Title"
    assert updated.body == "Body"
    assert updated.tags == ["a"]


def test_update_never_changes_id_or_created_at(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    note = Note.new("Title", "Body")
    store.add(note)

    updated = store.update(note.id, title="New Title")
    assert updated.id == note.id
    assert updated.created_at == note.created_at


def test_update_persists_to_disk(tmp_path):
    path = tmp_path / "notes.json"
    store = NoteStore(path)
    note = Note.new("Title", "Body")
    store.add(note)
    store.update(note.id, title="New Title")

    reloaded = NoteStore(path)
    assert reloaded.get(note.id).title == "New Title"

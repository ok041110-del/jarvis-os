import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from notekeeper.models import Note
from notekeeper.store import NoteStore
from notekeeper.search import search_notes


def _make_store(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    store.add(Note.new("Buy milk", "Remember to buy milk", tags=["errand"]))
    store.add(Note.new("Project plan", "Draft the Q3 project plan", tags=["work"]))
    store.add(Note.new("Meeting notes", "Notes from the milk industry meeting", tags=["work"]))
    return store


def test_no_filters_returns_all(tmp_path):
    store = _make_store(tmp_path)
    assert len(search_notes(store)) == 3


def test_query_matches_title(tmp_path):
    store = _make_store(tmp_path)
    results = {n.title for n in search_notes(store, query="milk")}
    assert results == {"Buy milk", "Meeting notes"}


def test_query_is_case_insensitive(tmp_path):
    store = _make_store(tmp_path)
    results = {n.title for n in search_notes(store, query="MILK")}
    assert results == {"Buy milk", "Meeting notes"}


def test_query_no_match_returns_empty(tmp_path):
    store = _make_store(tmp_path)
    assert search_notes(store, query="nomatch") == []


def test_tag_filter_exact_match(tmp_path):
    store = _make_store(tmp_path)
    results = {n.title for n in search_notes(store, tag="work")}
    assert results == {"Project plan", "Meeting notes"}


def test_tag_filter_is_case_insensitive(tmp_path):
    store = _make_store(tmp_path)
    results = {n.title for n in search_notes(store, tag="WORK")}
    assert results == {"Project plan", "Meeting notes"}


def test_tag_no_partial_match(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    store.add(Note.new("A", "a", tags=["work-related"]))
    assert search_notes(store, tag="work") == []


def test_query_and_tag_combined_is_and(tmp_path):
    store = _make_store(tmp_path)
    results = {n.title for n in search_notes(store, query="milk", tag="work")}
    assert results == {"Meeting notes"}


def test_empty_store_returns_empty(tmp_path):
    store = NoteStore(tmp_path / "notes.json")
    assert search_notes(store) == []

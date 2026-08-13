import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from notekeeper import cli
from notekeeper.store import NoteStore


def test_add_prints_id_and_persists(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    rc = cli.main(["add", "Hello", "World", "--store", store_path])
    assert rc == 0
    note_id = capsys.readouterr().out.strip()

    store = NoteStore(store_path)
    assert store.get(note_id).title == "Hello"


def test_store_option_works_before_subcommand(tmp_path, capsys):
    """Regression: real Fix Cycle round 2 introduced (and this fixed) a
    bug where `--store PATH` given BEFORE the subcommand silently
    reverted to the default "notes.json" instead of using PATH."""
    store_path = str(tmp_path / "notes.json")
    rc = cli.main(["--store", store_path, "add", "Hello", "World"])
    assert rc == 0
    note_id = capsys.readouterr().out.strip()

    store = NoteStore(store_path)
    assert store.get(note_id) is not None


def test_store_option_works_after_subcommand(tmp_path, capsys):
    """Regression: `--store PATH` given AFTER the subcommand
    (`add ... --store PATH`) must also work — this was the original
    real bug found by Review before any fix."""
    store_path = str(tmp_path / "notes.json")
    rc = cli.main(["add", "Hello", "World", "--store", store_path])
    assert rc == 0
    capsys.readouterr()
    store = NoteStore(store_path)
    assert len(store.list()) == 1


def test_show_prints_created_at_without_crashing(tmp_path, capsys):
    """Regression: real Fix Cycle found `_cmd_show` referenced
    `note.created` (AttributeError) instead of `note.created_at`."""
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "Hello", "World", "--store", store_path])
    note_id = capsys.readouterr().out.strip()

    rc = cli.main(["show", note_id, "--store", store_path])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Created:" in out
    assert "Title: Hello" in out
    assert "Body: World" in out


def test_show_missing_id_errors_cleanly(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    rc = cli.main(["show", "does-not-exist", "--store", store_path])
    err = capsys.readouterr().err
    assert rc == 1
    assert "Note not found" in err


def test_list_shows_all_notes(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "A", "a", "--store", store_path])
    capsys.readouterr()
    cli.main(["add", "B", "b", "--store", store_path])
    capsys.readouterr()

    rc = cli.main(["list", "--store", store_path])
    out = capsys.readouterr().out
    assert rc == 0
    assert "A" in out and "B" in out


def test_search_delegates_to_search_notes(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "Buy milk", "body", "--tags", "errand", "--store", store_path])
    capsys.readouterr()
    cli.main(["add", "Other", "body", "--store", store_path])
    capsys.readouterr()

    rc = cli.main(["search", "milk", "--store", store_path])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Buy milk" in out
    assert "Other" not in out


def test_delete_success_and_missing(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "A", "a", "--store", store_path])
    note_id = capsys.readouterr().out.strip()

    rc = cli.main(["delete", note_id, "--store", store_path])
    capsys.readouterr()
    assert rc == 0

    rc2 = cli.main(["delete", note_id, "--store", store_path])
    err = capsys.readouterr().err
    assert rc2 == 1
    assert "Note not found" in err


def test_add_with_tags(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "A", "a", "--tags", "x,y,x", "--store", store_path])
    note_id = capsys.readouterr().out.strip()

    store = NoteStore(store_path)
    assert store.get(note_id).tags == ["x", "y"]


def test_missing_subcommand_raises_systemexit(tmp_path):
    import pytest

    with pytest.raises(SystemExit):
        cli.main(["--store", str(tmp_path / "notes.json")])


def test_edit_updates_title_and_prints_id(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "Original", "body", "--store", store_path])
    note_id = capsys.readouterr().out.strip()

    rc = cli.main(["edit", note_id, "--title", "Edited", "--store", store_path])
    printed_id = capsys.readouterr().out.strip()
    assert rc == 0
    assert printed_id == note_id
    assert NoteStore(store_path).get(note_id).title == "Edited"


def test_edit_missing_id_errors_cleanly(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    rc = cli.main(["edit", "does-not-exist", "--title", "x", "--store", store_path])
    err = capsys.readouterr().err
    assert rc == 1
    assert "Note not found" in err


def test_edit_without_tags_leaves_tags_unchanged(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "A", "a", "--tags", "x,y", "--store", store_path])
    note_id = capsys.readouterr().out.strip()

    cli.main(["edit", note_id, "--title", "New", "--store", store_path])
    capsys.readouterr()
    assert NoteStore(store_path).get(note_id).tags == ["x", "y"]


def test_edit_with_tags_replaces_tags(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "A", "a", "--tags", "x,y", "--store", store_path])
    note_id = capsys.readouterr().out.strip()

    cli.main(["edit", note_id, "--tags", "z", "--store", store_path])
    capsys.readouterr()
    assert NoteStore(store_path).get(note_id).tags == ["z"]


def test_edit_store_option_works_before_and_after_subcommand(tmp_path, capsys):
    store_path = str(tmp_path / "notes.json")
    cli.main(["add", "A", "a", "--store", store_path])
    note_id = capsys.readouterr().out.strip()

    rc1 = cli.main(["--store", store_path, "edit", note_id, "--title", "T1"])
    capsys.readouterr()
    rc2 = cli.main(["edit", note_id, "--title", "T2", "--store", store_path])
    capsys.readouterr()
    assert rc1 == 0 and rc2 == 0
    assert NoteStore(store_path).get(note_id).title == "T2"

"""Command-line interface for notekeeper."""

from __future__ import annotations

import argparse
import sys

from .models import Note
from .search import search_notes
from .store import NoteStore, NoteStoreError


def _parse_tags(raw):
    if raw is None:
        return []
    seen = set()
    tags = []
    for part in raw.split(","):
        tag = part.strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags


def _format_note_line(note):
    return f"{note.id}\t{note.title}"


def _cmd_add(args, store):
    tags = _parse_tags(args.tags)
    note = Note.new(args.title, args.body, tags)
    store.add(note)
    print(note.id)
    return 0


def _cmd_list(args, store):
    for note in store.list():
        print(_format_note_line(note))
    return 0


def _cmd_show(args, store):
    note = store.get(args.id)
    if note is None:
        print(f"Note not found: {args.id}", file=sys.stderr)
        return 1
    print(f"Title: {note.title}")
    print(f"Body: {note.body}")
    print(f"Tags: {', '.join(note.tags)}")
    print(f"Created: {note.created_at}")
    return 0


def _cmd_search(args, store):
    for note in search_notes(store, args.query, args.tag):
        print(_format_note_line(note))
    return 0


def _cmd_delete(args, store):
    if not store.delete(args.id):
        print(f"Note not found: {args.id}", file=sys.stderr)
        return 1
    return 0


def build_parser():
    # Real execution found that giving every subparser its own `--store`
    # via `parents=[store_parent]` with a literal default ("notes.json")
    # made the subparser's own default win over an already-parsed
    # top-level `--store` value whenever `--store` was given *before* the
    # subcommand (`notekeeper --store X add ...` silently reverted to
    # "notes.json", ignoring X). Each subparser copy must instead default
    # to `argparse.SUPPRESS` so that omitting `--store` after the
    # subcommand leaves the top-level parser's already-parsed value in
    # place, while still letting `--store` be given after the subcommand
    # too (`notekeeper add ... --store X`).
    store_parent = argparse.ArgumentParser(add_help=False)
    store_parent.add_argument("--store", default="notes.json", help="Path to the note store file")

    sub_store_parent = argparse.ArgumentParser(add_help=False)
    sub_store_parent.add_argument("--store", default=argparse.SUPPRESS, help="Path to the note store file")

    parser = argparse.ArgumentParser(prog="notekeeper", parents=[store_parent])

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new note", parents=[sub_store_parent])
    add_parser.add_argument("title")
    add_parser.add_argument("body")
    add_parser.add_argument("--tags", default=None, help="Comma-separated tags")
    add_parser.set_defaults(func=_cmd_add)

    list_parser = subparsers.add_parser("list", help="List all notes", parents=[sub_store_parent])
    list_parser.set_defaults(func=_cmd_list)

    show_parser = subparsers.add_parser("show", help="Show a note's details", parents=[sub_store_parent])
    show_parser.add_argument("id")
    show_parser.set_defaults(func=_cmd_show)

    search_parser = subparsers.add_parser("search", help="Search notes", parents=[sub_store_parent])
    search_parser.add_argument("query", nargs="?", default=None)
    search_parser.add_argument("--tag", default=None)
    search_parser.set_defaults(func=_cmd_search)

    delete_parser = subparsers.add_parser("delete", help="Delete a note", parents=[sub_store_parent])
    delete_parser.add_argument("id")
    delete_parser.set_defaults(func=_cmd_delete)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        store = NoteStore(args.store)
        return args.func(args, store)
    except NoteStoreError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

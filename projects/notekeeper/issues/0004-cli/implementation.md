# Implementation: Add a CLI to notekeeper

실제 저장 위치: `src/notekeeper/cli.py`

**참고**: 아래는 최초 Implementation 산출물이다(역사적 기록, 수정하지
않음). 실제 결함(잘못된 속성명, argparse 순서 문제 2라운드)과 그
수정은 `fix-cycle.md`에 기록되어 있다 — 실제 최종 코드는
`fix-cycle.md`가 기술하는 버전이다.

```python
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
    print(f"Created: {note.created}")
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
    parser = argparse.ArgumentParser(prog="notekeeper")
    parser.add_argument("--store", default="notes.json", help="Path to the note store file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new note")
    add_parser.add_argument("title")
    add_parser.add_argument("body")
    add_parser.add_argument("--tags", default=None, help="Comma-separated tags")
    add_parser.set_defaults(func=_cmd_add)

    list_parser = subparsers.add_parser("list", help="List all notes")
    list_parser.set_defaults(func=_cmd_list)

    show_parser = subparsers.add_parser("show", help="Show a note's details")
    show_parser.add_argument("id")
    show_parser.set_defaults(func=_cmd_show)

    search_parser = subparsers.add_parser("search", help="Search notes")
    search_parser.add_argument("query", nargs="?", default=None)
    search_parser.add_argument("--tag", default=None)
    search_parser.set_defaults(func=_cmd_search)

    delete_parser = subparsers.add_parser("delete", help="Delete a note")
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
```

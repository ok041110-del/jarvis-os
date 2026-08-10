# Design: Add a CLI to textkit that uses slugify and truncate

## Design: `textkit` CLI

**Approach**

Add `src/textkit/cli.py` as a thin argparse-based adapter. It builds one top-level parser with a required subparsers block (`dest="command"`), and one sub-parser per existing function. Each subcommand's arguments map 1:1 onto that function's parameters, so the CLI does no interpretation of the text itself — it only translates shell arguments into a Python call and prints the return value.

Structure:
- A top-level `ArgumentParser` (prog name, short description).
- `subparsers = parser.add_subparsers(dest="command", required=True)` so invoking with no subcommand fails fast with argparse's own usage message rather than silently doing nothing.
- `slugify` subparser: one positional `text`.
- `truncate` subparser: one positional `text`, required `--max-len` (`type=int`), optional `--suffix` (`default="..."`, matching `truncate()`'s own default so `--help` shows the real behavior instead of leaving it implicit via a `None` fallback).
- Each subparser calls `set_defaults(func=...)` pointing at a small wrapper (or a lambda-equivalent) that unpacks `args` into the real `slugify()`/`truncate()` call and prints the result. This keeps `main()` free of `if/elif` branching on `args.command` and makes adding a third subcommand later purely additive.
- `main()` = `parse_args()` → `args.func(args)`. The `if __name__ == "__main__": main()` guard at the bottom makes it runnable directly and importable as a future `console_scripts` target.

**Responsibilities**

- `cli.py` owns: argument definitions, help text, dispatch, printing.
- `slugify.py` / `truncate.py` remain untouched and own all text-transformation logic and validation (e.g., `truncate`'s `ValueError` on bad `max_len`/`suffix` combinations). The CLI never duplicates or re-validates that logic — it imports the two functions directly (`from textkit.slugify import slugify`, `from textkit.truncate import truncate`) and trusts them.

**Error-handling UX decision**

Recommend explicitly punting on custom error handling: let `truncate()`'s `ValueError` propagate as an uncaught exception. This is consistent with the "thin adapter" constraint — adding a `try/except` that reformats the error into `argparse.error(...)` is a legitimate future enhancement but is new behavior/UX design, not just wiring, so it shouldn't be assumed. Flagging this to the user rather than silently picking one path.

**Risks**

- Import path: `cli.py` sitting inside `src/textkit/` means `python -m textkit.cli` or a proper editable install is needed for `from textkit.slugify import slugify` to resolve — running the file directly with `python src/textkit/cli.py` would break on the package-relative import unless the package is installed. Worth confirming how the user intends to invoke it before assuming `python -m`.
- `--max-len` omitted or non-integer: handled for free by argparse (`required=True`, `type=int`), no extra code needed, but worth a one-line mention in `--help`/error output expectations.
- No `console_scripts` entry point is in scope per the requirement, so the CLI is only reachable via `python -m textkit.cli ...` or direct file execution post-install — flagging again in case the user actually wants `pip install` to give them a bare `textkit` command.
- Future subcommand growth: the `set_defaults(func=...)` pattern avoids an `if/elif` chain, but if subcommands multiply significantly, argument definitions and dispatch wrappers may eventually warrant moving into a small per-subcommand registration function — not needed at 2 subcommands.

No code has been written yet — this is the proposed shape for review before implementation.


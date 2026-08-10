# Planning: Add a CLI to textkit that uses slugify and truncate

## Requirement Analysis: textkit CLI

**Goal**
Give the `textkit` package a command-line entry point (`src/textkit/cli.py`) that exposes its existing `slugify` and `truncate` functions as subcommands, so users can invoke the library's text-transformation logic directly from a shell rather than only via Python imports.

**Scope**
- New file `cli.py` using only `argparse` (stdlib) — no third-party CLI frameworks (e.g., Click, Typer).
- Two subcommands:
  - `slugify TEXT` — positional text argument, calls `textkit.slugify.slugify(text)`, prints result.
  - `truncate TEXT --max-len N [--suffix S]` — positional text plus a required `--max-len` int option and optional `--suffix` string option (defaulting to whatever `truncate()`'s own default is, i.e., `"..."`), calls `textkit.truncate.truncate(text, max_len, suffix)`, prints result.
- Must `import` both functions from `textkit.slugify` and `textkit.truncate` — no reimplementation of slug/truncate logic inside the CLI. This is an explicit non-negotiable constraint, so the CLI layer stays a thin adapter (arg parsing + dispatch + print) over the existing pure functions.
- Standard `main()` function plus `if __name__ == "__main__": main()` guard, so it works both as a script and as an importable entry point (e.g., for a future `console_scripts` hook in packaging config, though packaging/setup changes aren't explicitly requested here — worth clarifying with the user if they also want an installable `textkit` command).
- Output: print the transformed string to stdout. No mention of exit codes, so default `argparse`/Python behavior (0 on success) is acceptable.

**Out of scope**
- No new business logic — `slugify.py` and `truncate.py` are untouched.
- No external dependencies.
- No mention of tests in the request, though a CLI wrapper this thin would typically warrant a couple of subprocess/argparse-level smoke tests (e.g., via `capsys` or invoking `main()` with patched `sys.argv`) — flag this as a likely follow-up rather than assumed scope.
- No packaging/`pyproject.toml` entry_points change specified — only the module itself.

**Risks / edge cases to watch**
- `truncate()` raises `ValueError` for negative `max_len` or `max_len < len(suffix)`; the CLI should let this propagate as a normal traceback/error (or the user may want a cleaner `argparse.error`/non-zero-exit message — worth confirming expected UX, since an uncaught `ValueError` produces a Python traceback rather than a clean CLI error).
- `slugify()` will raise `AttributeError` on non-str input, but since `TEXT` comes from `argparse` positional args it's always a `str`, so this isn't reachable in practice.
- `--max-len` must be parsed as `int` (`type=int` in argparse) — an invalid value should fail via argparse's own error handling, which is standard and requires no extra code.
- Subcommand dispatch (`args.command == "slugify"` vs `"truncate"`) needs to be structured so adding future subcommands doesn't require touching unrelated code — but given the 2-subcommand scope, a straightforward `subparsers` + `set_defaults(func=...)` pattern is sufficient without over-engineering.

No implementation ambiguity beyond the exit-code/error-handling UX question above; this is a small, well-bounded task.


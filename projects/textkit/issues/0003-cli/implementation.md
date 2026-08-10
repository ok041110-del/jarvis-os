# Implementation: Add a CLI to textkit that uses slugify and truncate

실제 저장 위치: `src/textkit/cli.py`

```python
"""Command-line interface for textkit."""

import argparse

from textkit.slugify import slugify
from textkit.truncate import truncate


def _run_slugify(args):
    print(slugify(args.text))


def _run_truncate(args):
    print(truncate(args.text, args.max_len, suffix=args.suffix))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="textkit",
        description="Text transformation utilities.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    slugify_parser = subparsers.add_parser("slugify", help="Convert text to a URL-friendly slug.")
    slugify_parser.add_argument("text", help="Text to slugify.")
    slugify_parser.set_defaults(func=_run_slugify)

    truncate_parser = subparsers.add_parser("truncate", help="Truncate text to a maximum length.")
    truncate_parser.add_argument("text", help="Text to truncate.")
    truncate_parser.add_argument("--max-len", type=int, required=True, dest="max_len", help="Maximum length of the result.")
    truncate_parser.add_argument("--suffix", default="...", help="Suffix to append when text is truncated (default: '...').")
    truncate_parser.set_defaults(func=_run_truncate)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

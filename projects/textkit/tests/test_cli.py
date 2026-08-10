import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from textkit.cli import build_parser, main


def _run(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["textkit"] + argv)
    main()


def test_slugify_subcommand(monkeypatch, capsys):
    _run(monkeypatch, ["slugify", "Hello World"])
    assert capsys.readouterr().out.strip() == "hello-world"


def test_truncate_subcommand_default_suffix(monkeypatch, capsys):
    _run(monkeypatch, ["truncate", "hello!", "--max-len", "5"])
    assert capsys.readouterr().out.strip() == "he..."


def test_truncate_subcommand_custom_suffix(monkeypatch, capsys):
    _run(monkeypatch, ["truncate", "hello world", "--max-len", "8", "--suffix", "-"])
    out = capsys.readouterr().out.strip()
    assert len(out) == 8
    assert out.endswith("-")


def test_truncate_subcommand_text_fits(monkeypatch, capsys):
    _run(monkeypatch, ["truncate", "hi", "--max-len", "10"])
    assert capsys.readouterr().out.strip() == "hi"


def test_missing_subcommand_errors(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["textkit"])
    with pytest.raises(SystemExit):
        main()


def test_unknown_subcommand_errors(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["textkit", "nope"])
    with pytest.raises(SystemExit):
        main()


def test_truncate_missing_required_max_len_errors(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["textkit", "truncate", "hello"])
    with pytest.raises(SystemExit):
        main()


def test_build_parser_registers_both_subcommands():
    parser = build_parser()
    assert parser._subparsers is not None
    choices = parser._subparsers._group_actions[0].choices
    assert set(choices.keys()) == {"slugify", "truncate"}

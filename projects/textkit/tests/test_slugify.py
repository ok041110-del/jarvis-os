import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from textkit.slugify import slugify


def test_basic():
    assert slugify("Hello World") == "hello-world"


def test_idempotent():
    assert slugify("already-a-slug") == "already-a-slug"


def test_strips_surrounding_whitespace():
    assert slugify("  leading and trailing spaces  ") == "leading-and-trailing-spaces"


def test_collapses_runs_of_separators():
    assert slugify("a---b") == "a-b"
    assert slugify("a b") == "a-b"
    assert slugify("a??b") == "a-b"


def test_empty_string():
    assert slugify("") == ""


def test_all_punctuation_yields_empty():
    assert slugify("!!!") == ""


def test_whitespace_only_yields_empty():
    assert slugify("   ") == ""


def test_underscore_treated_as_separator():
    assert slugify("snake_case_name") == "snake-case-name"


def test_leading_underscore_stripped():
    assert slugify("_leading_underscore") == "leading-underscore"


def test_numbers_preserved():
    assert slugify("Product123") == "product123"
    assert slugify("123 456") == "123-456"


def test_strips_leading_trailing_dashes_after_collapse():
    assert slugify("---hello---") == "hello"


def test_non_str_raises_attributeerror():
    import pytest

    with pytest.raises(AttributeError):
        slugify(123)

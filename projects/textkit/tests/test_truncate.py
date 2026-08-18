import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from textkit.truncate import truncate


def test_no_truncation_needed():
    assert truncate("hello", 5) == "hello"


def test_shorter_than_max_len():
    assert truncate("hi", 10) == "hi"


def test_truncates_with_default_suffix():
    result = truncate("hello!", 5)
    assert result == "he..."
    assert len(result) == 5


def test_empty_text():
    assert truncate("", 5) == ""


def test_result_length_matches_max_len_exactly():
    result = truncate("x" * 100, 10)
    assert len(result) == 10


def test_custom_suffix():
    result = truncate("hello world", 8, suffix="…")
    assert len(result) == 8
    assert result.endswith("…")


def test_max_len_equal_to_suffix_length_when_truncating():
    result = truncate("hello world", 5, suffix="[cut]")
    assert result == "[cut]"


def test_empty_suffix_behaves_as_plain_slice():
    assert truncate("hello world", 5, suffix="") == "hello"


def test_negative_max_len_raises_when_truncation_needed():
    with pytest.raises(ValueError):
        truncate("hello world", -1)


def test_max_len_shorter_than_suffix_raises_when_truncation_needed():
    with pytest.raises(ValueError):
        truncate("hello world", 2, suffix="...")


def test_max_len_shorter_than_suffix_does_not_raise_when_text_already_fits():
    assert truncate("hi", 2, suffix="...") == "hi"


def test_negative_max_len_still_raises_when_text_is_short():
    with pytest.raises(ValueError):
        truncate("hi", -1)

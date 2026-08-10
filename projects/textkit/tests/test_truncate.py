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
    """Two-round real Fix cycle, both rounds verified against a real
    pytest run (not just Engine opinion):

    Round 1 — the original implementation validated `max_len < len(suffix)`
    *after* the `len(text) <= max_len` early return, so it silently skipped
    validation whenever the text already fit (e.g. `truncate("hi", 2,
    suffix="...")` returned `"hi"` instead of raising, per a strict reading
    of the docstring's unconditional `Raises` wording at the time).

    Round 2 — moving the validation before the early return (to satisfy
    round 1's literal contract) was itself re-reviewed by a second real
    Engine call, which found *that* version wrong instead: it now raised
    `ValueError` for legitimate no-op calls like `truncate("ok", 2)` where
    `len(text) == max_len` and the suffix is never actually used — directly
    contradicting the docstring's own "returned unchanged" guarantee.

    Resolution: `max_len`/`suffix` validation only matters once truncation
    is actually attempted (this is a docstring/contract clarification, not
    a code bug — the original code's *behavior* here was correct; only its
    docstring overclaimed unconditional validation). `truncate.py`'s
    docstring was corrected to say so explicitly."""
    assert truncate("hi", 2, suffix="...") == "hi"


def test_negative_max_len_still_raises_when_text_is_short():
    """Unlike the suffix-length check above, this one is NOT masked by
    the early return: `len(text)` is never negative, so
    `len(text) <= max_len` can never be True when `max_len` is negative
    — the early return can't fire, so the negative-max_len check is
    always reached. Confirmed by running this test: it passes against
    the current implementation (no bug here), unlike the suffix-length
    case above."""
    with pytest.raises(ValueError):
        truncate("hi", -1)

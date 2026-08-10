"""Truncate text to a maximum length, appending a suffix when truncation occurs."""


def truncate(text: str, max_len: int, suffix: str = "...") -> str:
    """Truncate ``text`` to at most ``max_len`` characters.

    If ``text`` already fits within ``max_len``, it is returned unchanged
    and no validation of ``max_len``/``suffix`` is performed — the
    combination only matters once truncation is actually attempted.
    Otherwise, ``text`` is sliced so that the result (sliced text + ``suffix``)
    is exactly ``max_len`` characters long.

    Args:
        text: The string to truncate.
        max_len: The maximum length of the returned string.
        suffix: Appended to truncated text. Defaults to ``"..."``.

    Returns:
        ``text`` unchanged if ``len(text) <= max_len``; otherwise
        ``text`` sliced and concatenated with ``suffix`` such that the
        result has length exactly ``max_len``.

    Raises:
        ValueError: If truncation is actually needed (``len(text) >
            max_len``) and ``max_len`` is negative, or ``max_len`` is
            shorter than ``len(suffix)`` (truncation would be
            impossible). Not raised when ``text`` already fits, even if
            ``max_len`` is smaller than ``len(suffix)`` — the suffix is
            never used in that case.

    Examples:
        >>> truncate("hello", 5)
        'hello'
        >>> truncate("hi", 2)
        'hi'
        >>> truncate("hello!", 5)
        'he...'
        >>> truncate("hello", 3, suffix="...")
        '...'
    """
    if len(text) <= max_len:
        return text

    if max_len < 0:
        raise ValueError(f"max_len ({max_len}) cannot be negative")

    if max_len < len(suffix):
        raise ValueError(
            f"max_len ({max_len}) is shorter than suffix length ({len(suffix)})"
        )

    return text[: max_len - len(suffix)] + suffix

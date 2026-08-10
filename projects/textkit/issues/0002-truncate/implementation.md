# Implementation: Add truncate() to textkit

실제 저장 위치: `src/textkit/truncate.py`

**참고**: 아래는 이 Issue의 최초 Implementation 산출물이다(역사적
기록, 수정하지 않음). 이후 real Review와 real pytest가 찾아낸 결함과
그 수정 2라운드는 `fix-cycle.md`에 기록되어 있다 — `src/textkit/truncate.py`의
실제 최종 코드는 이 파일이 아니라 `fix-cycle.md`가 기술하는 최종
버전이다.

```python
"""Truncate text to a maximum length, appending a suffix when truncation occurs."""


def truncate(text: str, max_len: int, suffix: str = "...") -> str:
    """Truncate ``text`` to at most ``max_len`` characters.

    If ``text`` already fits within ``max_len``, it is returned unchanged.
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
        ValueError: If ``max_len`` is negative, or if ``max_len`` is
            shorter than ``len(suffix)``.

    Examples:
        >>> truncate("hello", 5)
        'hello'
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
```

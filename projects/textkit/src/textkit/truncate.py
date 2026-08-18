def truncate(text: str, max_len: int, suffix: str = "...") -> str:
    """max_len/suffix validation only applies once truncation is actually
    needed; text that already fits is returned unchanged without raising."""
    if len(text) <= max_len:
        return text

    if max_len < 0:
        raise ValueError(f"max_len ({max_len}) cannot be negative")

    if max_len < len(suffix):
        raise ValueError(
            f"max_len ({max_len}) is shorter than suffix length ({len(suffix)})"
        )

    return text[: max_len - len(suffix)] + suffix

import re


def slugify(text: str) -> str:
    """Non-ASCII alphanumeric characters (accented letters, CJK, ...) are
    treated as separators, not transliterated."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

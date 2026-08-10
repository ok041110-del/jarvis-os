# Implementation: Add slugify() to textkit

실제 저장 위치: `src/textkit/slugify.py`

```python
import re


def slugify(text: str) -> str:
    """Convert text to an ASCII-only slug.

    Non-ASCII alphanumeric characters (e.g. accented letters, CJK) are
    treated as separators, not preserved or transliterated. Does not
    validate input type; a non-str argument will raise naturally
    (e.g. AttributeError on `.lower()`).
    """
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
```

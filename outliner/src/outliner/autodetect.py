import os
from outliner.parsers import _PARSERS


def detect_syntax(filename: str | None, content: str | None = None) -> str | None:
    """Return syntax name for a file, or None if undetectable.

    Tries extension first.  Falls back to scanning the first 10 lines of
    *content* when provided and the extension gave no result.
    """
    if filename and filename != "-":
        ext = os.path.splitext(filename.lower())[1]
        for mod in _PARSERS:
            if ext in mod.EXTENSIONS:
                return mod.SYNTAX
    if content is not None:
        lines = content.splitlines()[:10]
        for mod in _PARSERS:
            if hasattr(mod, "detect_content") and mod.detect_content(lines):
                return mod.SYNTAX
    return None

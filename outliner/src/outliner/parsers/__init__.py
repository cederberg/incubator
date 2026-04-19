import os
from . import rst, markdown
from outliner.types import OutlineItem

_PARSERS = [rst, markdown]

NAMES = [mod.SYNTAX for mod in _PARSERS]

EXTENSIONS: dict[str, str] = {
    ext: mod.SYNTAX
    for mod in _PARSERS
    for ext in mod.EXTENSIONS
}


def detect(content: str) -> str | None:
    """Return syntax name from content scan, or None."""
    lines = content.splitlines()[:100]
    for mod in _PARSERS:
        if mod.detect(lines):
            return mod.SYNTAX
    return None


def outline(syntax: str, content: str) -> list[OutlineItem] | None:
    """Parse content with the named syntax. Returns None if syntax is unknown."""
    for mod in _PARSERS:
        if mod.SYNTAX == syntax:
            return mod.parse(content)
    return None

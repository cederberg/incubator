from . import rst, python, markdown
from outliner.types import OutlineItem

_MODULES = [rst, python, markdown]
_PARSERS = {mod.SYNTAX: mod.parse for mod in _MODULES}
NAMES = sorted(_PARSERS)
EXTENSIONS = {ext: mod.SYNTAX for mod in _MODULES for ext in mod.EXTENSIONS}


def detect(content: str) -> str | None:
    lines = content.splitlines()[:100]
    for mod in _MODULES:
        if mod.detect(lines):
            return mod.SYNTAX
    return None


def outline(syntax: str, content: str) -> list[OutlineItem] | None:
    parse = _PARSERS.get(syntax)
    return parse(content) if parse else None

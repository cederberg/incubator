import io
import re
import types
from typing import TextIO

from ..types import OutlineItem
from . import (
    python, scala, go, java, rust, swift, c, ruby, php, shell, javascript,
    csharp, perl, zig, clojure, html, asciidoc, orgmode, rst, json, xml,
    markdown,
)

_MODULES = {
    mod.SYNTAX: mod
    for mod in globals().values() if (
        isinstance(mod, types.ModuleType)
        and mod.__name__.startswith(f"{__name__}.")
        and hasattr(mod, "SYNTAX")
        and hasattr(mod, "EXTENSIONS")
    )
}
NAMES = sorted(_MODULES)
EXTENSIONS = {ext: syntax for syntax, mod in _MODULES.items() for ext in mod.EXTENSIONS}
_FRONTMATTER_RE = re.compile(r'\A(?:---\n(?:.*\n){0,98}?---\n|\+\+\+\n(?:.*\n){0,98}?\+\+\+\n)')


def _strip_frontmatter(content: str) -> str:
    m = _FRONTMATTER_RE.match(content)
    return content[m.end():] if m else content


def syntax(name: str) -> str | None:
    if name in _MODULES:
        return name
    ext = name if name.startswith(".") else "." + name
    return EXTENSIONS.get(ext)


def detect(content: str) -> str | None:
    lines = _strip_frontmatter(content).splitlines()[:100]
    for mod in _MODULES.values():
        if mod.detect(lines):
            return mod.SYNTAX
    return None


def outline(syntax: str, content: str | TextIO) -> list[OutlineItem] | None:
    mod = _MODULES.get(syntax)
    if not mod:
        return None
    elif hasattr(mod, "read"):
        fh = io.StringIO(content) if isinstance(content, str) else content
        return list(mod.read(fh))
    else:
        text = content.read() if hasattr(content, "read") else content
        return _outline_text(mod, text)


def _outline_text(mod, content: str) -> list[OutlineItem]:
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return list(mod.parse(content))
    offset = m.group(0).count('\n')
    return [OutlineItem(start=it.start + offset, count=it.count, signature=it.signature)
            for it in mod.parse(content[m.end():])]

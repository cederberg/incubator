import re

from . import python, scala, go, java, rust, swift, c, ruby, php, shell, javascript, csharp, perl, zig, clojure, asciidoc, orgmode, rst, markdown
from outliner.types import OutlineItem

_MODULES = [python, scala, go, java, rust, swift, c, ruby, php, shell, javascript, csharp, perl, zig, clojure, asciidoc, orgmode, rst, markdown]
_PARSERS = {mod.SYNTAX: mod.parse for mod in _MODULES}
NAMES = sorted(_PARSERS)
EXTENSIONS = {ext: mod.SYNTAX for mod in _MODULES for ext in mod.EXTENSIONS}

_FRONTMATTER_RE = re.compile(r'\A---\n(?:.*\n){0,98}?---\n')


def _strip_frontmatter(content: str) -> str:
    m = _FRONTMATTER_RE.match(content)
    return content[m.end():] if m else content


def detect(content: str) -> str | None:
    lines = _strip_frontmatter(content).splitlines()[:100]
    for mod in _MODULES:
        if mod.detect(lines):
            return mod.SYNTAX
    return None


def outline(syntax: str, content: str) -> list[OutlineItem] | None:
    parse = _PARSERS.get(syntax)
    if not parse:
        return None
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return parse(content)
    offset = m.group(0).count('\n')
    return [OutlineItem(start=it.start + offset, count=it.count, signature=it.signature)
            for it in parse(content[m.end():])]

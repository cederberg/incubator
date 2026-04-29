"""Ruby outline parser (regex-based)."""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start

SYNTAX = "ruby"
EXTENSIONS = (".rb", ".rake", ".gemspec")

_MODULE_RE = re.compile(r"^\s*module\s+[A-Z][\w:]*")
_CLASS_RE  = re.compile(r"^\s*class\s+[A-Z][\w:]*")
# Matches regular methods, self.methods, ?, ! suffixes, and operator overloads
_DEF_RE    = re.compile(r"^\s*def\s+(?:\w+\.)?(?:[_a-zA-Z]\w*[?!]?|[=<>!+\-*/%&|^~\[\]]+)")
_ATTR_RE   = re.compile(r"^\s*attr_(?:reader|writer|accessor)\b")

# Closing 'end' keyword matched on the raw (unstripped) line
_END_RE    = re.compile(r"^\s*end\b")

_SHEBANG_RE          = re.compile(r"^#!.*ruby", re.IGNORECASE)
_REQUIRE_RELATIVE_RE = re.compile(r"^\s*require_relative\b")


def detect(lines: list[str]) -> bool:
    """Detect Ruby: shebang, attr_* macros, require_relative, or def+end+class/module."""
    for line in lines[:3]:
        if _SHEBANG_RE.match(line.strip()):
            return True
    if any(_ATTR_RE.match(l) for l in lines):
        return True
    if any(_REQUIRE_RELATIVE_RE.match(l) for l in lines):
        return True
    has_def = any(_DEF_RE.match(l) for l in lines)
    has_end = any(re.match(r"^\s*end\s*$", l) for l in lines)
    has_container = any(_CLASS_RE.match(l) or _MODULE_RE.match(l) for l in lines)
    return has_def and has_end and has_container


def _collect_sig(lines: list[str], start: int) -> tuple[str, int]:
    """Return (indented_signature, last_sig_line_0based).

    Tracks parenthesis depth for multi-line signatures; stops when balanced.
    Parens inside string literals or inline comments may confuse the counter,
    which is an accepted limitation.
    """
    ind = " " * indent_level(lines[start])
    depth = 0
    has_paren = False
    parts: list[str] = []
    for i in range(start, len(lines)):
        raw = lines[i]
        text = raw.lstrip() if i == start else raw.strip()
        for ch in raw:
            if ch == "(":
                depth += 1
                has_paren = True
            elif ch == ")":
                depth -= 1
        parts.append(text)
        if not has_paren or depth <= 0:
            break
    return ind + extract_signature(parts), i


def _block_end(lines: list[str], start: int) -> int:
    """Return 0-based exclusive end of the Ruby block starting at lines[start].

    Matches the closing 'end' at the same indentation level as the opener,
    which naturally handles nested do...end blocks without keyword counting.
    Endless methods (Ruby 3.0+, e.g. 'def square(x) = x * 2') have no 'end'
    and will incorrectly extend to the next same-level 'end'.
    """
    target_ind = indent_level(lines[start])
    for i in range(start + 1, len(lines)):
        if _END_RE.match(lines[i]) and indent_level(lines[i]) == target_ind:
            return i + 1
    return len(lines)


def parse(text: str) -> Iterator[OutlineItem]:
    for i, line in enumerate(lines := text.splitlines()):
        if any(r.match(line) for r in [_MODULE_RE, _CLASS_RE, _DEF_RE, _ATTR_RE]):
            _is_comment = lambda ln, s, d=indent_level(line): indent_level(ln) >= d and s[0] == '#'
            sig, _sig_end = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_comment)
            end = i + 1 if _ATTR_RE.match(line) else _block_end(lines, i)
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)

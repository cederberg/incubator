"""Scala outline parser (regex-based)."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end

SYNTAX = "scala"
EXTENSIONS = (".scala", ".sc")

_MODS = (
    r"(?:(?:override|private(?:\[[\w.]+\])?|protected(?:\[[\w.]+\])?|"
    r"final|abstract|sealed|implicit|lazy|inline|transparent|opaque|open|case|inner)\s+)*"
)

_TRAIT_RE     = re.compile(r"^\s*" + _MODS + r"trait\s+\w+")
_CLASS_RE     = re.compile(r"^\s*" + _MODS + r"class\s+\w+")
_OBJECT_RE    = re.compile(r"^\s*" + _MODS + r"object\s+\w+")
_DEF_RE       = re.compile(r"^\s*" + _MODS + r"def\s+\w+")
_TYPE_RE      = re.compile(r"^\s*" + _MODS + r"type\s+\w+\s*(?:\[|=|<:|>:)")
_GIVEN_RE     = re.compile(r"^\s*given\s+\w")
_EXTENSION_RE = re.compile(r"^\s*extension\s*\(")

_ALL_DECLS = [_TRAIT_RE, _CLASS_RE, _OBJECT_RE, _DEF_RE, _TYPE_RE, _GIVEN_RE, _EXTENSION_RE]

# Detection helpers
_CASE_CLASS_RE  = re.compile(r"\bcase\s+class\s+\w+")
_OBJ_DECL_RE    = re.compile(r"\bobject\s+\w+\s*(?:\{|extends\b|:)")
_DEF_DETECT_RE  = re.compile(r"\bdef\s+\w+")

# frozenset membership avoids the Python gotcha where '"" in "abc"' is True.
# _BAD_PREV: skip '=' when preceded by =>(arrow), <=(compare), >=(compare),
# !=(not-equal), <:(lower-bound), :=(compound-assign), ==(equality),
# or '(single-quote, to handle '=' character literals).
_BAD_PREV = frozenset("'=><!:")
_BAD_NEXT = frozenset(">:=")


def detect(lines: list[str]) -> bool:
    """Detect Scala: case class, or object declaration with def."""
    has_case_class = any(_CASE_CLASS_RE.search(l) for l in lines)
    if has_case_class:
        return True
    has_object = any(_OBJ_DECL_RE.search(l) for l in lines)
    has_def = any(_DEF_DETECT_RE.search(l) for l in lines)
    return has_object and has_def


def _strip_equals_body(sig: str) -> str:
    """Strip '= <body>' from a def/given signature at paren and bracket depth 0.

    Skips '=' inside parameter lists (dp > 0) and type parameters (db > 0),
    and skips compound operators: =>, <=, >=, !=, <:, ==.
    """
    dp = 0
    db = 0
    for i, ch in enumerate(sig):
        if ch == "(":
            dp += 1
        elif ch == ")":
            dp -= 1
        elif ch == "[":
            db += 1
        elif ch == "]":
            db -= 1
        elif ch == "=" and dp == 0 and db == 0:
            prev = sig[i - 1] if i > 0 else ""
            nxt  = sig[i + 1] if i + 1 < len(sig) else ""
            if prev not in _BAD_PREV and nxt not in _BAD_NEXT:
                return sig[:i].rstrip()
    return sig


def _collect_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a possibly multi-line Scala signature.

    Tracks paren and bracket depth; stops when both reach 0 (all parameter
    lists and type parameters closed).  Returns (signature, last_sig_line,
    has_body).
    """
    dp = 0
    db = 0
    parts: list[str] = []
    ind = " " * indent_level(lines[start])
    has_body = False
    last = start

    is_def   = bool(_DEF_RE.match(lines[start]))
    is_given = bool(_GIVEN_RE.match(lines[start]))

    for i in range(start, len(lines)):
        raw = lines[i]
        for ch in raw:
            if ch == "(":
                dp += 1
            elif ch == ")":
                dp -= 1
            elif ch == "[":
                db += 1
            elif ch == "]":
                db -= 1
        parts.append(raw.strip())
        last = i

        if dp <= 0 and db <= 0:
            if raw.rstrip().endswith("{"):
                has_body = True
            break

    sig = extract_signature(parts, strip="{")
    if sig.rstrip().endswith(" with"):
        sig = sig.rstrip()[:-5].rstrip()
    if is_def or is_given:
        sig = _strip_equals_body(sig)

    return ind + sig, last, has_body


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines()
    items: list[OutlineItem] = []

    for i, raw in enumerate(lines):
        if not any(r.match(raw) for r in _ALL_DECLS):
            continue
        sig, sig_end, has_body = _collect_sig(lines, i)
        start = seek_comment_start(lines, i, lambda _, s: s[0] in "/*@")
        end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
        items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))

    return items

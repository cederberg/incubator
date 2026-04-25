"""Python outline parser (regex-based)."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start

SYNTAX = "python"
EXTENSIONS = (".py", ".pyw")

_DEF_RE = re.compile(r"^\s*(?:async\s+def|def|class)\s+\w+")
# Python-specific: def/class declarations end with ':' not '{' (Java/C/JS use braces).
_PY_COLON_RE = re.compile(r"^\s*(async\s+def|def|class)\s+\w+[^{]*:\s*$")
_SHEBANG_RE = re.compile(r"^#!.*python", re.IGNORECASE)


def detect(lines: list[str]) -> bool:
    """Detect Python by shebang or colon-terminated def/class (Java/C use braces)."""
    for line in lines[:3]:
        if _SHEBANG_RE.match(line.strip()):
            return True
    return any(_PY_COLON_RE.match(l) for l in lines)


def _collect_sig(lines: list[str], start: int) -> tuple[str, int]:
    """Return (signature_without_trailing_colon, last_sig_line_0based).

    Tracks bracket depth so multi-line signatures are merged into one line.
    Bracket depth is counted on raw characters; brackets inside string literals
    may confuse the depth counter, which is an accepted limitation.
    """
    ind = " " * indent_level(lines[start])
    depth = 0
    parts: list[str] = []
    for i in range(start, len(lines)):
        raw = lines[i]
        # Strip leading indent for joining; indent is re-applied at the end.
        text = raw.lstrip() if i == start else raw.strip()
        for ch in raw:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
        parts.append(text)
        if depth <= 0 and raw.rstrip().endswith(":"):
            break
    return ind + extract_signature(parts, strip=":"), i


def _block_end(lines: list[str], def_line: int, sig_end: int) -> int:
    """Return 0-based exclusive end of the indented block (trailing blanks excluded)."""
    def_ind = indent_level(lines[def_line])
    last = sig_end
    for i in range(sig_end + 1, len(lines)):
        raw = lines[i]
        if not raw.strip():
            continue
        if indent_level(raw) <= def_ind:
            break
        last = i
    return last + 1


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines()
    n = len(lines)
    items: list[OutlineItem] = []

    i = 0
    while i < n:
        raw = lines[i]

        m = _DEF_RE.match(raw)
        if m:
            sig, sig_end = _collect_sig(lines, i)
            def_ind = indent_level(lines[i])
            start = seek_comment_start(lines, i, lambda ln, s: indent_level(ln) >= def_ind and s[0] in "#@")
            end = _block_end(lines, i, sig_end)
            items.append(OutlineItem(
                start=start + 1,
                count=end - start,
                signature=sig,
            ))
            i = sig_end + 1
            continue

        i += 1

    return items

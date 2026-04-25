"""Go outline parser (regex-based)."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, seek_comment_start, seek_brace_end

SYNTAX = "go"
EXTENSIONS = (".go",)

_FUNC_RE = re.compile(r"^func\b")
_TYPE_RE = re.compile(r"^type\b")
_PACKAGE_RE = re.compile(r"^package\s+\w+")


def detect(lines: list[str]) -> bool:
    has_package = any(_PACKAGE_RE.match(l) for l in lines)
    has_go = any(_FUNC_RE.match(l) or _TYPE_RE.match(l) for l in lines)
    return has_package and has_go


def _collect_sig(lines: list[str], start: int, n: int, *, until_brace: bool = False) -> tuple[str, int, bool]:
    """Collect a possibly multi-line Go signature.

    until_brace=True (func): keep collecting until balanced and trailing '{'.
    until_brace=False (type): stop as soon as depth hits zero.
    Returns (signature_without_trailing_{, last_sig_line, has_body).
    """
    paren_depth = 0
    bracket_depth = 0
    parts: list[str] = []
    i = start
    has_body = False
    while i < n:
        raw = lines[i].rstrip("\r\n")
        for ch in raw:
            if ch == "(":
                paren_depth += 1
            elif ch == ")":
                paren_depth -= 1
            elif ch == "[":
                bracket_depth += 1
            elif ch == "]":
                bracket_depth -= 1
        parts.append(raw.strip())
        if paren_depth <= 0 and bracket_depth <= 0:
            if raw.rstrip().endswith("{"):
                has_body = True
            if has_body or not until_brace:
                break
        i += 1
    return extract_signature(parts, strip="{"), i, has_body


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines(keepends=True)
    n = len(lines)
    items: list[OutlineItem] = []
    i = 0
    while i < n:
        raw = lines[i].rstrip("\r\n")

        # Only consider top-level declarations (no leading whitespace).
        if not raw or raw[0].isspace():
            i += 1
            continue

        if _FUNC_RE.match(raw):
            sig, sig_end, _ = _collect_sig(lines, i, n, until_brace=True)
            start = seek_comment_start(lines, i, lambda _, s: s.startswith("//"))
            end = seek_brace_end(lines, sig_end)
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i = end

        elif _TYPE_RE.match(raw):
            sig, sig_end, has_body = _collect_sig(lines, i, n)
            start = seek_comment_start(lines, i, lambda _, s: s.startswith("//"))
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i = end

        else:
            i += 1

    return items

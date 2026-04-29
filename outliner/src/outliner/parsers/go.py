"""Go outline parser (regex-based)."""

import re
from collections.abc import Iterator

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


def _collect_sig(lines: list[str], start: int, *, until_brace: bool = False) -> tuple[str, int, bool]:
    """Collect a possibly multi-line Go signature.

    until_brace=True (func): keep collecting until balanced and trailing '{'.
    until_brace=False (type): stop as soon as depth hits zero.
    Returns (signature_without_trailing_{, last_sig_line, has_body).
    """
    paren_depth = 0
    bracket_depth = 0
    parts: list[str] = []
    has_body = False
    for i in range(start, len(lines)):
        raw = lines[i]
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
    return extract_signature(parts, strip="{"), i, has_body


def parse(text: str) -> Iterator[OutlineItem]:
    _is_go_comment = lambda _, s: s.startswith("//")
    for i, line in enumerate(lines := text.splitlines()):
        if _FUNC_RE.match(line):
            sig, sig_end, _ = _collect_sig(lines, i, until_brace=True)
            start = seek_comment_start(lines, i, _is_go_comment)
            end = seek_brace_end(lines, sig_end)
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)
        elif _TYPE_RE.match(line):
            sig, sig_end, has_body = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_go_comment)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)

"""Zig outline parser (regex-based)."""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem
from outliner.parsers.util import indent_level, seek_comment_start, seek_brace_end

SYNTAX = "zig"
EXTENSIONS = (".zig",)

# Optional visibility prefix
_VIS = r"(?:pub\s+)?"
# Function modifiers: export, extern (with optional ABI string), inline, noinline
_FN_MODS = r"(?:export\s+)?(?:extern\s+(?:\"[^\"]*\"\s+)?)?(?:inline\s+)?(?:noinline\s+)?"

_FN_RE = re.compile(r"^\s*" + _VIS + _FN_MODS + r"fn\s+\w+")

# Top-level const where the RHS is struct, enum, or union (tagged or plain)
_CONST_TYPE_RE = re.compile(r"^\s*" + _VIS + r"const\s+\w+\s*=\s*(?:struct|enum|union)\b")

# Detection markers
_IMPORT_RE = re.compile(r"@import\(")
_FN_DETECT_RE = re.compile(r"^\s*(?:pub\s+)?fn\s+\w+\s*\(")

_WS_RE = re.compile(r"\s+")
_OPEN_RE = re.compile(r"\(\s+")
_CLOSE_RE = re.compile(r"[,\s]*\)")


def detect(lines: list[str]) -> bool:
    """Detect Zig: @import() built-in combined with fn declarations."""
    has_zig_marker = any(_IMPORT_RE.search(l) for l in lines)
    has_fn = any(_FN_DETECT_RE.match(l) for l in lines)
    return has_zig_marker and has_fn


def _strip_body(s: str, has_body: bool) -> str:
    """Strip the body-opening { (and anything after it) from a joined signature.

    Tracks both paren and brace depth so that:
    - { inside parameter lists is ignored (paren_depth > 0)
    - error{Set} in return types is skipped (brace opened+closed before body)
    The body opener is the last { found at paren_depth=0 and brace_depth=0.
    """
    if not has_body:
        return s.rstrip(";").rstrip()
    paren_depth = 0
    brace_depth = 0
    body_pos = -1
    for k, ch in enumerate(s):
        if ch == "(":
            paren_depth += 1
        elif ch == ")":
            paren_depth -= 1
        elif ch == "{" and paren_depth == 0:
            if brace_depth == 0:
                body_pos = k  # new candidate; updated if a balanced {} follows
            brace_depth += 1
        elif ch == "}" and paren_depth == 0:
            brace_depth -= 1
    return s[:body_pos].rstrip() if body_pos >= 0 else s


def _collect_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a possibly multi-line Zig signature.

    Tracks parenthesis depth; stops when balanced and line contains {
    (has body) or ends with ; (extern fn, no body).
    Returns (signature, last_sig_line_0based, has_body).
    """
    depth = 0
    parts: list[str] = []
    ind = " " * indent_level(lines[start])
    has_body = False
    for i in range(start, len(lines)):
        raw = lines[i]
        for ch in raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        parts.append(raw.strip())
        if depth <= 0:
            if "{" in raw:
                has_body = True
                break
            if raw.rstrip().endswith(";"):
                break
    joined = _WS_RE.sub(" ", " ".join(parts)).strip()
    joined = _OPEN_RE.sub("(", joined)
    joined = _CLOSE_RE.sub(")", joined)
    return ind + _strip_body(joined, has_body), i, has_body


def parse(text: str) -> Iterator[OutlineItem]:
    for i, line in enumerate(lines := text.splitlines()):
        if _FN_RE.match(line) or _CONST_TYPE_RE.match(line):
            sig, sig_end, has_body = _collect_sig(lines, i)
            _is_comment = lambda ln, s, d=indent_level(line): indent_level(ln) >= d and s.startswith("//")
            start = seek_comment_start(lines, i, _is_comment)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)

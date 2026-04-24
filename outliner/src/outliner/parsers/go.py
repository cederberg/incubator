"""Go outline parser (regex-based)."""

import re

from outliner.types import OutlineItem

SYNTAX = "go"
EXTENSIONS = (".go",)

_FUNC_RE = re.compile(r"^func\b")
_TYPE_RE = re.compile(r"^type\b")
_PACKAGE_RE = re.compile(r"^package\s+\w+")


def detect(lines: list[str]) -> bool:
    has_package = any(_PACKAGE_RE.match(l) for l in lines)
    has_go = any(_FUNC_RE.match(l) or _TYPE_RE.match(l) for l in lines)
    return has_package and has_go


def _walk_back(lines: list[str], def_line: int) -> int:
    """Walk back through contiguous // comments above def_line."""
    if def_line == 0:
        return 0
    start = def_line
    i = def_line - 1
    while i >= 0:
        stripped = lines[i].strip()
        if not stripped:
            break
        if stripped.startswith("//"):
            start = i
            i -= 1
        else:
            break
    return start


def _collect_func_sig(lines: list[str], start: int, n: int) -> tuple[str, int]:
    """Collect a multi-line Go function signature, stopping at the opening {.

    Tracks () and [] depth; stops when both are balanced and the line ends
    with {.  Returns (signature_without_trailing_{, last_sig_line_0based).
    """
    paren_depth = 0
    bracket_depth = 0
    parts: list[str] = []
    i = start
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
        if paren_depth <= 0 and bracket_depth <= 0 and raw.rstrip().endswith("{"):
            break
        i += 1
    sig = re.sub(r"\s+", " ", " ".join(parts)).strip()
    sig = re.sub(r"\(\s+", "(", sig)
    sig = re.sub(r",\s*\)", ")", sig)
    sig = sig.rstrip("{").rstrip()
    return sig, i


def _collect_type_sig(lines: list[str], start: int, n: int) -> tuple[str, int, bool]:
    """Collect a Go type signature.

    Returns (signature, last_sig_line_0based, has_body).
    has_body is True when the declaration opens a brace block (struct/interface).
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
            break
        i += 1
    sig = re.sub(r"\s+", " ", " ".join(parts)).strip()
    sig = sig.rstrip("{").rstrip()
    return sig, i, has_body


def _find_brace_end(lines: list[str], sig_line: int, n: int) -> int:
    """Return the 0-based exclusive end of a brace-delimited body.

    sig_line is the line whose trailing { opens the body.
    """
    depth = 1
    i = sig_line + 1
    while i < n:
        raw = lines[i].rstrip("\r\n")
        for ch in raw:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
        if depth <= 0:
            return i + 1
        i += 1
    return n


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
            sig, sig_end = _collect_func_sig(lines, i, n)
            start = _walk_back(lines, i)
            end = _find_brace_end(lines, sig_end, n)
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i = end

        elif _TYPE_RE.match(raw):
            sig, sig_end, has_body = _collect_type_sig(lines, i, n)
            start = _walk_back(lines, i)
            end = _find_brace_end(lines, sig_end, n) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i = end

        else:
            i += 1

    return items

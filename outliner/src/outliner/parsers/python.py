"""Python outline parser (regex-based)."""

import re

from outliner.types import OutlineItem

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


def _indent(line: str) -> int:
    raw = line.rstrip("\r\n")
    return len(raw) - len(raw.lstrip())


def _walk_back(lines: list[str], def_line: int) -> int:
    """Walk back through contiguous # comments and @ decorators above def_line.

    A blank line stops the walk; the def's range does not cross blank lines.
    """
    if def_line == 0:
        return 0
    def_ind = _indent(lines[def_line])
    start = def_line
    i = def_line - 1
    while i >= 0:
        stripped = lines[i].strip()
        if not stripped:
            break
        if _indent(lines[i]) >= def_ind and (stripped.startswith("#") or stripped.startswith("@")):
            start = i
            i -= 1
        else:
            break
    return start


def _collect_sig(lines: list[str], start: int, n: int) -> tuple[str, int]:
    """Return (signature_without_trailing_colon, last_sig_line_0based).

    Tracks bracket depth so multi-line signatures are merged into one line.
    Bracket depth is counted on raw characters; brackets inside string literals
    may confuse the depth counter, which is an accepted limitation.
    """
    depth = 0
    parts: list[str] = []
    i = start
    while i < n:
        raw = lines[i].rstrip("\r\n")
        # First line: strip leading indent; continuation lines: strip both ends.
        text = raw.lstrip() if i == start else raw.strip()
        for ch in raw:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
        parts.append(text)
        if depth <= 0 and raw.rstrip().endswith(":"):
            break
        i += 1
    sig = re.sub(r"\s+", " ", " ".join(parts)).strip()
    # Clean up whitespace that multi-line joining introduces around brackets,
    # and remove the trailing comma that each continuation arg line contributes.
    sig = re.sub(r"\(\s+", "(", sig)
    sig = re.sub(r",\s*\)", ")", sig)
    sig = sig.rstrip(":").rstrip()
    return sig, i


def _block_end(lines: list[str], def_line: int, sig_end: int, n: int) -> int:
    """Return 0-based exclusive end of the indented block (trailing blanks excluded)."""
    def_ind = _indent(lines[def_line])
    last = sig_end
    i = sig_end + 1
    while i < n:
        raw = lines[i].rstrip("\r\n")
        if not raw.strip():
            i += 1
            continue
        if _indent(raw) <= def_ind:
            break
        last = i
        i += 1
    return last + 1


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines(keepends=True)
    n = len(lines)
    items: list[OutlineItem] = []

    i = 0
    while i < n:
        raw = lines[i].rstrip("\r\n")

        m = _DEF_RE.match(raw)
        if m:
            sig, sig_end = _collect_sig(lines, i, n)
            start = _walk_back(lines, i)
            end = _block_end(lines, i, sig_end, n)
            items.append(OutlineItem(
                start=start + 1,
                count=end - start,
                signature=sig,
            ))
            i = sig_end + 1
            continue

        i += 1

    return items

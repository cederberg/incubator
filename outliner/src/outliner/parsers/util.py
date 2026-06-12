"""Shared utilities for outline parsers."""

import re

_RE_WS    = re.compile(r"\s+")
_RE_OPEN  = re.compile(r"\(\s+")
_RE_CLOSE = re.compile(r"[,\s]*\)")


# Format a count with K/M suffix, one decimal below 10 units
def format_count(n: int) -> str:
    for div, unit in ((1_000_000, "M"), (1_000, "K")):
        if n >= div:
            digits = 1 if n < 10 * div else 0
            return f"{n / div:.{digits}f}{unit}"
    return str(n)


# Format a byte size in human-readable units
def format_size(size_bytes: int) -> str:
    for div, unit in ((1_000_000_000, "GB"), (1_000_000, "MB"), (1_000, "KB")):
        if size_bytes >= div:
            return f"{size_bytes / div:.1f} {unit}"
    return f"{size_bytes} B"


# Returns number of indentation chars
def indent_level(line: str) -> int:
    raw = line.rstrip("\r\n")
    return len(raw) - len(raw.lstrip())


# Extract multi-line signature into a clean string
def extract_signature(parts: list[str], strip: str = "") -> str:
    s = " ".join(parts)
    s = _RE_WS.sub(" ", s).strip()
    s = _RE_OPEN.sub("(", s)
    s = _RE_CLOSE.sub(")", s)
    if strip:
        s = s.rstrip(strip).rstrip()
    return s


# Extract short summary sentence or at max a number of chars
def extract_summary(text: str, max_len: int = 120, min_sentence: int = 10) -> str:
    limit = min(len(text), max_len)
    indices = [pos for c in ".!?" if min_sentence <= (pos := text.find(c)) < limit]
    return text[:min(indices) + 1] if indices else text[:limit]


# Seeks the starting comment line for a declaration at lineno
def seek_comment_start(lines: list[str], lineno: int, pred) -> int:
    start = lineno
    for i in range(lineno - 1, -1, -1):
        s = lines[i].strip()
        if not s or not pred(lines[i], s):
            break
        start = i
    return start


# Seeks the 0-based exclusive end of the brace-delimited function body
def seek_brace_end(lines: list[str], start_index: int) -> int:
    depth = 0
    started = False
    for i in range(start_index, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
        if started and depth <= 0:
            return i + 1
    return len(lines)

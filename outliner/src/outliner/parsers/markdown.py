"""Markdown / plain-text outline parser.

Recognises ATX headings (# … ######) and Setext headings (=== / ---
underlines).  Each heading's range extends to the line before the next
heading at the same or higher level (lower number), or to EOF.

When no Markdown headings are found, a blank-sandwich fallback is used:
lines that are surrounded by blank lines (or file boundaries) on both
sides are treated as headings.  A whitespace-prevalence filter (75%
threshold) then drops candidates that don't match the dominant style
(indented vs. left-aligned), which separates RFC-style body paragraphs
from section titles and vice-versa.
"""

import re
from outliner.types import OutlineItem

SYNTAX = "markdown"
EXTENSIONS = frozenset({".md", ".markdown", ".mdown", ".mkd", ".txt", ".text"})

_ATX_RE = re.compile(r"^(#{1,6})(?:\s+(.*?))?\s*#*\s*$")
_ATX_START = re.compile(r"^#{1,6} ")
_SETEXT_RE = re.compile(r"^(=+|-+)\s*$")
_THRESHOLD = 0.75


def detect_content(lines: list[str]) -> bool:
    """Return True if content has ATX headings (unambiguous Markdown signal)."""
    return any(_ATX_START.match(line) for line in lines)


def _is_setext_underline(line: str) -> tuple[bool, int]:
    m = _SETEXT_RE.match(line)
    if not m:
        return False, 0
    return True, (1 if line.lstrip()[0] == "=" else 2)


def _heading_candidates(lines: list[str], start: int, end: int) -> list[tuple[int, str]]:
    """Return (0-based index, raw line) for blank-sandwiched lines in lines[start:end]."""
    out = []
    for i in range(start, end):
        s = lines[i]
        if not s.strip():
            continue
        before = (i == 0) or not lines[i - 1].strip()
        after  = (i == end - 1) or not lines[i + 1].strip()
        if before and after:
            out.append((i, s))
    return out


def _whitespace_filter(candidates: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Drop candidates that don't match the dominant indentation style."""
    if not candidates:
        return candidates
    n_indent = sum(1 for _, s in candidates if s[0:1] in (' ', '\t'))
    total = len(candidates)
    if n_indent / total >= _THRESHOLD:
        return [(i, s) for i, s in candidates if s[0:1] in (' ', '\t')]
    if (total - n_indent) / total >= _THRESHOLD:
        return [(i, s) for i, s in candidates if s[0:1] not in (' ', '\t')]
    return candidates


def _preamble_sig(lines: list[str], end: int) -> str:
    """Best signature for the preamble block (lines before index `end`).

    Re-runs heading candidate detection over the preamble; takes the first hit.
    Falls back to the first non-empty text line.
    """
    hits = _heading_candidates(lines, 0, end)
    if hits:
        return hits[0][1].strip()
    return next((l.strip() for l in lines[:end] if l.strip()), "")


def _items_from_headings(headings: list[tuple[int, str]], n: int) -> list[OutlineItem]:
    """Convert (0-based idx, signature) pairs into OutlineItems with ranges."""
    items = []
    for k, (line_idx, sig) in enumerate(headings):
        end_line = headings[k + 1][0] if k + 1 < len(headings) else n
        items.append(OutlineItem(
            start=line_idx + 1,
            count=end_line - line_idx,
            signature=sig,
        ))
    return items


def _sandwich_fallback(lines: list[str]) -> list[OutlineItem]:
    """Blank-sandwich heuristic for files with no Markdown headings."""
    n = len(lines)
    candidates = _heading_candidates(lines, 0, n)
    filtered = _whitespace_filter(candidates)

    if not filtered:
        first = next((l.strip() for l in lines if l.strip()), "")
        return [OutlineItem(start=1, count=n, signature=first)] if n else []

    # Build (idx, sig) list, prepending a preamble item if content precedes first heading.
    headings: list[tuple[int, str]] = [(i, s.strip()) for i, s in filtered]
    first_idx = headings[0][0]
    if any(lines[i].strip() for i in range(first_idx)):
        sig = _preamble_sig(lines, first_idx)
        headings = [(0, sig)] + headings

    return _items_from_headings(headings, n)


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines(keepends=True)
    n = len(lines)

    # --- collect Markdown headings ---
    md_headings: list[tuple[int, int, str]] = []  # (0-based idx, level, sig)
    i = 0
    while i < n:
        line = lines[i].rstrip('\r\n')

        m = _ATX_RE.match(line)
        if m:
            level = len(m.group(1))
            sig = (m.group(2) or "").strip()
            md_headings.append((i, level, sig))
            i += 1
            continue

        if i + 1 < n:
            is_ul, level = _is_setext_underline(lines[i + 1])
            stripped = line.strip()
            if is_ul and stripped and not stripped.startswith("#"):
                md_headings.append((i, level, stripped))
                i += 2
                continue

        i += 1

    if not md_headings:
        return _sandwich_fallback(lines)

    # --- compute ranges for Markdown headings ---
    items: list[OutlineItem] = []
    for idx, (line_idx, level, sig) in enumerate(md_headings):
        end_line = n
        for future_idx, future_level, _ in md_headings[idx + 1:]:
            if future_level <= level:
                end_line = future_idx
                break
        items.append(OutlineItem(
            start=line_idx + 1,
            count=end_line - line_idx,
            signature=sig,
        ))
    return items

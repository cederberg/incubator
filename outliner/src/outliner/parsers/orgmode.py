"""Org-mode outline parser.

Recognises headings prefixed with one or more `*` characters followed by a
space: ``* Top``, ``** Sub``, ``*** Deep``, …  The star count is the heading
level; the signature preserves the star prefix for native-format nesting.

Org extras stripped from signatures:
  - TODO/DONE state keywords (``* TODO Buy milk`` → ``* Buy milk``)
  - Priority cookies (``* [#A] Task`` → ``* Task``)
  - Trailing tags  (``* Heading :tag1:tag2:`` → ``* Heading``)

Content detection looks for Org-specific co-occurring markers:
  - ``#+TITLE:`` / ``#+AUTHOR:`` / ``#+DATE:`` directives (alone sufficient)
  - ``#+BEGIN_SRC`` / ``#+END_SRC`` blocks
  - Two or more ``*``-prefixed headings (single heading is too ambiguous)
"""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem
from outliner.parsers.util import extract_summary

SYNTAX = "orgmode"
EXTENSIONS = (".org",)

_HEADING_RE = re.compile(r"^(\*+)\s+(.+?)\s*$")
_DIRECTIVE_RE = re.compile(r"^\s*#[\+#]|^\s*# ", re.IGNORECASE)
_TITLE_DIRECTIVE_RE = re.compile(r"^\s*#\+(TITLE|AUTHOR|DATE|STARTUP|OPTIONS|FILETAGS):", re.IGNORECASE)
_BEGIN_END_RE = re.compile(r"^\s*#\+(BEGIN|END)_", re.IGNORECASE)
# Strips optional TODO/DONE keyword at start (case-sensitive: Org keywords are uppercase)
_TODO_RE = re.compile(r"^(TODO|DONE|FIXME|CANCELLED|WAITING|HOLD|NEXT|PROJ)\s+")
# Strips optional priority cookie [#A] at start
_PRIORITY_RE = re.compile(r"^\[#[A-Z]\]\s+")
# Strips statistics cookies [n/m] or [n%]
_STATS_RE = re.compile(r"\s*\[\d+/\d+\]|\s*\[\d+%\]")
# Strips trailing tags  :word1:word2:
_TAGS_RE = re.compile(r"\s+:[A-Za-z0-9_@#%:]+:\s*$")


def _clean_heading(stars: str, body: str) -> str:
    """Return the normalised signature for a heading."""
    body = _TODO_RE.sub("", body)
    body = _PRIORITY_RE.sub("", body)
    body = _STATS_RE.sub("", body)
    body = _TAGS_RE.sub("", body).strip()
    return stars + " " + body


def detect(lines: list[str]) -> bool:
    """Return True when content has unambiguous Org-mode markers.

    A ``#+TITLE:`` / ``#+AUTHOR:`` / ``#+BEGIN_SRC`` line alone is sufficient
    (these are Org-specific).  Two or more ``*``-prefixed headings together
    also constitute a strong signal.
    """
    heading_count = 0
    for line in lines:
        s = line.rstrip()
        if _TITLE_DIRECTIVE_RE.match(s):
            return True
        if _BEGIN_END_RE.match(s):
            return True
        if _HEADING_RE.match(s):
            heading_count += 1
            if heading_count >= 2:
                return True
    return False


def _preamble_sig(lines: list[str], end: int) -> str | None:
    """Return a signature for preamble content before index *end*, or None.

    Directive-only preambles (#+TITLE: etc.) are suppressed.
    """
    non_directive = [
        l.strip() for l in lines[:end]
        if l.strip() and not _DIRECTIVE_RE.match(l)
    ]
    if not non_directive:
        return None
    return extract_summary(non_directive[0])


def parse(text: str) -> Iterator[OutlineItem]:
    lines = text.splitlines(keepends=True)
    n = len(lines)

    headings: list[tuple[int, int, str]] = []  # (0-based idx, level, sig)

    for i, line in enumerate(lines):
        stripped = line.rstrip("\r\n")
        m = _HEADING_RE.match(stripped)
        if m:
            level = len(m.group(1))
            sig = _clean_heading(m.group(1), m.group(2))
            headings.append((i, level, sig))

    if not headings:
        first_sig = next(
            (l.strip() for l in lines if l.strip() and not _DIRECTIVE_RE.match(l)),
            next((l.strip() for l in lines if l.strip()), ""),
        )
        if first_sig:
            yield OutlineItem(start=1, count=n, signature=extract_summary(first_sig))
        return

    # Preamble item if non-directive content precedes first heading
    first_idx = headings[0][0]
    preamble_sig = _preamble_sig(lines, first_idx)
    if preamble_sig:
        yield OutlineItem(start=1, count=first_idx, signature=preamble_sig)

    for idx, (line_idx, level, sig) in enumerate(headings):
        end_line = n
        for future_line_idx, future_level, _ in headings[idx + 1:]:
            if future_level <= level:
                end_line = future_line_idx
                break
        yield OutlineItem(start=line_idx + 1, count=end_line - line_idx, signature=sig)

"""AsciiDoc outline parser.

Recognises ATX-style headings prefixed with one or more `=` characters
followed by a space (``= Title``, ``== Section``, ``=== Subsection``, …).
The number of `=` signs determines the heading level; level 0 (`=`) is
the document title.  Each heading's range extends to the line before the
next heading at the same or higher level (lower `=` count), or to EOF.

Content detection looks for AsciiDoc-specific co-occurring markers:
  - a document-title line (``= `` at column 0) together with attribute
    entries (``:attr:`` lines) or block macros (``[source,…]``, ``[NOTE]``,
    ``[TIP]``, etc.)
  - block macros alone are sufficient (``[source,lang]`` / ``[NOTE]``)
"""

import re
from outliner.types import OutlineItem
from outliner.parsers.util import extract_summary

SYNTAX = "asciidoc"
EXTENSIONS = (".adoc", ".asciidoc")

_HEADING_RE = re.compile(r"^(={1,6})\s+(.+?)\s*$")
_ATTR_ENTRY_RE = re.compile(r"^:!?[A-Za-z0-9_-]+:(?:\s|$)")
_BLOCK_MACRO_RE = re.compile(r"^\[(?:source|NOTE|TIP|WARNING|CAUTION|IMPORTANT|listing|example|quote|verse|sidebar|pass|abstract|partintro)[,\]]")


def detect(lines: list[str]) -> bool:
    """Return True when content has unambiguous AsciiDoc markers.

    We require co-occurring signals to avoid false-positives:
    - A ``= Document Title`` line (level-0 heading) plus at least one
      attribute entry or block macro; OR
    - A block macro (``[source,…]``, admonition) alone.
    """
    has_doc_title = False
    has_section = False
    has_attr = False
    has_block = False
    for line in lines:
        s = line.rstrip()
        if _BLOCK_MACRO_RE.match(s):
            has_block = True
        if _ATTR_ENTRY_RE.match(s):
            has_attr = True
        m = _HEADING_RE.match(s)
        if m:
            if len(m.group(1)) == 1:
                has_doc_title = True
            else:
                has_section = True
    if has_block:
        return True
    # Level-0 document title paired with attribute entries or section headings
    if has_doc_title and (has_attr or has_section):
        return True
    return False


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines(keepends=True)
    n = len(lines)

    headings: list[tuple[int, int, str]] = []  # (0-based idx, level, sig)

    for i, raw in enumerate(lines):
        stripped = raw.rstrip("\r\n")
        m = _HEADING_RE.match(stripped)
        if m:
            level = len(m.group(1))
            sig = "=" * level + " " + m.group(2)
            headings.append((i, level, sig))

    if not headings:
        # Fallback: first non-empty line spans the whole file
        first_sig = next((l.strip() for l in lines if l.strip()), "")
        if not first_sig:
            return []
        return [OutlineItem(start=1, count=n, signature=extract_summary(first_sig))]

    items: list[OutlineItem] = []
    for idx, (line_idx, level, sig) in enumerate(headings):
        end_line = n
        for future_line_idx, future_level, _ in headings[idx + 1:]:
            if future_level <= level:
                end_line = future_line_idx
                break
        items.append(OutlineItem(
            start=line_idx + 1,
            count=end_line - line_idx,
            signature=sig,
        ))

    return items

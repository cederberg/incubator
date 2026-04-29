"""reStructuredText outline parser.

Recognises headings formed by a text line followed by an underline of repeated
decoration characters (= - ~ ^ * + # < >).  The first decoration character seen
becomes level 1, the second distinct character becomes level 2, and so on — the
same level-assignment rule as docutils.

Overline+underline headings (same decoration above and below the text) are not
yet supported; plain underline headings cover all common RST documents.
"""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem
from outliner.parsers.util import extract_summary

SYNTAX = "rst"
EXTENSIONS = (".rst", ".rest")

_DECORATION_CHARS = frozenset("=-~^*+#<>")
_DIRECTIVE_RE = re.compile(r"^\.\. ")


def _underline_char(line: str, min_len: int = 1) -> str | None:
    """Return decoration char if *line* is a valid RST underline of length >= min_len."""
    s = line.rstrip()
    if len(s) < min_len or not s:
        return None
    c = s[0]
    if c not in _DECORATION_CHARS:
        return None
    if all(ch == c for ch in s):
        return c
    return None


def detect(lines: list[str]) -> bool:
    """Return True if content has strong RST signals not present in plain Markdown.

    We only trigger on unambiguous RST markers: directives (``.. ``) and
    decoration chars outside the ``=`` / ``-`` set.  Files that use only
    ``=`` and ``-`` underlines are left for the markdown catch-all — we must
    not false-detect RST on files that are valid (and more likely) Markdown.
    """
    for line in lines:
        stripped = line.strip()
        if _DIRECTIVE_RE.match(stripped):
            return True
        c = _underline_char(stripped)
        if c and c not in "=-":
            return True
    return False


def parse(text: str) -> Iterator[OutlineItem]:
    lines = text.splitlines(keepends=True)
    n = len(lines)

    level_map: dict[str, int] = {}
    headings: list[tuple[int, int, str]] = []  # (0-based line idx, level, sig)

    i = 0
    while i < n:
        line = lines[i].rstrip("\r\n")
        text_stripped = line.strip()

        if i + 1 < n:
            next_line = lines[i + 1].rstrip("\r\n")
            dec = _underline_char(next_line, len(line.strip()))
            if dec and text_stripped and _underline_char(line) is None:
                if dec not in level_map:
                    level_map[dec] = len(level_map) + 1
                level = level_map[dec]
                headings.append((i, level, text_stripped))
                i += 2
                continue

        i += 1

    # Preamble before first heading, or whole-file item when there are no headings.
    # Decoration-only lines (e.g. overlines in overline+underline headings) are
    # skipped so they don't pollute the preamble signature or create phantom items.
    first_idx = headings[0][0] if headings else n
    if any(lines[k].strip() for k in range(first_idx)):
        sig = next(
            (lines[k].strip() for k in range(first_idx)
             if lines[k].strip() and not _underline_char(lines[k].strip())),
            None,
        )
        if sig is not None:
            sig = extract_summary(sig)
        if sig:
            yield OutlineItem(start=1, count=first_idx, signature=sig)

    for idx, (line_idx, level, sig) in enumerate(headings):
        end_line = n
        for future_line_idx, future_level, _ in headings[idx + 1:]:
            if future_level <= level:
                end_line = future_line_idx
                break
        yield OutlineItem(start=line_idx + 1, count=end_line - line_idx, signature="  " * (level - 1) + sig)

"""reStructuredText outline parser.

Recognises headings formed by a text line followed by an underline of repeated
decoration characters (= - ~ ^ * + # < >).  The first decoration character seen
becomes level 1, the second distinct character becomes level 2, and so on — the
same level-assignment rule as docutils.

Overline+underline headings (same decoration above and below the text) are not
yet supported; plain underline headings cover all common RST documents.
"""

import re
from outliner.types import OutlineItem

SYNTAX = "rst"
EXTENSIONS = frozenset({".rst", ".rest"})

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
    """Return True if content has strong RST signals not present in plain Markdown."""
    for line in lines:
        stripped = line.strip()
        if _DIRECTIVE_RE.match(stripped):
            return True
        c = _underline_char(stripped)
        if c and c not in "=-":
            return True
    return False


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines(keepends=True)
    n = len(lines)

    level_map: dict[str, int] = {}
    headings: list[tuple[int, int, str]] = []  # (0-based line idx, level, sig)

    i = 0
    while i < n:
        raw = lines[i].rstrip("\r\n")
        text_stripped = raw.strip()

        if i + 1 < n:
            next_raw = lines[i + 1].rstrip("\r\n")
            dec = _underline_char(next_raw, len(raw.rstrip()))
            if dec and text_stripped and _underline_char(raw) is None:
                if dec not in level_map:
                    level_map[dec] = len(level_map) + 1
                level = level_map[dec]
                headings.append((i, level, text_stripped))
                i += 2
                continue

        i += 1

    items: list[OutlineItem] = []

    # Preamble before first heading, or whole-file item when there are no headings.
    first_idx = headings[0][0] if headings else n
    if any(lines[k].strip() for k in range(first_idx)):
        sig = next(lines[k].strip() for k in range(first_idx) if lines[k].strip())
        items.append(OutlineItem(start=1, count=first_idx, signature=sig))

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

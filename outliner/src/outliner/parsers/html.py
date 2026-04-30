"""HTML outline parser.

Recognises <head> and <body> as depth-0 structural elements; h1–h6
headings with depth equal to the heading level (2 spaces per level);
and semantic landmark elements (<nav>, <main>, <article>, <section>) at
depth 1 (2 spaces, inside body).

Signature format:
  <head>                    depth 0
  <body>                    depth 0
    <h1>Title</h1>          depth 1  (2 spaces)
      <h2>Sub</h2>          depth 2  (4 spaces)
  <nav>                     depth 1
  <section#id>              depth 1

Heading ranges extend to the next same-or-higher-level heading;
landmark and structural ranges extend to the matching closing tag.

Regex-based, covering ~90-95% of real-world HTML.  Known limitations:
tags whose attributes contain '>', and multiple headings on the same
minified line.
"""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem

SYNTAX = "html"
EXTENSIONS = (".html", ".htm", ".xhtml")

# Match start of heading tag — '>' may be on a later line
_HEADING_START_RE  = re.compile(r'<h([1-6])\b', re.IGNORECASE)
_HEADING_CLOSE_RE  = re.compile(r'</h[1-6]\s*>', re.IGNORECASE)
_TAG_RE            = re.compile(r'<[^>]+>')
_WS_RE             = re.compile(r'\s+')
_ENTITY_RE         = re.compile(r'&(?:([a-zA-Z]\w+)|#x([0-9a-fA-F]+)|#(\d+));')
_DOCTYPE_RE        = re.compile(r'^\s*<!DOCTYPE\s+html', re.IGNORECASE)
_HTML_TAG_RE       = re.compile(r'^\s*<html[\s>]', re.IGNORECASE)
_LANDMARK_START_RE = re.compile(r'<(section|article|main|nav)\b', re.IGNORECASE)
_STRUCTURAL_START_RE = re.compile(r'<(head|body)\b', re.IGNORECASE)
_ATTR_ID_RE        = re.compile(r'\bid=["\']([^"\']+)["\']')
# \b lets us match <script or <script\n... (tag name at end of line)
_SKIP_OPEN_RE      = re.compile(r'<(script|style)\b', re.IGNORECASE)
_SKIP_CLOSE_RE     = re.compile(r'</(script|style)\s*>', re.IGNORECASE)

# Pre-compiled open/close patterns for nesting-aware close search
_BLOCK_RES: dict[str, tuple[re.Pattern, re.Pattern]] = {
    tag: (re.compile(rf'<{tag}\b', re.IGNORECASE),
          re.compile(rf'</{tag}\s*>', re.IGNORECASE))
    for tag in ('head', 'body', 'section', 'article', 'main', 'nav')
}

_NAMED_ENTITIES: dict[str, str] = {
    'amp': '&', 'lt': '<', 'gt': '>', 'quot': '"', 'apos': "'",
    'nbsp': ' ', 'copy': '©', 'reg': '®', 'trade': '™',
    'mdash': '—', 'ndash': '–',
    'ldquo': '“', 'rdquo': '”', 'lsquo': '‘', 'rsquo': '’',
    'hellip': '…', 'bull': '•', 'euro': '€', 'pound': '£', 'yen': '¥',
    'times': '×', 'divide': '÷', 'plusmn': '±', 'frac12': '½',
}


def _decode_entity(m: re.Match) -> str:
    if m.group(1):
        return _NAMED_ENTITIES.get(m.group(1), m.group(0))
    try:
        return chr(int(m.group(2), 16) if m.group(2) else int(m.group(3)))
    except (ValueError, OverflowError):
        return m.group(0)


def _clean(text: str) -> str:
    """Strip HTML tags, decode entities, normalise whitespace.

    Tags are replaced with a space so adjacent words don't merge
    (e.g. <h1>Foo<small>bar</small></h1> → 'Foo bar', not 'Foobar').
    """
    return _WS_RE.sub(' ', _ENTITY_RE.sub(_decode_entity, _TAG_RE.sub(' ', text))).strip()


def _parse_tag_open(lines: list[str], i: int, col: int) -> tuple[str, bool, int, int]:
    """Scan forward from (line i, col) until '>' is found.

    Returns (attrs_text, is_self_closing, end_line, col_after_gt).
    Looks at most 20 lines ahead (enough for any real-world tag).
    """
    parts: list[str] = []
    for j in range(i, min(i + 20, len(lines))):
        seg = lines[j][col if j == i else 0:]
        gt = seg.find('>')
        if gt >= 0:
            parts.append(seg[:gt])
            attrs = ' '.join(parts)
            col_gt = (col if j == i else 0) + gt
            return attrs, attrs.rstrip().endswith('/'), j, col_gt + 1
        parts.append(seg)
    return '', False, i, len(lines[i])


def _block_sig(tag: str, attrs: str) -> str:
    """Return bare signature token (no indentation) for a block element."""
    tag = tag.lower()
    m = _ATTR_ID_RE.search(attrs)
    if m:
        return f'<{tag}#{m.group(1)}>'
    return f'<{tag}>'


def _find_close(lines: list[str], i: int, open_re: re.Pattern, close_re: re.Pattern) -> int:
    """Return exclusive-end line index j for the block element opening at line i."""
    depth, j = 1, i + 1
    while j < len(lines) and depth > 0:
        if open_re.search(lines[j]):
            depth += 1
        if close_re.search(lines[j]):
            depth -= 1
        j += 1
    return j


def _collect_blocks(lines: list[str], start_re: re.Pattern, indent: str,
                    result: list[OutlineItem]) -> None:
    """Scan lines for block elements matching start_re; append OutlineItems to result."""
    n = len(lines)
    i = 0
    while i < n:
        m = start_re.search(lines[i])
        if m:
            tag = m.group(1).lower()
            attrs, is_self_closing, _, _ = _parse_tag_open(lines, i, m.end())
            sig = indent + _block_sig(tag, attrs)
            if is_self_closing:
                result.append(OutlineItem(start=i + 1, count=1, signature=sig))
            else:
                open_pat, close_pat = _BLOCK_RES[tag]
                j = _find_close(lines, i, open_pat, close_pat)
                result.append(OutlineItem(start=i + 1, count=j - i, signature=sig))
        i += 1


def detect(lines: list[str]) -> bool:
    for line in lines[:30]:
        if _DOCTYPE_RE.match(line) or _HTML_TAG_RE.match(line):
            return True
    return False


def parse(text: str) -> Iterator[OutlineItem]:
    lines = text.splitlines()
    n = len(lines)
    result: list[OutlineItem] = []

    # --- collect headings, skipping <script> and <style> blocks ---
    headings: list[tuple[int, int, str]] = []  # (0-based start, level, sig)
    in_skip = False
    i = 0
    while i < n:
        line = lines[i]
        if in_skip:
            if _SKIP_CLOSE_RE.search(line):
                in_skip = False
            i += 1
            continue
        skip_m = _SKIP_OPEN_RE.search(line)
        if skip_m:
            if not _SKIP_CLOSE_RE.search(line):
                in_skip = True
            i += 1
            continue

        m = _HEADING_START_RE.search(line)
        if m:
            level = int(m.group(1))
            # Scan forward to find '>' — handles multi-line opening tags
            attrs, _, j_open, content_col = _parse_tag_open(lines, i, m.end())
            tail = lines[j_open][content_col:]
            close_m = _HEADING_CLOSE_RE.search(tail)
            if close_m:
                # Content and closing tag are on j_open
                sig_text = _clean(tail[:close_m.start()])
                j = j_open
            else:
                # Accumulate lines after j_open until </hN>
                parts = [tail]
                j = j_open + 1
                while j < n and not _HEADING_CLOSE_RE.search(lines[j]):
                    parts.append(lines[j])
                    j += 1
                if j < n:
                    before = re.split(r'</h[1-6]\s*>', lines[j], flags=re.IGNORECASE)[0]
                    parts.append(before)
                sig_text = _clean(' '.join(parts))
            indent = '  ' * level
            sig = f'{indent}<h{level}>{sig_text}</h{level}>'
            headings.append((i, level, sig))
            i = j + 1
            continue
        i += 1

    # Heading ranges: extend to next same-or-higher-level heading
    for idx, (line_idx, level, sig) in enumerate(headings):
        end_line = n
        for future_idx, future_level, _ in headings[idx + 1:]:
            if future_level <= level:
                end_line = future_idx
                break
        result.append(OutlineItem(start=line_idx + 1, count=end_line - line_idx, signature=sig))

    # --- structural elements: <head> and <body> at depth 0 ---
    _collect_blocks(lines, _STRUCTURAL_START_RE, '', result)

    # --- body-level landmarks: <nav>, <main>, <article>, <section> at depth 1 ---
    _collect_blocks(lines, _LANDMARK_START_RE, '  ', result)

    result.sort(key=lambda it: it.start)
    yield from result

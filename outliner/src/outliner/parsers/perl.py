"""Perl outline parser (regex-based)."""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end

SYNTAX = "perl"
EXTENSIONS = (".pl", ".pm", ".t")

_SHEBANG_RE = re.compile(r"^#!.*perl", re.IGNORECASE)
_PACKAGE_RE = re.compile(r"^\s*package\s+([\w:]+)\s*(?:;|\{)")
_SUB_RE = re.compile(r"^\s*sub\s+(\w+)\s*")
# Perl-specific co-occurrence markers for conservative detection
_USE_STRICT_RE = re.compile(r"^\s*use\s+(?:strict|warnings)\b")
_PACKAGE_DCOLON_RE = re.compile(r"^\s*package\s+\w+::")

_MAX_SIG_LINES = 20
# POD block boundaries: start on =word, end on =cut
_POD_START_RE = re.compile(r"^=[a-zA-Z]")
_POD_END_RE = re.compile(r"^=cut\b")


def detect(lines: list[str]) -> bool:
    """Detect Perl: shebang, or (use strict/warnings | package Foo::Bar) + sub."""
    for line in lines[:3]:
        if _SHEBANG_RE.match(line):
            return True
    has_sub = any(_SUB_RE.match(l) for l in lines)
    has_marker = any(
        _USE_STRICT_RE.match(l) or _PACKAGE_DCOLON_RE.match(l) for l in lines
    )
    return has_sub and has_marker


def _collect_sub_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect sub signature up to and including the opening brace.

    Tracks paren depth for Perl 5.20+ signatures (sub name ($x, $y) { ... }).
    Returns (indented_signature, last_sig_line_0based, has_body).
    """
    ind = " " * indent_level(lines[start])
    depth = 0
    has_paren = False
    found_brace = False
    parts: list[str] = []
    end = min(start + _MAX_SIG_LINES, len(lines))
    for i in range(start, end):
        raw = lines[i]
        text = raw.lstrip() if i == start else raw.strip()
        for ch in raw:
            if ch == "(":
                depth += 1
                has_paren = True
            elif ch == ")":
                depth -= 1
        parts.append(text)
        if "{" in raw and (not has_paren or depth <= 0):
            found_brace = True
            break
        # Stop at prototype/forward declaration (sub foo; or sub foo ($x);)
        if raw.rstrip().endswith(";") and (not has_paren or depth <= 0):
            break
    # Truncate the last collected part at the opening brace so inline
    # bodies (sub foo { ... }) don't bleed into the signature.
    if parts:
        brace_idx = parts[-1].find("{")
        if brace_idx >= 0:
            parts[-1] = parts[-1][:brace_idx]
    return ind + extract_signature(parts), i, found_brace


def parse(text: str) -> Iterator[OutlineItem]:
    in_pod = False
    for i, line in enumerate(lines := text.splitlines()):
        if in_pod:
            if _POD_END_RE.match(line):
                in_pod = False
            continue
        if _POD_START_RE.match(line):
            in_pod = True
            continue

        def_ind = indent_level(line)
        _is_comment = lambda ln, s, d=def_ind: indent_level(ln) >= d and s[0] == "#"

        if _PACKAGE_RE.match(line):
            ind = " " * def_ind
            sig = ind + extract_signature([line.strip()], strip=";{")
            start = seek_comment_start(lines, i, _is_comment)
            end = seek_brace_end(lines, i) if "{" in line else i + 1
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)

        elif _SUB_RE.match(line):
            sig, sig_end, has_body = _collect_sub_sig(lines, i)
            if has_body:
                start = seek_comment_start(lines, i, _is_comment)
                end = seek_brace_end(lines, sig_end)
                yield OutlineItem(start=start + 1, count=end - start, signature=sig)

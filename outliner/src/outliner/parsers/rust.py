"""Rust outline parser (regex-based)."""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end

SYNTAX = "rust"
EXTENSIONS = (".rs",)

# Visibility + fn modifiers
_VIS = r"(?:pub(?:\([^)]*\))?\s+)?"
_FN_MODS = r"(?:default\s+)?(?:const\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+(?:\"[^\"]*\"\s+)?)?"

_FN_RE    = re.compile(r"^\s*" + _VIS + _FN_MODS + r"fn\s+\w+")
_STRUCT_RE = re.compile(r"^\s*" + _VIS + r"(?:unsafe\s+)?struct\s+\w+")
_ENUM_RE   = re.compile(r"^\s*" + _VIS + r"enum\s+\w+")
_TRAIT_RE  = re.compile(r"^\s*" + _VIS + r"(?:unsafe\s+)?(?:auto\s+)?trait\s+\w+")
_IMPL_RE   = re.compile(r"^\s*(?:unsafe\s+)?impl\b")
_MOD_RE    = re.compile(r"^\s*" + _VIS + r"mod\s+\w+")
_TYPE_RE   = re.compile(r"^\s*" + _VIS + r"type\s+\w+")

_ALL_DECLS = [_FN_RE, _STRUCT_RE, _ENUM_RE, _TRAIT_RE, _IMPL_RE, _MOD_RE, _TYPE_RE]

# Detection helpers
_FN_DETECT_RE  = re.compile(r"^\s*" + _VIS + r"(?:async\s+)?(?:unsafe\s+)?fn\s+\w+")
_IMPL_DETECT_RE = re.compile(r"^\s*(?:unsafe\s+)?impl\b")
_DERIVE_RE     = re.compile(r"#\[derive\(")


def detect(lines: list[str]) -> bool:
    """Detect Rust: fn keyword combined with impl block, return arrow, or derive attribute."""
    has_fn = any(_FN_DETECT_RE.match(l) for l in lines)
    has_marker = any(
        _IMPL_DETECT_RE.match(l) or _DERIVE_RE.search(l) or "->" in l
        for l in lines
    )
    return has_fn and has_marker


def _collect_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a possibly multi-line Rust signature.

    Tracks parenthesis depth; stops when depth is balanced and line ends with
    { (has body) or ; (no body, e.g. trait method or type alias).
    Returns (signature, last_sig_line_0based, has_body).
    """
    depth = 0
    parts: list[str] = []
    ind = " " * indent_level(lines[start])
    has_body = False
    for i in range(start, len(lines)):
        raw = lines[i]
        for ch in raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        parts.append(raw.strip())
        if depth <= 0:
            stripped = raw.rstrip()
            if stripped.endswith("{"):
                has_body = True
                break
            if stripped.endswith(";"):
                break
    sig = extract_signature(parts, strip="{;")
    # Remove trailing comma left by a where-clause when { was on its own line
    if sig.endswith(","):
        sig = sig.rstrip(",").rstrip()
    return ind + sig, i, has_body


def parse(text: str) -> Iterator[OutlineItem]:
    for i, line in enumerate(lines := text.splitlines()):
        if any(r.match(line) for r in _ALL_DECLS):
            sig, sig_end, has_body = _collect_sig(lines, i)
            is_comment_chr = lambda _, s: s[0] in "/#*"
            start = seek_comment_start(lines, i, is_comment_chr)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)

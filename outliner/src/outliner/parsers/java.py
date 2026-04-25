"""Java outline parser (regex-based)."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end

SYNTAX = "java"
EXTENSIONS = (".java",)

_PACKAGE_RE = re.compile(r"^\s*package\s+[\w.]+\s*;")
_IMPORT_SKIP_RE = re.compile(r"^\s*import\s+")
_IMPORT_DETECT_RE = re.compile(r"^\s*import\s+[\w.*]+\s*;")

# Type declarations: class, interface, enum, record, @interface
_TYPE_RE = re.compile(
    r"^\s*(?:(?:public|protected|private|static|abstract|final|sealed|non-sealed|strictfp)\s+)*"
    r"(@\s*interface|interface|class|enum|record)\s+\w+"
)

# Method/constructor detection — control flow keywords that must not be the captured name
_CONTROL_FLOW = frozenset({
    "if", "else", "while", "for", "do", "switch", "case", "try", "catch",
    "finally", "return", "throw", "assert", "new", "super", "this",
    "break", "continue", "instanceof", "synchronized",
})

# Statement starters that make a line definitely not a declaration
_STMT_START_RE = re.compile(r"^\s*(?:return|throw|break|continue|assert)\b")

# A method/constructor declaration starts with optional modifiers + optional return type + name(
# Note: generic type-params group uses [^(] (not [^(>]) so backtracking correctly
# handles nested bounds like <T extends Comparable<T>>.
_METHOD_RE = re.compile(
    r"^\s*"
    r"(?:(?:public|protected|private|static|abstract|final|native|synchronized|strictfp|default|transient|volatile)\s+)*"
    r"(?:<[^(]*>\s*)?"                               # optional generic type params on method
    r"(?:(?:void|[\w$][\w$]*(?:<[^(]*>)?(?:\[\])*)\s+)?"  # optional return type
    r"([\w$]+)\s*\("                                 # method name (captured in group 1)
)

# Conservative content detection
_JAVA_DECL_RE = re.compile(r"\b(?:class|interface|enum|record)\s+\w+[^{]*\{")
_AT_IFACE_RE = re.compile(r"@\s*interface\s+\w+[^{]*\{")


def detect(lines: list[str]) -> bool:
    """Detect Java: requires package/import statement AND a type declaration."""
    has_java_marker = any(
        _PACKAGE_RE.match(l) or _IMPORT_DETECT_RE.match(l) for l in lines
    )
    has_type = any(_JAVA_DECL_RE.search(l) or _AT_IFACE_RE.search(l) for l in lines)
    return has_java_marker and has_type


def _collect_sig(lines: list[str], start: int, n: int) -> tuple[str, int, bool]:
    """Collect a possibly multi-line Java signature.

    Tracks parenthesis depth; stops when balanced and line ends with { or ;.
    Returns (signature, last_sig_line_0based, has_body).
    """
    depth = 0
    parts: list[str] = []
    i = start
    ind = " " * indent_level(lines[start])
    has_body = False
    while i < n:
        raw = lines[i].rstrip("\r\n")
        for ch in raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        parts.append(raw.strip())
        stripped = raw.rstrip()
        if depth <= 0:
            if stripped.endswith("{"):
                has_body = True
                break
            if stripped.endswith(";"):
                break
        i += 1
    return ind + extract_signature(parts, strip="{;"), i, has_body


def _is_method_line(raw: str) -> bool:
    """Return True if line looks like a method or constructor declaration."""
    if _STMT_START_RE.match(raw):
        return False
    m = _METHOD_RE.match(raw)
    if m is None:
        return False
    name = m.group(1)
    return name not in _CONTROL_FLOW


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines(keepends=True)
    n = len(lines)
    items: list[OutlineItem] = []
    i = 0
    while i < n:
        raw = lines[i].rstrip("\r\n")

        if _IMPORT_SKIP_RE.match(raw) or _PACKAGE_RE.match(raw):
            i += 1
            continue

        if _TYPE_RE.match(raw) or _is_method_line(raw):
            sig, sig_end, has_body = _collect_sig(lines, i, n)
            start = seek_comment_start(lines, i, lambda _, s: s[0] in "/*@")
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i += 1
            continue

        i += 1

    return items

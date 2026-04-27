"""PHP outline parser (regex-based)."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end

SYNTAX = "php"
EXTENSIONS = (".php", ".phtml", ".php3", ".php4", ".php5", ".phps")

_OPEN_TAG_RE = re.compile(r"<\?php\b", re.IGNORECASE)
_PHP_VAR_RE = re.compile(r"^\s*\$[a-zA-Z_]\w*")
_NAMED_FUNC_RE = re.compile(r"\bfunction\s+\w+\s*\(")

_NAMESPACE_RE = re.compile(r"^\s*namespace\s+[\w\\]+")
_USE_RE = re.compile(r"^\s*use\b")

_TYPE_RE = re.compile(
    r"^\s*(?:(?:abstract|final|readonly)\s+)*"
    r"(?:class|interface|trait|enum)\s+\w+"
)

_FUNC_RE = re.compile(
    r"^\s*"
    r"(?:(?:abstract|public|protected|private|static|final|readonly)\s+)*"
    r"function\s+\w+"
)


def detect(lines: list[str]) -> bool:
    """Detect PHP: <?php open tag, or $variables + named function declarations."""
    for line in lines[:5]:
        if _OPEN_TAG_RE.search(line):
            return True
    has_var = any(_PHP_VAR_RE.match(l) for l in lines)
    has_func = any(_NAMED_FUNC_RE.search(l) for l in lines)
    return has_var and has_func


def _collect_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a possibly multi-line PHP signature.

    Tracks parenthesis depth; stops when balanced. Parentheses inside string
    literals may confuse the depth counter, which is an accepted limitation.
    Returns (signature, brace_line_0based, has_body). brace_line points to
    the line containing the opening '{'; for bodyless items (abstract/interface
    methods, namespace) it points to the last signature line.
    """
    depth = 0
    parts: list[str] = []
    ind = " " * indent_level(lines[start])
    i = start
    for i in range(start, min(start + 40, len(lines))):
        raw = lines[i]
        for ch in raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        parts.append(raw.strip())
        if depth <= 0:
            break

    sig_end = i
    raw_end = lines[sig_end]

    if "{" in raw_end:
        has_body, brace_line = True, sig_end
    elif raw_end.rstrip().endswith(";"):
        has_body, brace_line = False, sig_end
    else:
        # Allman-style brace: '{' on the next non-blank line (may have trailing comment)
        has_body, brace_line = False, sig_end
        for j in range(sig_end + 1, min(sig_end + 3, len(lines))):
            s = lines[j].strip()
            if s.startswith("{"):
                has_body, brace_line = True, j
                break
            elif s:
                break

    sig = ind + extract_signature(parts, strip="{;")
    return sig, brace_line, has_body


def _is_walkback_line(line: str, s: str) -> bool:
    if not s:
        return False
    return s[0] in "/*#" or s.startswith("//")


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines()
    items: list[OutlineItem] = []

    for i, raw in enumerate(lines):
        if _USE_RE.match(raw):
            continue

        if _NAMESPACE_RE.match(raw) or _TYPE_RE.match(raw) or _FUNC_RE.match(raw):
            sig, brace_line, has_body = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_walkback_line)
            end = seek_brace_end(lines, brace_line) if has_body else brace_line + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))

    return items

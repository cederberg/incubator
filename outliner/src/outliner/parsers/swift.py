"""Swift outline parser (regex-based)."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end

SYNTAX = "swift"
EXTENSIONS = (".swift",)

# Access modifiers and declaration modifiers
_ACCESS = r"(?:(?:public|open|internal|fileprivate|private)(?:\([^)]*\))?\s+)*"
_MODS = (
    r"(?:(?:static|class|final|override|required|convenience|mutating|nonmutating"
    r"|dynamic|lazy|nonisolated(?:\([^)]*\))?|isolated|async|weak|unowned|indirect"
    r"|@\w+(?:\([^)]*\))?)\s+)*"
)
_FULL_MODS = _ACCESS + _MODS

# Declaration patterns
# func name OR operator (e.g. ==, +, <=)
_FUNC_RE = re.compile(r"^\s*" + _FULL_MODS + r"func\s+(?:\w+|[+\-*/=<>!&|^~%?.]+)")
_INIT_RE = re.compile(r"^\s*" + _FULL_MODS + r"init[?!]?\s*[<(]")
_DEINIT_RE = re.compile(r"^\s*deinit\s*\{")
# Negative lookahead prevents "class var/let/func" from matching as a type decl
_TYPE_RE = re.compile(r"^\s*" + _FULL_MODS + r"(?:class|struct|enum|protocol|actor)\s+(?!(?:var|let|func|init)\b)\w+")
_EXT_RE = re.compile(r"^\s*(?:(?:public|internal|private|fileprivate)\s+)*extension\s+\w+")

# Detection helpers — require fileprivate before a known Swift declaration keyword
_FILEPRIVATE_RE = re.compile(r"\bfileprivate\s+(?:func|var|let|class|struct|enum|protocol|init|extension|typealias)\b")
_ACTOR_RE = re.compile(r"^\s*(?:(?:public|internal|private|fileprivate|open)\s+)*actor\s+\w+", re.MULTILINE)
_OPEN_ACCESS_RE = re.compile(r"\bopen\s+(?:class|func|var)\b")
_SWIFT_FUNC_RE = re.compile(r"\bfunc\s+\w+")
# func with labeled parameters (colon notation) — unique to Swift vs Go's "name type" style
_SWIFT_PARAM_RE = re.compile(r"\bfunc\s+\w+\s*\([^)]*\w+\s*:\s*\w")
_IMPORT_RE = re.compile(r"^\s*import\s+\w+")


def detect(lines: list[str]) -> bool:
    """Detect Swift: fileprivate before a decl keyword, actor declaration, open access,
    or func with colon-labeled parameters (Swift's name:Type notation distinguishes from Go)."""
    text = "\n".join(lines)
    # fileprivate followed by a declaration keyword is unique to Swift
    if _FILEPRIVATE_RE.search(text):
        return True
    # actor as a declaration keyword is unique to Swift
    if _ACTOR_RE.search(text):
        return True
    has_func = bool(_SWIFT_FUNC_RE.search(text))
    if not has_func:
        return False
    # Go also uses func but uses "name type" not "label: Type"
    if _SWIFT_PARAM_RE.search(text):
        return True
    # open as an access modifier is unique to Swift
    if _OPEN_ACCESS_RE.search(text):
        return True
    return False


def _collect_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a possibly multi-line Swift signature.

    Tracks parenthesis depth; stops when balanced and the line contains {
    or ends with ; (protocol method), or parens close and next non-blank
    line has { (body on next line).
    Returns (signature, last_sig_line_0based, has_body).
    """
    depth = 0
    paren_opened = False
    parts: list[str] = []
    ind = " " * indent_level(lines[start])
    has_body = False
    i = start
    for i in range(start, len(lines)):
        raw = lines[i]
        for ch in raw:
            if ch == "(":
                depth += 1
                paren_opened = True
            elif ch == ")":
                depth -= 1
        parts.append(raw.strip())
        if depth <= 0:
            if "{" in raw:
                has_body = True
                break
            if raw.rstrip().endswith(";"):
                break
            if paren_opened:
                # Look ahead for { on the next non-blank line (body on next line)
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and lines[j].strip().startswith("{"):
                    has_body = True
                break
    sig = ind + extract_signature(parts, strip="{;")
    # Strip inline body — in Swift, { never appears inside a valid type signature
    sig = re.sub(r"\s*\{.*$", "", sig)
    return sig, i, has_body


def _is_comment_or_attr(line: str, s: str) -> bool:
    return bool(s) and (
        s.startswith("//")
        or s.startswith("/*")
        or s[0] == "*"
        or s[0] == "@"
    )


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines()
    n = len(lines)
    items: list[OutlineItem] = []
    i = 0

    while i < n:
        raw = lines[i]
        s = raw.strip()

        # Skip blank/comment lines and import statements
        if not s or s.startswith("//") or s.startswith("/*") or s[:1] == "*":
            i += 1
            continue
        if _IMPORT_RE.match(raw):
            i += 1
            continue

        # deinit has no parens — handle specially
        if _DEINIT_RE.match(raw):
            sig = " " * indent_level(raw) + "deinit"
            start = seek_comment_start(lines, i, _is_comment_or_attr)
            end = seek_brace_end(lines, i)
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i = end  # skip body; deinit cannot contain nested decls
            continue

        if any(r.match(raw) for r in [_FUNC_RE, _INIT_RE, _TYPE_RE, _EXT_RE]):
            sig, sig_end, has_body = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_comment_or_attr)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i += 1  # advance one line; body is re-scanned for nested decls
            continue

        i += 1

    return items

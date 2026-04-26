"""C# outline parser (regex-based)."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end

SYNTAX = "csharp"
EXTENSIONS = (".cs",)

# Detection: require using/namespace AND a type declaration
_USING_RE = re.compile(r"^\s*(?:global\s+)?using\s+[\w.]+")
_NS_RE = re.compile(r"^\s*namespace\s+[\w.]+")
_TYPE_DETECT_RE = re.compile(r"\b(?:class|interface|struct|enum|record|delegate)\s+\w+")

# Type declarations (class, interface, struct, enum, record, delegate)
_TYPE_RE = re.compile(
    r"^\s*"
    r"(?:(?:public|protected|internal|private|static|abstract|sealed|partial|readonly|unsafe|new)\s+)*"
    r"(?:"
    r"record\s+(?:class|struct)\s+\w+"
    r"|record\s+\w+"
    r"|class\s+\w+"
    r"|interface\s+\w+"
    r"|struct\s+\w+"
    r"|enum\s+\w+"
    r"|delegate\s+\S+\s+\w+"      # delegate ReturnType Name
    r")"
)

# Namespace
_NAMESPACE_RE = re.compile(r"^\s*(?:file\s+)?namespace\s+[\w.]+")

_CONTROL_FLOW = frozenset({
    "if", "else", "while", "for", "foreach", "do", "switch", "case",
    "return", "throw", "catch", "finally", "try", "using", "lock",
    "fixed", "checked", "unchecked", "sizeof", "typeof", "new",
    "break", "continue", "goto", "yield",
})

_STMT_START_RE = re.compile(r"^\s*(?:return|throw|break|continue|goto|yield)\b")
_ASSIGN_RE = re.compile(r"(?<![=!<>])=(?!=)")

# Explicit interface implementation: "Type IfaceName.Method(" — the name contains a dot
_EXPLICIT_IFACE_RE = re.compile(
    r"^\s*"
    r"(?:(?:public|protected|internal|private|static|abstract|virtual|override|sealed|"
    r"async|extern|new|partial|readonly|unsafe|volatile)\s+)*"
    r"(?:~?\w[\w.<>,\[\] ]*?\s+)?"       # optional return type
    r"(~?(?:\w+\.)+\w+)\s*(?:<[^(]*>)?\s*\("  # qualified name like IFoo.Bar
)

_METHOD_RE = re.compile(
    r"^\s*"
    r"(?:(?:public|protected|internal|private|static|abstract|virtual|override|sealed|"
    r"async|extern|new|partial|readonly|unsafe|volatile)\s+)*"
    r"(?:~?\w[\w.<>,\[\] ]*?\s+)?"     # optional return type
    r"(~?\w+)\s*(?:<[^(]*>)?\s*\("     # method name captured in group 1
)

# Property: modifiers + type + name + { or => (same line)
_PROPERTY_RE = re.compile(
    r"^\s*"
    r"(?:(?:public|protected|internal|private|static|abstract|virtual|override|sealed|"
    r"new|readonly|required|unsafe)\s+)*"
    r"(?:[\w.<>,\[\]?]+\s+){1,3}"
    r"(\w+)\s*(?:\{|=>)"
)
# Property name on its own line (body brace on next line)
_PROPERTY_NAME_RE = re.compile(
    r"^\s*"
    r"(?:(?:public|protected|internal|private|static|abstract|virtual|override|sealed|"
    r"new|readonly|required|unsafe)\s+)*"
    r"(?:[\w.<>,\[\]?]+\s+){1,3}"
    r"(\w+)\s*$"
)

_ATTR_RE = re.compile(r"^\s*\[")


def detect(lines: list[str]) -> bool:
    """Detect C#: requires using/namespace AND a type declaration."""
    has_cs_marker = any(_USING_RE.match(l) or _NS_RE.match(l) for l in lines)
    has_type = any(_TYPE_DETECT_RE.search(l) for l in lines)
    return has_cs_marker and has_type


def _collect_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a possibly multi-line C# signature.

    Tracks parenthesis depth; stops when parens close and the line ends with
    { (has body), ; (abstract/interface method), => (expression body), or
    the closing ) itself (body on next line, detected via look-ahead).
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
            if "=>" in raw:
                break
            if paren_opened:
                # Look ahead for { on the next non-blank line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and lines[j].strip().startswith("{"):
                    has_body = True
                break
    sig = ind + extract_signature(parts, strip="{;")
    sig = re.sub(r"\s*=>.*$", "", sig).rstrip()
    return sig, i, has_body


def _collect_prop_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a property signature. Returns (signature, last_line_0based, has_body)."""
    raw = lines[start]
    ind = " " * indent_level(raw)
    s = raw.strip()
    if "{" in s or "=>" in s:
        # Strip body portion to get clean signature
        sig = re.sub(r"\s*(?:\{.*|=>.*)", "", s).strip()
        return ind + extract_signature([sig]), start, "{" in s
    # Name-only line; { expected on next line
    next_idx = start + 1
    if next_idx < len(lines) and lines[next_idx].strip() == "{":
        return ind + extract_signature([s]), next_idx, True
    return ind + extract_signature([s]), start, False


def _is_property_line(raw: str, next_line: str = "") -> bool:
    """Return True if the line looks like a property declaration."""
    if _STMT_START_RE.match(raw):
        return False
    m = _PROPERTY_RE.match(raw)
    if m:
        name = m.group(1)
        if name in _CONTROL_FLOW:
            return False
        if re.match(r"\s*\(", raw[m.end(1):]):
            return False
        if _ASSIGN_RE.search(raw[m.start():m.end()]):
            return False
        return True
    m2 = _PROPERTY_NAME_RE.match(raw)
    if m2:
        name = m2.group(1)
        if name in _CONTROL_FLOW:
            return False
        if _ASSIGN_RE.search(raw):
            return False
        if next_line.strip() == "{":
            return True
    return False


def _is_method_line(raw: str) -> bool:
    """Return True if the line looks like a method, constructor, or explicit interface impl."""
    if _STMT_START_RE.match(raw):
        return False
    # Try explicit interface implementation first (qualified name like IFoo.Bar)
    m = _EXPLICIT_IFACE_RE.match(raw)
    if m:
        if _ASSIGN_RE.search(raw[m.start():m.end()]):
            return False
        return True
    m = _METHOD_RE.match(raw)
    if m is None:
        return False
    name = m.group(1)
    if name in _CONTROL_FLOW:
        return False
    prefix = raw[:m.start(1)].strip()
    if not prefix:
        return False
    if _ASSIGN_RE.search(raw[m.start():m.end()]):
        return False
    return True


def _is_comment_line(line: str, s: str) -> bool:
    return bool(s) and (
        s.startswith("///")
        or s.startswith("//")
        or s.startswith("/*")
        or s[0] == "*"
        or s[0] == "["  # attribute
    )


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines()
    n = len(lines)
    items: list[OutlineItem] = []
    i = 0

    while i < n:
        raw = lines[i]
        s = raw.strip()

        # Skip blank, comment, and continuation lines
        if not s or s.startswith("//") or s.startswith("/*") or s[0:1] == "*":
            i += 1
            continue

        # Skip using/import directives (including global using)
        if _USING_RE.match(raw):
            i += 1
            continue

        # Skip event declarations (excluded by design — too noisy)
        if re.match(r"^\s*(?:(?:public|protected|internal|private|static|abstract|virtual|"
                    r"override|sealed|new)\s+)*event\b", raw):
            i += 1
            continue

        # Skip attribute-only lines
        if _ATTR_RE.match(raw) and not _TYPE_RE.match(raw) and not _NAMESPACE_RE.match(raw):
            i += 1
            continue

        # --- namespace ---
        if _NAMESPACE_RE.match(raw):
            sig = s.rstrip(";{").strip()
            start = seek_comment_start(lines, i, _is_comment_line)
            if "{" in raw:
                end = seek_brace_end(lines, i)
            else:
                end = n  # file-scoped namespace covers rest of file
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i += 1
            continue

        # --- type declarations ---
        if _TYPE_RE.match(raw):
            sig, sig_end, has_body = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_comment_line)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i = sig_end + 1
            continue

        # --- methods / constructors / explicit interface implementations ---
        if _is_method_line(raw):
            sig, sig_end, has_body = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_comment_line)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            if has_body:
                i = end
            else:
                i = sig_end + 1
            continue

        # --- properties ---
        next_raw = lines[i + 1] if i + 1 < n else ""
        if _is_property_line(raw, next_raw):
            sig, sig_end, has_body = _collect_prop_sig(lines, i)
            start = seek_comment_start(lines, i, _is_comment_line)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            if has_body:
                i = end
            else:
                i = sig_end + 1
            continue

        i += 1

    return items

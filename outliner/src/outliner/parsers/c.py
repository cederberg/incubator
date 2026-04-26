"""C/C++ outline parser (regex-based)."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end


def _block_comment_set(lines: list[str]) -> set[int]:
    """Return 0-based line indices that are inside a /* */ block comment.

    The opening line (containing /*) is NOT included unless it is also
    a continuation (i.e. the same line also contains text after the /*)
    that carries no code — callers skip it based on the leading * check.
    Subsequent lines until the matching */ are included.
    """
    inside = False
    result: set[int] = set()
    for i, raw in enumerate(lines):
        if inside:
            result.add(i)
            if "*/" in raw:
                inside = False
        elif "/*" in raw:
            pos = raw.index("/*")
            if raw.find("*/", pos + 2) == -1:
                inside = True  # comment continues beyond this line
    return result

SYNTAX = "c"
EXTENSIONS = (".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hxx", ".hh")

# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

_INCLUDE_RE = re.compile(r"^\s*#\s*include\s*[<\"]")
_DETECT_STRUCT_RE = re.compile(r"\b(?:struct|class|namespace|union|enum)\s+\w+")
_DETECT_FUNC_RE = re.compile(r"\w+\s*\([^)\n]*\)\s*(?:const\s+)?[{;]")


def detect(lines: list[str]) -> bool:
    """Detect C/C++: requires #include AND a structural code marker."""
    if not any(_INCLUDE_RE.match(l) for l in lines):
        return False
    text = "\n".join(lines)
    return bool(_DETECT_STRUCT_RE.search(text) or _DETECT_FUNC_RE.search(text))


# ---------------------------------------------------------------------------
# Macro (#define)
# ---------------------------------------------------------------------------

_DEFINE_RE = re.compile(r"^\s*#\s*define\s+\w+")


def _collect_define(lines: list[str], start: int) -> tuple[str, int]:
    """Collect a #define, following backslash line continuations."""
    parts = [lines[start].rstrip()]
    i = start
    while parts[-1].endswith("\\") and i + 1 < len(lines):
        i += 1
        parts.append(lines[i].rstrip())
    sig = " ".join(p.rstrip("\\").strip() for p in parts)
    sig = re.sub(r"\s+", " ", sig).strip()
    return sig, i


# ---------------------------------------------------------------------------
# Template prefix
# ---------------------------------------------------------------------------

_TEMPLATE_RE = re.compile(r"^\s*template\s*<")


def _collect_template_sig(lines: list[str], start: int) -> tuple[str, int]:
    """Collect template<...> parameters, handling nested angle brackets."""
    depth = 0
    parts: list[str] = []
    for i in range(start, min(start + 10, len(lines))):
        raw = lines[i]
        for ch in raw:
            if ch == "<":
                depth += 1
            elif ch == ">":
                depth -= 1
        parts.append(raw.strip())
        if depth <= 0:
            break
    return extract_signature(parts), i


# ---------------------------------------------------------------------------
# Type declarations (struct / class / union / enum / namespace)
# ---------------------------------------------------------------------------

# Matches 'struct Name', 'class Name', etc. but NOT 'struct Name varname'
# Lookahead ensures after the name there is no other identifier (variable name).
_TYPE_RE = re.compile(
    r"^\s*"
    r"(?:(?:static|inline|extern|virtual|explicit|constexpr|friend)\s+)*"
    r"(?:typedef\s+)?"
    r"(?:struct|class|union|enum(?:\s+class)?|namespace)\s+\w+"
    r"\s*(?=[{;:<]|//|$)"  # followed by {, ;, :, <, //, or end-of-line
)

# ---------------------------------------------------------------------------
# Function / method detection
# ---------------------------------------------------------------------------

_FLOW_STARTERS = frozenset({
    "if", "else", "while", "for", "do", "switch", "case",
    "return", "goto", "throw", "try", "catch",
    "sizeof", "typeof", "alignof", "decltype",
})

_STMT_START_RE = re.compile(
    r"^\s*(?:return|throw|break|continue|goto|delete\b|assert\b|static_assert\b)\b"
)

# Identifier (with optional ~) or operator overload, followed by (
_FUNC_NAME_PAREN_RE = re.compile(
    r"(~?\w+|operator\s*(?:\(\)|[+\-*/%^&|~!<>=,\[\]()\s]+?))\s*\("
)


def _is_func_line(raw: str) -> bool:
    """Return True if line looks like a C/C++ function/method declaration."""
    s = raw.strip()
    # Skip comment lines, constructor-init-list and comma continuations
    if not s or s[0] in ("*", ":", ",") or s.startswith("//") or s.startswith("/*"):
        return False
    if _STMT_START_RE.match(raw):
        return False
    for m in _FUNC_NAME_PAREN_RE.finditer(raw):
        name = m.group(1).strip()
        if name in _FLOW_STARTERS:
            continue
        prefix = raw[: m.start()].strip()
        if not prefix:
            continue  # no return type — bare call or constructor without qualifier
        # Exclude: assignment (x = func(...)) and member access (p->func(...))
        if "=" in prefix or "->" in prefix:
            continue
        # Exclude: prefix contains a comment → tail of a statement line
        if "//" in prefix:
            continue
        # Exclude: nested call — prefix has unmatched open paren
        if prefix.count("(") > prefix.count(")"):
            continue
        # Exclude: bare namespace/template qualifier with no return type (e.g. "std::", "Foo<T>::")
        if prefix.endswith("::") and " " not in prefix:
            continue
        # Exclude: member access via . or closing bracket
        if re.search(r"[).\]]\s*$", prefix):
            continue
        first_word = re.split(r"\W+", prefix.lstrip())[0] if prefix.lstrip() else ""
        if first_word in _FLOW_STARTERS:
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# Signature collection
# ---------------------------------------------------------------------------


def _collect_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a C/C++ function or type signature spanning multiple lines.

    Tracks parenthesis depth; stops when depth returns to 0 and line ends with
    { (has body) or ; (declaration only).
    Returns (signature, last_sig_line_0based, has_body).
    """
    depth = 0
    parts: list[str] = []
    ind = " " * indent_level(lines[start])
    has_body = False

    for i in range(start, min(start + 30, len(lines))):
        raw = lines[i]
        for ch in raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        parts.append(raw.strip())
        if depth <= 0:
            bd = raw.count("{") - raw.count("}")
            if bd > 0 or (bd == 0 and raw.rstrip().endswith("}")):
                has_body = True
                break
            if raw.rstrip().endswith(";"):
                break

    sig = ind + extract_signature(parts, strip="{;")
    # For one-liner bodies the inline body may remain; truncate at first {
    if has_body:
        brace = sig.find("{")
        if brace != -1:
            sig = sig[:brace].rstrip()
    # Strip constructor init list: ): ... before end of sig
    sig = re.sub(r"\)\s*:(?!:)[^{;]*$", ")", sig).rstrip()
    return sig, i, has_body


# ---------------------------------------------------------------------------
# Comment walk-back predicate
# ---------------------------------------------------------------------------


def _is_comment_line(line: str, s: str) -> bool:
    return bool(s) and (s.startswith("//") or s.startswith("/*") or s[0] == "*")


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines()
    n = len(lines)
    items: list[OutlineItem] = []
    block_comments = _block_comment_set(lines)
    i = 0

    while i < n:
        raw = lines[i]

        # Skip lines inside /* */ block comments, blank lines, and line comments
        s = raw.strip()
        if i in block_comments or not s or s[0] == "*" or s.startswith("//"):
            i += 1
            continue

        # --- #define macros ---
        if _DEFINE_RE.match(raw):
            sig, sig_end = _collect_define(lines, i)
            start = seek_comment_start(lines, i, _is_comment_line)
            items.append(OutlineItem(
                start=start + 1,
                count=sig_end - start + 1,
                signature=sig,
            ))
            i = sig_end + 1
            continue

        # Skip other preprocessor directives (#if, #ifdef, #include, #pragma, etc.)
        if s.startswith("#"):
            i += 1
            continue

        # --- template<...> + following declaration ---
        if _TEMPLATE_RE.match(raw):
            tmpl_sig, tmpl_end = _collect_template_sig(lines, i)
            comment_start = seek_comment_start(lines, i, _is_comment_line)
            # Find the declaration following the template params (skip blanks and preprocessor)
            j = tmpl_end + 1
            while j < n and (not lines[j].strip() or lines[j].strip().startswith("#")):
                j += 1
            if j < n and (_TYPE_RE.match(lines[j]) or _is_func_line(lines[j])):
                is_type_decl = bool(_TYPE_RE.match(lines[j]))
                decl_sig, decl_end, has_body = _collect_sig(lines, j)
                full_sig = tmpl_sig + " " + decl_sig.strip()
                end = seek_brace_end(lines, decl_end) if has_body else decl_end + 1
                items.append(OutlineItem(
                    start=comment_start + 1,
                    count=end - comment_start,
                    signature=full_sig,
                ))
                if has_body and not is_type_decl:
                    i = end  # skip function body entirely
                else:
                    i = decl_end + 1  # advance into type body so members are parsed
            else:
                i = tmpl_end + 1
            continue

        # --- type declarations (struct/class/union/enum/namespace) ---
        if _TYPE_RE.match(raw):
            sig, sig_end, has_body = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_comment_line)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            i = sig_end + 1  # advance into body to parse members
            continue

        # --- function / method declarations and definitions ---
        if _is_func_line(raw):
            sig, sig_end, has_body = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_comment_line)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
            if has_body:
                i = end  # skip body to avoid matching statements inside
            else:
                i = sig_end + 1
            continue

        i += 1

    return items

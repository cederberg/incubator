"""JavaScript/TypeScript outline parser (regex-based)."""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem
from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end

SYNTAX = "javascript"
EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")

# --- Top-level declaration matchers ---

_FUNC_RE = re.compile(
    r"^\s*(?:export\s+(?:default\s+)?)?(?:declare\s+)?(?:async\s+)?function\s*\*?\s*\w+"
)
_CLASS_RE = re.compile(
    r"^\s*(?:export\s+(?:default\s+)?)?(?:abstract\s+)?(?:declare\s+)?class\s+\w+"
)
_IFACE_RE = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?interface\s+\w+")
# type alias: allow <T = Default> generics by using [^>]* instead of [^=]*
_TYPE_RE  = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?type\s+\w+\s*(?:<[^>]*>)?\s*=")
_ENUM_RE  = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?(?:const\s+)?enum\s+\w+")
_NS_RE    = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?(?:namespace|module)\s+\w+")

# const/let/var with optional type annotation before =, RHS must be fn/arrow/class.
# The type annotation may itself contain '=>' (function type), so we allow '='
# only if preceded by '>' (part of '=>') or if it starts the outer assignment.
# Strategy: match the assignment '=' that is NOT preceded by '>' (arrow) or '!<>='.
_CONST_FN_RE = re.compile(
    r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)"
    r"(?::[^;{\n]*)?"  # optional TS type annotation (may contain =>, not ; or {)
    r"(?<![=>!<])\s*=\s*(?!=)"  # assignment = not preceded by =>/!=/<=/>=
    r"(?:async\s+)?(?:<[^>]*>\s*)?(?:function\b|\(|class\b)"
)

# --- Class method matcher (indented, no 'function' keyword) ---

_JS_CONTROL = frozenset({
    "if", "else", "while", "for", "do", "switch", "case",
    "try", "catch", "finally", "return", "throw", "new",
    "typeof", "instanceof", "void", "delete", "await", "yield",
    "break", "continue", "super", "this", "import", "export",
    "class", "function", "var", "let", "const",
})

_METHOD_RE = re.compile(
    r"^\s+"  # must be indented
    r"(?:(?:public|private|protected|static|async|abstract|override|readonly|declare)\s+)*"
    r"(?:get\s+|set\s+)?"
    r"(#?\w+)\??"    # group 1: method name, optional '?' for TS optional methods
    r"\s*[(<]"       # followed by ( or <
)

_STMT_START_RE = re.compile(
    r"^\s*(?:return|throw|if|while|for|else|switch|do|try|catch|finally|"
    r"break|continue|new\s|delete\s|typeof\s|void\s|await\s|yield\s)"
)

# --- Detection helpers ---

_CLASS_DETECT_RE    = re.compile(r"\bclass\s+\w+")
_FUNC_DETECT_RE     = re.compile(r"\bfunction\s+\w+|\bconst\s+\w+\s*=\s*(?:async\s+)?\(")
_TS_MARKER_RE       = re.compile(r"\binterface\s+\w+|\benum\s+\w+|\bnamespace\s+\w+|:\s*\w+\s*[;{=,(]")
_ARROW_DETECT_RE    = re.compile(r"=>\s*[{(]")
_EXPORT_DEFAULT_RE  = re.compile(r"\bexport\s+(?:default\s+)?(?:class|function)\b")
_TS_STRUCT_RE       = re.compile(r"\b(?:interface|enum|namespace)\s+\w+")
_CONST_ASSIGN_RE    = re.compile(r"\bconst\s+\w+\s*=")
_CONSTRUCTOR_RE     = re.compile(r"\bconstructor\s*\(")
_CLASS_FN_BRACE_RE  = re.compile(r"\b(?:class|function)\s+\w+[^:]*\{")
# Rejection helpers
_PY_DEF_RE     = re.compile(r"^\s*(?:def|class)\s+\w+[^{]*:\s*$", re.MULTILINE)
_GO_PKG_RE     = re.compile(r"^package\s+\w+", re.MULTILINE)
_JAVA_TYPE_RE  = re.compile(r"\bpublic\s+(?:class|interface|enum)\b")
_RUST_FN_RE    = re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+\w+", re.MULTILINE)
_RUST_IMPL_RE  = re.compile(r"^\s*impl\b", re.MULTILINE)
_RUST_ARROW_RE = re.compile(r"->\s*\w")



def detect(lines: list[str]) -> bool:
    """Detect JS/TS using conservative multi-marker approach."""
    text = "\n".join(lines)
    if _PY_DEF_RE.search(text):
        return False
    if _GO_PKG_RE.search(text):
        return False
    if _JAVA_TYPE_RE.search(text):
        return False
    if _RUST_FN_RE.search(text) and (
        _RUST_IMPL_RE.search(text) or _RUST_ARROW_RE.search(text)
    ):
        return False

    has_decl = (
        _CLASS_DETECT_RE.search(text) or
        _FUNC_DETECT_RE.search(text) or
        _EXPORT_DEFAULT_RE.search(text) or
        _TS_STRUCT_RE.search(text)
    )
    has_js_marker = (
        _ARROW_DETECT_RE.search(text) or
        _TS_MARKER_RE.search(text) or
        _CONST_ASSIGN_RE.search(text) or
        _CONSTRUCTOR_RE.search(text) or
        _CLASS_FN_BRACE_RE.search(text) or
        _TS_STRUCT_RE.search(text)
    )
    return bool(has_decl and has_js_marker)


def _truncate_at_body(raw: str, stripped: str) -> tuple[str | None, bool]:
    """Try to detect a body-opening '{' on this line and return (truncated_part, has_body).

    Returns (None, False) if no body detected on this line.
    Uses rindex to find the LAST '{', which is always the body opener
    (not '{' inside generic type parameters like <{ id: string }>).
    """
    if stripped.endswith("{"):
        # Body-opening brace is last on line; truncate at it
        brace_pos = raw.rindex("{")
        return raw[:brace_pos].strip(), True
    if stripped.endswith("=>"):
        # Arrow body on next line
        return raw.strip(), True
    if stripped.endswith(";"):
        return raw.strip(), False
    # Inline body: line ends with } or }, or }; — body starts at first { AFTER )
    if stripped.endswith("}") or stripped.endswith("},") or stripped.endswith("};"):
        paren_pos = raw.rfind(")")
        brace_pos = raw.find("{", paren_pos) if paren_pos != -1 else -1
        if brace_pos != -1:
            return raw[:brace_pos].strip(), True
        return raw.strip(), False
    return None, False


def _collect_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect a possibly multi-line JS/TS signature (tracks paren depth).

    Returns (signature, last_sig_line_0based, has_body).
    """
    depth = 0
    parts: list[str] = []
    ind = " " * indent_level(lines[start])
    has_body = False
    i = start

    for i in range(start, min(start + 40, len(lines))):
        raw = lines[i]
        for ch in raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        parts.append(raw.strip())
        stripped = raw.rstrip()
        if depth <= 0:
            part, has_body = _truncate_at_body(raw, stripped)
            if part is not None:
                parts[-1] = part
                break

    sig = ind + extract_signature(parts, strip="{;")
    if sig.endswith("=>"):
        sig = sig[:-2].rstrip()
    return sig, i, has_body


def _collect_const_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Collect signature for a const/let = fn/arrow/class expression."""
    depth = 0
    parts: list[str] = []
    ind = " " * indent_level(lines[start])
    has_body = False
    found_eq = False
    i = start

    for i in range(start, min(start + 40, len(lines))):
        raw = lines[i]
        for ch in raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        parts.append(raw.strip())
        stripped = raw.rstrip()
        if not found_eq and "=" in raw:
            found_eq = True
        if found_eq and depth <= 0:
            part, has_body = _truncate_at_body(raw, stripped)
            if part is not None:
                parts[-1] = part
                break

    sig = ind + extract_signature(parts, strip="{;")
    if sig.endswith("=>"):
        sig = sig[:-2].rstrip()
    return sig, i, has_body


def _find_type_alias_eq(sig: str) -> int:
    """Find position of the standalone '=' in a type alias, skipping generics."""
    depth = 0
    i = 0
    while i < len(sig):
        c = sig[i]
        if c == "<":
            depth += 1
        elif c == ">":
            depth -= 1
        elif c == "=" and depth == 0:
            prev = sig[i - 1] if i > 0 else ""
            nxt  = sig[i + 1] if i + 1 < len(sig) else ""
            if prev not in "!<>=" and nxt != "=":
                return i
        i += 1
    return -1


def _collect_type_alias_sig(lines: list[str], start: int) -> tuple[str, int]:
    """Collect a type alias declaration to 'type Name<params>' (no RHS).

    Scans to the closing ';' so the count covers multi-line type aliases.
    """
    ind = " " * indent_level(lines[start])
    parts = []
    sig_end = start
    for i in range(start, min(start + 20, len(lines))):
        parts.append(lines[i].strip())
        if lines[i].rstrip().endswith(";"):
            sig_end = i
            break
    else:
        sig_end = min(start + 19, len(lines) - 1)
    sig = ind + extract_signature(parts, strip=";")
    eq = _find_type_alias_eq(sig)
    if eq != -1:
        sig = sig[:eq].rstrip()
    return sig, sig_end


def _is_method_line(raw: str) -> bool:
    """Return True if line looks like a class/interface method declaration."""
    if _STMT_START_RE.match(raw):
        return False
    # Object literal single-line methods end with '};' or '},' — skip them
    stripped = raw.rstrip()
    if stripped.endswith("},") or stripped.endswith("};"):
        return False
    m = _METHOD_RE.match(raw)
    if not m:
        return False
    return m.group(1) not in _JS_CONTROL


def _seek_expression_end(lines: list[str], start_index: int) -> int:
    """Find end of a brace-delimited body or expression-arrow body.

    If the body opens with '{', scan to the matching '}'. Otherwise treat it
    as an expression body that ends at a top-level ';'.
    """
    depth = 0
    brace_started = False
    paren_depth = 0

    for i in range(start_index, len(lines)):
        raw = lines[i]
        # Decide on first non-empty line whether it's a block or expression
        if not brace_started:
            stripped = raw.lstrip()
            if stripped.startswith("{"):
                brace_started = True
            else:
                # Expression arrow: track parens and wait for top-level ;
                for ch in raw:
                    if ch == "(":
                        paren_depth += 1
                    elif ch == ")":
                        paren_depth -= 1
                if paren_depth <= 0 and raw.rstrip().endswith(";"):
                    return i + 1
                continue

        for ch in raw:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
        if brace_started and depth <= 0:
            return i + 1

    return len(lines)


def parse(text: str) -> Iterator[OutlineItem]:
    _is_walkback = lambda _, s: s[:1] in "/*@" or s.startswith("//")
    for i, line in enumerate(lines := text.splitlines()):
        if any(r.match(line) for r in [_FUNC_RE, _CLASS_RE, _IFACE_RE, _ENUM_RE, _NS_RE]) or _is_method_line(line):
            sig, sig_end, has_body = _collect_sig(lines, i)
            start = seek_comment_start(lines, i, _is_walkback)
            end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)
        elif _TYPE_RE.match(line):
            sig, sig_end = _collect_type_alias_sig(lines, i)
            start = seek_comment_start(lines, i, _is_walkback)
            yield OutlineItem(start=start + 1, count=sig_end - start + 1, signature=sig)
        elif _CONST_FN_RE.match(line):
            sig, sig_end, has_body = _collect_const_sig(lines, i)
            start = seek_comment_start(lines, i, _is_walkback)
            end = _seek_expression_end(lines, sig_end) if has_body else sig_end + 1
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)

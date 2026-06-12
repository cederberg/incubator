"""JavaScript/TypeScript outline parser."""

import re
from collections.abc import Iterator

from outliner.parsers.util import extract_signature, indent_level, seek_comment_start, seek_brace_end
from outliner.types import OutlineItem

SYNTAX = "javascript"
EXTENSIONS = (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".svelte", ".vue", ".astro")
STRIP_FRONTMATTER = False  # Astro delimits its script with --- fences

_FUNC_RE = re.compile(
    r"^\s*(?:(?:export\s+(?:default\s+)?)?(?:declare\s+)?(?:async\s+)?function\s*\*?\s*\w+"
    r"|export\s+default\s+(?:async\s+)?function\s*\*?\s*\()"
)
_CLASS_RE = re.compile(
    r"^\s*(?:(?:export\s+(?:default\s+)?)?(?:declare\s+)?(?:abstract\s+)?class\s+\w+"
    r"|export\s+default\s+(?:abstract\s+)?class\b)"
)
_IFACE_RE = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?interface\s+\w+")
_TYPE_RE = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?type\s+\w+\s*(?:<[^>]*>)?\s*=")
_ENUM_RE = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?(?:const\s+)?enum\s+\w+")
_NS_RE = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?namespace\s+\w+")
_MODULE_RE = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?module\s+(?:\w+|\s*(?={|$))")
_GLOBAL_RE = re.compile(r"^\s*declare\s+global\b")
_AMBIENT_VAR_RE = re.compile(r"^\s*(?:export\s+)?declare\s+(?:const|let|var)\s+\w+")
_EXPORT_ASSIGN_RE = re.compile(r"^\s*export\s*=\s*[\w$.]+\s*;?\s*$")
_CONST_FN_RE = re.compile(
    r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)"
    r"(?::[^;{\n]*)?"
    r"(?<![=>!<])\s*=\s*(?!=)"
    r"(?:async\s+)?(?:<[^>]*>\s*)?(?:function\b|\(|class\b|[\w$]+\s*=>)"
)
_MULTILINE_TYPED_CONST_RE = re.compile(
    r"^\s*(?:export\s+)?(?:const|let|var)\s+\w+\s*:\s*[^;=\n]*\{\s*$"
)
_PROPERTY_FN_RE = re.compile(
    r"^\s*(?:[\w$]+\.)+[\w$]+\s*=\s*(?:async\s+)?"
    r"(?:function\s*\*?\s*(?:[\w$]+\s*)?\(|\(|[\w$]+\s*=>)"
)
_METHOD_RE = re.compile(
    r"^\s+"
    r"(?:(?:public|private|protected|static|async|abstract|override|readonly|declare)\s+)*"
    r"(?:get\s+|set\s+)?#?[\w$]+\??\s*[(<]"
)
_CLASS_FIELD_FN_RE = re.compile(
    r"^\s+"
    r"(?:(?:public|private|protected|static|readonly|declare|override)\s+)*"
    r"#?[\w$]+\??(?:\s*:\s*.*?)?\s*=\s*(?:async\s+)?"
    r"(?:function\s*\*?\s*(?:[\w$]+\s*)?\(|(?:<[^>]*>\s*)?\([^)]*\)\s*(?::[^=;\n]+)?\s*=>|[\w$]+\s*=>)"
)
_MEMBER_BOUNDARY_RE = re.compile(
    r"^\s+"
    r"(?:(?:readonly|public|private|protected|static|abstract)\s+)*"
    r"(?:[\w$]+\??\s*(?:[(<:]|\[)|\(|\[[^\]]+\]\s*:)"
)
_CALLABLE_MEMBER_RE = re.compile(
    r"^\s+"
    r"(?:(?:readonly|public|private|protected|static|abstract)\s+)*"
    r"(?:(?:get\s+|set\s+)?[\w$]+\??\s*[(<]|\(|new\s*[(<])"
)
_PROTOTYPE_OBJECT_RE = re.compile(r"^\s*(?:(?:[\w$]+\.)*prototype\s*=\s*)+\{|^\s*export\s+default\s+\{")
_OPTION_GROUP_RE = re.compile(r"^\s*(?:methods|computed|watch)\s*:\s*\{\s*$")
_PROTOTYPE_MEMBER_RE = re.compile(
    r"^\s+(?:(?:get|set)\s+[\w$]+\s*\(|[\w$]+\s*\(|[\w$]+\s*:\s*(?:async\s+)?"
    r"(?:function\s*\*?\s*(?:[\w$]+\s*)?\(|(?:\([^)]*\)|[\w$]+)\s*=>))"
)
_MODULE_WRAPPER_RE = re.compile(
    r"^\s*(?:"
    r";?\s*\(\s*function\b|"
    r"(?:const|let|var)\s+\w+\s*=\s*\(\s*function\b|"
    r"!\s*function\b|"
    r"define\s*\([^;]*\(?\s*function\b"
    r").*\{"
)
_CLASS_EXPR_RE = re.compile(r"=\s*class\b")

_CLASS_DETECT_RE = re.compile(r"\bclass\s+\w+")
_FUNC_DETECT_RE = re.compile(r"\bfunction\s+\w+|\bconst\s+\w+\s*=\s*(?:async\s+)?\(")
_TS_MARKER_RE = re.compile(r"\binterface\s+\w+|\benum\s+\w+|\bnamespace\s+\w+|:\s*\w+\s*[;{=,(]")
_ARROW_DETECT_RE = re.compile(r"=>\s*[{(]")
_EXPORT_DEFAULT_RE = re.compile(r"\bexport\s+(?:default\s+)?(?:class|function)\b")
_TS_STRUCT_RE = re.compile(r"\b(?:interface|enum|namespace)\s+\w+")
_CONST_ASSIGN_RE = re.compile(r"\bconst\s+\w+\s*=")
_CONSTRUCTOR_RE = re.compile(r"\bconstructor\s*\(")
_CLASS_FN_BRACE_RE = re.compile(r"\b(?:class|function)\s+\w+[^:]*\{")
_PY_DEF_RE = re.compile(r"^\s*(?:def|class)\s+\w+[^{]*:\s*$", re.MULTILINE)
_GO_PKG_RE = re.compile(r"^package\s+\w+", re.MULTILINE)
_JAVA_TYPE_RE = re.compile(r"\bpublic\s+(?:class|interface|enum)\b")
_RUST_FN_RE = re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+\w+", re.MULTILINE)
_RUST_IMPL_RE = re.compile(r"^\s*impl\b", re.MULTILINE)
_RUST_ARROW_RE = re.compile(r"->\s*\w")

def detect(lines: list[str]) -> bool:
    text = "\n".join(lines)
    if _PY_DEF_RE.search(text) or _GO_PKG_RE.search(text) or _JAVA_TYPE_RE.search(text):
        return False
    if _RUST_FN_RE.search(text) and (_RUST_IMPL_RE.search(text) or _RUST_ARROW_RE.search(text)):
        return False
    has_decl = _CLASS_DETECT_RE.search(text) or _FUNC_DETECT_RE.search(text) or _EXPORT_DEFAULT_RE.search(text) or _TS_STRUCT_RE.search(text)
    has_js = _ARROW_DETECT_RE.search(text) or _TS_MARKER_RE.search(text) or _CONST_ASSIGN_RE.search(text) or _CONSTRUCTOR_RE.search(text) or _CLASS_FN_BRACE_RE.search(text) or _TS_STRUCT_RE.search(text)
    return bool(has_decl and has_js)

def _collect_sig(lines: list[str], start: int, is_member: bool = False, is_wrapper: bool = False) -> tuple[str, int, bool]:
    depth, parts, has_body, i = 0, [], False, start
    ind = " " * indent_level(lines[start])
    state = None
    for i in range(start, min(start + 40, len(lines))):
        raw, state = _sanitize(lines[i], state, preserve_strings=True)
        if is_member and i > start and depth == 0 and (_MEMBER_BOUNDARY_RE.match(raw) or raw.lstrip().startswith("}")):
            i -= 1
            break
        depth += raw.count("(") - raw.count(")")
        parts.append(raw.strip())
        stripped = raw.rstrip()
        if is_wrapper and i == start and "{" in raw:
            parts[-1], has_body = raw[:raw.find("{")].strip(), True
            break
        if depth == 1 and re.search(r"=>\s*\($", stripped):
            parts[-1], has_body = raw[:raw.rfind("=>")].strip(), True
            break
        if depth > 0:
            continue
        if _starts_multiline_template_expression(raw):
            parts[-1], has_body = raw[:raw.rfind("=>")].strip(), True
            break
        if stripped.endswith("{"):
            parts[-1], has_body = raw[:raw.rindex("{")].strip(), True
            break
        if stripped.endswith("=>"):
            has_body = True
            break
        if stripped.endswith(";"):
            break
        if stripped.endswith("}") or stripped.endswith("},") or stripped.endswith("};"):
            pos = raw.find("{", raw.rfind(")"))
            if pos != -1:
                parts[-1], has_body = raw[:pos].strip(), True
            break
        if "=>" in stripped and not stripped.endswith(("=>", "(", ",", ":", "=", "&&", "||", "?")):
            break  # complete expression-bodied arrow (no-semicolon style)
        is_type_continuation = stripped.endswith((":", "|", "&")) or stripped.lstrip().startswith(("|", "&"))
        if is_member and not is_type_continuation:
            break
    sig = ind + extract_signature(parts, strip="{;,")
    return (sig[:-2].rstrip() if sig.endswith("=>") else sig), i, has_body


def _find_type_alias_eq(sig: str) -> int:
    depth = 0
    for i, ch in enumerate(sig):
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif ch == "=" and depth == 0:
            prev = sig[i - 1] if i else ""
            nxt = sig[i + 1] if i + 1 < len(sig) else ""
            if prev not in "!<>=" and nxt != "=":
                return i
    return -1

def _collect_type_alias_sig(lines: list[str], start: int) -> tuple[str, int, bool]:
    ind, parts, sig_end = " " * indent_level(lines[start]), [], start
    for i in range(start, min(start + 20, len(lines))):
        parts.append(lines[i].strip())
        if lines[i].rstrip().endswith(";"):
            sig_end = i
            break
    sig = ind + extract_signature(parts, strip=";")
    eq = _find_type_alias_eq(sig)
    is_object = eq != -1 and "{" in sig[eq + 1:]
    if is_object:
        sig_end = seek_brace_end(lines, start) - 1
    return (sig[:eq] if eq != -1 else sig).rstrip(), sig_end, is_object


def _collect_multiline_typed_arrow_sig(lines: list[str], start: int) -> tuple[str, int, bool] | None:
    ind, parts = " " * indent_level(lines[start]), []
    state = None
    for i in range(start, min(start + 40, len(lines))):
        raw, state = _sanitize(lines[i], state, preserve_strings=True)
        parts.append(raw.strip())
        if not re.search(r"(?<![=>!<])=(?!=)", raw):
            continue
        if not re.search(r"=>\s*\{", raw):
            return None
        parts[-1] = raw[:raw.rindex("{")].strip()
        sig = ind + extract_signature(parts, strip="{;,")
        return sig[:-2].rstrip() if sig.endswith("=>") else sig, i, True
    return None


def _starts_multiline_template_expression(raw: str) -> bool:
    if "=>" not in raw:
        return False
    expression = raw[raw.rfind("=>") + 2:]
    return bool(re.match(r"\s*`", expression)) and sum(
        ch == "`" and not _is_escaped(expression, i)
        for i, ch in enumerate(expression)
    ) % 2 == 1


def _seek_template_expression_end(lines: list[str], start_index: int) -> int:
    in_template = False
    for i in range(start_index, len(lines)):
        raw = lines[i][lines[i].rfind("=>") + 2:] if i == start_index else lines[i]
        for j, ch in enumerate(raw):
            if ch == "`" and not _is_escaped(raw, j):
                in_template = not in_template
        if not in_template and raw.rstrip().endswith(";"):
            return i + 1
    return len(lines)


def _seek_expression_end(lines: list[str], start_index: int) -> int:
    if _starts_multiline_template_expression(lines[start_index]):
        return _seek_template_expression_end(lines, start_index)
    depth, paren_depth, block, state = 0, 0, False, None
    for i in range(start_index, len(lines)):
        clean, state = _sanitize(lines[i], state)
        if i == start_index and "=>" in clean:
            clean = clean[clean.rfind("=>") + 2:]
        if "{" in clean and paren_depth <= 0:
            block = True
        if block:
            depth += clean.count("{") - clean.count("}")
            if depth <= 0:
                return i + 1
            continue
        paren_depth += clean.count("(") - clean.count(")")
        if paren_depth <= 0 and clean.rstrip().endswith(";"):
            return i + 1
    return len(lines)


def _is_escaped(raw: str, index: int) -> bool:
    slashes = 0
    while index > slashes and raw[index - slashes - 1] == "\\":
        slashes += 1
    return slashes % 2 == 1


def _consume_quoted(raw: str, start: int, quote: str) -> int:
    i = start + 1
    while i < len(raw):
        if raw[i] == "\\":
            i += 2
        elif raw[i] == quote:
            return i + 1
        else:
            i += 1
    return i


def _consume_template_expression(raw: str, start: int) -> int:
    depth, i = 1, start
    while i < len(raw) and depth:
        ch, nxt = raw[i], raw[i + 1] if i + 1 < len(raw) else ""
        if ch in "\"'":
            i = _consume_quoted(raw, i, ch)
        elif ch == "`":
            i = _consume_template(raw, i)
        elif ch == "{":
            depth, i = depth + 1, i + 1
        elif ch == "}":
            depth, i = depth - 1, i + 1
        elif ch == "/" and nxt == "/":
            return len(raw)
        elif ch == "/" and nxt == "*":
            end = raw.find("*/", i + 2)
            i = len(raw) if end == -1 else end + 2
        else:
            i += 1
    return i


def _consume_template(raw: str, start: int) -> int:
    i = start + 1
    while i < len(raw):
        ch, nxt = raw[i], raw[i + 1] if i + 1 < len(raw) else ""
        if ch == "\\":
            i += 2
        elif ch == "`":
            return i + 1
        elif ch == "$" and nxt == "{":
            i = _consume_template_expression(raw, i + 2)
        else:
            i += 1
    return i


_REGEX_PREFIX_RE = re.compile(r"(?:^|[=(,:;!&|?\[]|\breturn|\bcase|\btypeof)\s*$")


def _consume_regex(raw: str, start: int) -> int:
    i, in_class = start + 1, False
    while i < len(raw):
        ch = raw[i]
        if ch == "\\":
            i += 2
        elif ch == "[":
            in_class, i = True, i + 1
        elif ch == "]":
            in_class, i = False, i + 1
        elif ch == "/" and not in_class:
            return i + 1
        else:
            i += 1
    return i


def _template_closed(raw: str, start: int, end: int) -> bool:
    return end <= len(raw) and end - start >= 2 and raw[end - 1] == "`"


def _sanitize(raw: str, state: str | None = None, preserve_strings: bool = False) -> tuple[str, str | None]:
    out, i = [], 0
    if state == "template":
        end = _consume_template(raw, -1)
        if not _template_closed(raw, -1, end):
            return "", "template"
        if preserve_strings:
            out.append(raw[:end])
        i, state = end, None
    while i < len(raw):
        ch = raw[i]
        nxt = raw[i + 1] if i + 1 < len(raw) else ""
        if state == "comment":
            if ch == "*" and nxt == "/":
                state, i = None, i + 2
            else:
                i += 1
            continue
        if ch in "\"'":
            end = _consume_quoted(raw, i, ch)
            if preserve_strings:
                out.append(raw[i:end])
            i = end
            continue
        if ch == "`":
            end = _consume_template(raw, i)
            if not _template_closed(raw, i, end):
                return "".join(out), "template"
            if preserve_strings:
                out.append(raw[i:end])
            i = end
            continue
        if ch == "/" and nxt == "*" and not _is_escaped(raw, i):
            state, i = "comment", i + 2
            continue
        if ch == "/" and nxt == "/" and not _is_escaped(raw, i):
            break
        if ch == "/" and _REGEX_PREFIX_RE.search("".join(out)):
            end = _consume_regex(raw, i)
            if preserve_strings:
                out.append(raw[i:end])
            i = end
            continue
        out.append(ch)
        i += 1
    return "".join(out), state


def parse(text: str) -> Iterator[OutlineItem]:
    lines = text.splitlines()
    is_walkback = lambda _, sig: sig[:1] in "/*@" or sig.startswith("//")
    depth, state, wrapper_depth, signature_end = 0, None, None, -1
    class_depths: set[int] = set()
    namespace_depths: set[int] = set()
    typed_member_depths: set[int] = set()
    prototype_depths: set[int] = set()
    for i, line in enumerate(lines):
        clean, state = _sanitize(line, state)
        start_depth = depth
        class_depths = {body_depth for body_depth in class_depths if start_depth >= body_depth}
        namespace_depths = {body_depth for body_depth in namespace_depths if start_depth >= body_depth}
        typed_member_depths = {body_depth for body_depth in typed_member_depths if start_depth >= body_depth}
        prototype_depths = {body_depth for body_depth in prototype_depths if start_depth >= body_depth}
        if wrapper_depth is not None and start_depth < wrapper_depth:
            wrapper_depth = None
        close_count, open_count = clean.count("}"), clean.count("{")
        depth = max(0, depth + open_count - close_count)
        is_wrapper = start_depth == 0 and bool(_MODULE_WRAPPER_RE.match(clean)) and depth > start_depth
        if is_wrapper:
            wrapper_depth = depth
        declaration_depths = {0} | namespace_depths | ({wrapper_depth} if wrapper_depth is not None else set())
        is_new_signature = i > signature_end
        is_class_method = is_new_signature and start_depth in class_depths and bool(_METHOD_RE.match(clean))
        is_class_field_fn = is_new_signature and start_depth in class_depths and bool(_CLASS_FIELD_FN_RE.match(clean))
        is_typed_member = is_new_signature and start_depth in typed_member_depths and bool(_CALLABLE_MEMBER_RE.match(clean))
        is_prototype_member = is_new_signature and start_depth in prototype_depths and bool(_PROTOTYPE_MEMBER_RE.match(clean))
        allow_depth = start_depth in declaration_depths or is_class_method or is_class_field_fn or is_typed_member or is_prototype_member
        if is_new_signature and start_depth in prototype_depths and _OPTION_GROUP_RE.match(clean):
            prototype_depths.add(start_depth + 1)
            continue
        if not allow_depth:
            continue
        is_namespace = bool(_NS_RE.match(clean) or _MODULE_RE.match(clean) or _GLOBAL_RE.match(clean))
        is_named_decl = any(r.match(clean) for r in (_FUNC_RE, _CLASS_RE, _IFACE_RE, _ENUM_RE, _TYPE_RE))
        is_ambient_var = bool(_AMBIENT_VAR_RE.match(clean))
        is_export_assign = bool(_EXPORT_ASSIGN_RE.match(clean))
        is_prototype_object = bool(_PROTOTYPE_OBJECT_RE.match(clean))
        is_const = bool(_CONST_FN_RE.match(clean))
        is_multiline_typed_const = bool(_MULTILINE_TYPED_CONST_RE.match(clean))
        is_property_fn = bool(_PROPERTY_FN_RE.match(clean))
        is_declaration = is_namespace or is_named_decl or is_ambient_var or is_export_assign or is_prototype_object or is_const or is_multiline_typed_const
        is_api_member = is_property_fn or is_class_method or is_class_field_fn or is_typed_member or is_prototype_member
        if not (is_declaration or is_api_member):
            continue
        if _TYPE_RE.match(clean):
            sig, sig_end, is_object = _collect_type_alias_sig(lines, i)
            start = seek_comment_start(lines, i, is_walkback)
            yield OutlineItem(start=start + 1, count=sig_end - start + 1, signature=sig)
            if is_object:
                typed_member_depths.add(start_depth + 1)
            continue
        if is_multiline_typed_const:
            collected = _collect_multiline_typed_arrow_sig(lines, i)
            if collected is None:
                continue
            sig, sig_end, _ = collected
            signature_end = sig_end
            start = seek_comment_start(lines, i, is_walkback)
            end = _seek_expression_end(lines, sig_end)
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)
            continue
        sig, sig_end, has_body = _collect_sig(lines, i, is_class_method or is_class_field_fn or is_typed_member or is_prototype_member, is_wrapper)
        signature_end = sig_end
        start = seek_comment_start(lines, i, is_walkback)
        end = _seek_expression_end(lines, sig_end) if is_const and has_body else (seek_brace_end(lines, sig_end) if has_body else sig_end + 1)
        yield OutlineItem(start=start + 1, count=end - start, signature=sig)
        if has_body and (_CLASS_RE.match(clean) or (is_const and _CLASS_EXPR_RE.search(clean))):
            class_depths.add(start_depth + 1)
        if has_body and is_namespace:
            namespace_depths.add(start_depth + 1)
        if has_body and (_IFACE_RE.match(clean) or is_ambient_var):
            typed_member_depths.add(start_depth + 1)
        if has_body and is_prototype_object:
            prototype_depths.add(start_depth + 1)

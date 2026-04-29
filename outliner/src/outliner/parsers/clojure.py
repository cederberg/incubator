"""Clojure outline parser."""

import re

from outliner.types import OutlineItem
from outliner.parsers.util import seek_comment_start

SYNTAX = "clojure"
EXTENSIONS = (".clj", ".cljs", ".cljc")

# Top-level forms to outline; anchored to column 0 (no leading whitespace)
_TOP_FORM_RE = re.compile(
    r"^\((?:defn-?|defmacro|deftype|defrecord|defprotocol|defmulti|ns|def)\s+"
)

# Forms that expect a parameter/field vector [params] as their structural element
_PARAM_VECTOR_RE = re.compile(r"^\((?:defn-?|defmacro|deftype|defrecord)\s+")

_NS_RE   = re.compile(r"^\(ns\s+[\w.-]+")
_DEFN_RE = re.compile(r"^\(defn\s+\w")
_DEF_RE  = re.compile(r"^\(def\s+\w")


def detect(lines: list[str]) -> bool:
    """Detect Clojure: (ns ...) declaration, or both defn and def at line start."""
    if any(_NS_RE.match(l) for l in lines):
        return True
    return any(_DEFN_RE.match(l) for l in lines) and any(_DEF_RE.match(l) for l in lines)


def _string_interior_lines(lines: list[str]) -> set[int]:
    """Return 0-based indices of lines whose first character is inside a string literal.

    Used to skip false-positive top-level form matches inside multi-line strings
    (e.g. code examples in docstrings).  Clojure character literals ``\\(`` are
    handled so they do not accidentally toggle string state.
    """
    in_string = False
    result: set[int] = set()
    for i, raw in enumerate(lines):
        if in_string:
            result.add(i)
        j = 0
        while j < len(raw):
            ch = raw[j]
            if in_string:
                if ch == "\\":
                    j += 2
                    continue
                if ch == '"':
                    in_string = False
            else:
                if ch == "\\":
                    j += 2  # character literal — skip the next char
                    continue
                if ch == '"':
                    in_string = True
                elif ch == ";":
                    break  # rest is a line comment
            j += 1
    return result


def _seek_paren_end(lines: list[str], start: int) -> int:
    """Return 0-based exclusive end of the paren-balanced form starting at start.

    Handles string literals and Clojure character literals (``\\(`` etc.) so
    neither triggers spurious depth changes.
    """
    depth = 0
    in_string = False
    for i in range(start, len(lines)):
        j = 0
        raw = lines[i]
        while j < len(raw):
            ch = raw[j]
            if in_string:
                if ch == "\\":
                    j += 2
                    continue
                if ch == '"':
                    in_string = False
            else:
                if ch == "\\":
                    j += 2  # character literal — skip next char
                    continue
                if ch == '"':
                    in_string = True
                elif ch == ";":
                    break  # line comment
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth <= 0:
                        return i + 1
            j += 1
    return len(lines)


def _collect_sig(lines: list[str], start: int) -> str:
    """Collect a Clojure form signature.

    For forms with a param vector (defn/defmacro/deftype/defrecord): gathers
    text up to and including the first ``[params]`` at paren depth 1.  Stops
    early when a sub-form opens before any vector is seen (multi-arity defn,
    defprotocol methods, etc.).

    For other forms (def, ns, defprotocol, defmulti): collects the first line
    of the form, stopping at the form close or at a nested sub-form.

    Metadata is stripped from the signature:
    - ``^{...}`` reader-macro annotations: skipped everywhere; preceding ``^``
      also removed.
    - Plain ``{...}`` attribute maps before the param vector: skipped for
      param-vector forms (defn/defmacro/deftype/defrecord).

    Returns the signature string.
    """
    has_param_vector = bool(_PARAM_VECTOR_RE.match(lines[start]))

    parts: list[str] = []
    paren_depth = 0
    bracket_depth = 0
    in_string = False
    found_bracket = False  # True once the first '[' at paren_depth==1 is seen
    meta_depth = 0         # depth inside a skipped {..} metadata/attribute map

    for i in range(start, min(start + 50, len(lines))):
        raw = lines[i]
        line_buf: list[str] = []
        stop = False
        j = 0

        while j < len(raw):
            ch = raw[j]

            # --- string literal handling (highest priority) ---
            if in_string:
                if ch == "\\":
                    j += 2
                    continue
                if ch == '"':
                    in_string = False
                j += 1
                continue

            if ch == '"':
                in_string = True
                j += 1
                continue

            if ch == ";":
                break  # rest of line is a comment

            # --- character literal: skip the next character entirely ---
            if ch == "\\":
                j += 2
                continue

            # --- inside a skipped metadata map: track {/} nesting only ---
            if meta_depth > 0:
                if ch == "{":
                    meta_depth += 1
                elif ch == "}":
                    meta_depth -= 1
                j += 1
                continue

            # --- normal character dispatch ---
            if ch == "(":
                paren_depth += 1
                if paren_depth >= 2 and not found_bracket:
                    # Sub-form opened before the param vector — stop sig here
                    stop = True
                    break
                line_buf.append(ch)
            elif ch == ")":
                paren_depth -= 1
                if paren_depth <= 0:
                    stop = True
                    break
                line_buf.append(ch)
            elif ch == "{":
                # ^{...} reader-macro metadata: skip and strip preceding '^'
                if line_buf and line_buf[-1] == "^":
                    line_buf.pop()
                    meta_depth = 1
                elif has_param_vector and paren_depth == 1 and not found_bracket:
                    # Plain attribute map before the param vector — skip it
                    meta_depth = 1
                else:
                    line_buf.append(ch)
            elif ch == "}":
                line_buf.append(ch)
            elif ch == "[":
                if has_param_vector and paren_depth == 1:
                    found_bracket = True
                bracket_depth += 1
                line_buf.append(ch)
            elif ch == "]":
                bracket_depth -= 1
                line_buf.append(ch)
                if found_bracket and bracket_depth == 0 and paren_depth == 1:
                    # First top-level param vector closed — signature complete
                    stop = True
                    break
            else:
                line_buf.append(ch)

            j += 1

        line_text = "".join(line_buf).strip()
        if line_text:
            parts.append(line_text)
        if stop:
            break

    sig = " ".join(parts)
    sig = re.sub(r"\s+", " ", sig).strip()
    if sig and not sig.startswith("("):
        sig = "(" + sig
    if sig and not sig.endswith(")"):
        sig += ")"
    return sig


def parse(text: str) -> list[OutlineItem]:
    lines = text.splitlines()
    in_str = _string_interior_lines(lines)
    items: list[OutlineItem] = []
    for i, raw in enumerate(lines):
        if i in in_str:
            continue
        if not _TOP_FORM_RE.match(raw):
            continue
        sig = _collect_sig(lines, i)
        form_end = _seek_paren_end(lines, i)
        start = seek_comment_start(lines, i, lambda _, s: s[0] == ";")
        items.append(OutlineItem(
            start=start + 1,
            count=form_end - start,
            signature=sig,
        ))
    return items

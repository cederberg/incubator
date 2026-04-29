"""Shell/Bash outline parser (regex-based)."""

import re
from collections.abc import Iterator

from outliner.types import OutlineItem
from outliner.parsers.util import indent_level, seek_comment_start, seek_brace_end

SYNTAX = "shell"
EXTENSIONS = (".sh", ".bash", ".zsh", ".ksh")

# Shebang: #!/bin/sh, #!/bin/bash, #!/bin/dash, #!/bin/ash, #!/usr/bin/env bash, etc.
_SHEBANG_RE = re.compile(r"^#!.*\b(?:ba|da|k|z|a)?sh\b")

# POSIX-style function: name() { ...
# Hyphen excluded from name: POSIX only allows [a-zA-Z0-9_] identifiers.
_POSIX_FUNC_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\)\s*(?:\{|$)")

# Bash keyword: function name [()]  { ...
# Hyphen allowed: bash permits hyphens in function names with the keyword syntax.
_BASH_FUNC_RE = re.compile(
    r"^\s*function\s+([a-zA-Z_][a-zA-Z0-9_-]*)\s*(?:\(\s*\))?\s*(?:\{|$)"
)

# Shell-specific control-flow keywords that co-occur with function defs
_SHELL_KW_RE = re.compile(r"^\s*(?:fi|done|esac)\s*$|^\s*local\s+\w")

# Strip ' { body' from function header line to produce a clean signature.
# Note: seek_brace_end counts raw '{'/'}' characters; unbalanced '}' inside
# comments or strings in the function body will fool it (accepted limitation).
_BODY_RE = re.compile(r"\s*\{.*$")


def detect(lines: list[str]) -> bool:
    """Detect Shell: shebang with shell interpreter, or function defs + shell keywords."""
    for line in lines[:3]:
        if _SHEBANG_RE.match(line):
            return True
    has_func = any(_POSIX_FUNC_RE.match(l) or _BASH_FUNC_RE.match(l) for l in lines)
    has_kw = any(_SHELL_KW_RE.match(l) for l in lines)
    return has_func and has_kw


def _func_sig(lines: list[str], i: int) -> tuple[str, int]:
    """Return (indented_signature, sig_line_0based).

    Shell function signatures are single-line; strip the trailing body opener.
    """
    raw = lines[i]
    ind = " " * indent_level(raw)
    sig = _BODY_RE.sub("", raw.strip())
    return ind + sig, i


def parse(text: str) -> Iterator[OutlineItem]:
    for i, line in enumerate(lines := text.splitlines()):
        if _POSIX_FUNC_RE.match(line) or _BASH_FUNC_RE.match(line):
            _is_comment = lambda ln, s, d=indent_level(line): indent_level(ln) >= d and s.startswith("#")
            sig, sig_end = _func_sig(lines, i)
            start = seek_comment_start(lines, i, _is_comment)
            end = seek_brace_end(lines, sig_end)
            yield OutlineItem(start=start + 1, count=end - start, signature=sig)

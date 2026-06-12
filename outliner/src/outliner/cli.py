"""outliner — print structural outline of source files."""

import argparse
import fnmatch
import os
import re
import shutil
import sys

from outliner.parsers import NAMES, EXTENSIONS, detect, outline, syntax
from outliner.parsers.util import format_count, format_size
from outliner.types import OutlineItem

_TEXT_CONTROLS = "\n\r\t\f\b"
_BINARY_THRESHOLD = 0.05


def die(msg: str, code: int = 2) -> None:
    print(f"outliner: {msg}", file=sys.stderr)
    sys.exit(code)


def guess_syntax(src: str) -> str | None:
    return EXTENSIONS.get(os.path.splitext(src.lower())[1])


def _load_gitignore(dirpath: str) -> list[str]:
    try:
        with open(os.path.join(dirpath, ".gitignore"), encoding="utf-8", errors="replace") as f:
            return [ln.rstrip("\n") for ln in f if ln.strip() and not ln.startswith("#")]
    except OSError:
        return []


def _gitignore_match(name: str, relpath: str, patterns: list[str], is_dir: bool) -> bool:
    result = False
    for pat in patterns:
        negate = pat.startswith("!")
        p = pat[1:] if negate else pat
        dir_only = p.endswith("/")
        if dir_only:
            if not is_dir:
                continue
            p = p[:-1]
        target = relpath if "/" in p else name
        if fnmatch.fnmatch(target, p.lstrip("/")):
            result = not negate
    return result


def _is_ignored(name: str, root: str, gi: dict[str, list[str]], is_dir: bool) -> bool:
    for gi_dir, pats in gi.items():
        if gi_dir == root or root.startswith(gi_dir + os.sep):
            rel = os.path.relpath(os.path.join(root, name), gi_dir)
            if _gitignore_match(name, rel, pats, is_dir):
                return True
    return False


def _expand_sources(
    sources: list[str],
    types: set[str] | None = None,
    excludes: list[str] | None = None,
) -> list[str]:
    result = []
    for src in sources:
        if src == "-" or not os.path.isdir(src):
            result.append(src)
            continue
        # CLI excludes behave like a .gitignore in the walk root
        gi: dict[str, list[str]] = {os.path.normpath(src): list(excludes)} if excludes else {}
        for root, dirs, files in os.walk(src):
            pats = _load_gitignore(root)
            if pats:
                gi[root] = gi.get(root, []) + pats
            dirs[:] = sorted(d for d in dirs
                             if not d.startswith(".") and not _is_ignored(d, root, gi, True))
            for name in sorted(files):
                wanted = not types or guess_syntax(name) in types
                if wanted and not _is_ignored(name, root, gi, False):
                    result.append(os.path.join(root, name))
    return result


def _format_items(items: list[OutlineItem], grep: re.Pattern | None, line_width: int) -> list[str]:
    if grep:
        items = [it for it in items if grep.search(it.signature)]
    if not items:
        return []
    fmt_width = max(it.fmt_width for it in items)
    fmt_width = max(fmt_width, 3)
    return [it.format(fmt_width, line_width) for it in items]


def _looks_binary(head: str) -> bool:
    if "\0" in head:
        return True
    if head:
        controls = sum(1 for ch in head if ord(ch) < 32 and ch not in _TEXT_CONTROLS)
        replaced = head.count("\ufffd")
        return (controls + replaced) / len(head) > _BINARY_THRESHOLD
    return False


def _unsupported_items(size: int, line_count: int) -> list[OutlineItem]:
    plural = "s" if line_count != 1 else ""
    sig = f"{format_size(size)} \u00b7 {format_count(line_count)} line{plural}"
    return [OutlineItem(locator="unsupported file", signature=sig)]


def _outline_source(src: str, selected: str | None) -> tuple[list[OutlineItem] | None, str]:
    if src == "-":
        if selected:
            return outline(selected, sys.stdin), selected
        text = sys.stdin.read().removeprefix("\ufeff")
        match = detect(text)
        if match:
            return outline(match, text), match
        if not text.strip():
            return [], "unsupported"
        return _unsupported_items(len(text), len(text.splitlines())), "unsupported"

    with open(src, encoding="utf-8-sig", errors="replace") as fh:
        head = fh.read(4096)
        if _looks_binary(head):
            size = format_size(os.path.getsize(src))
            return [OutlineItem(locator="binary file", signature=size)], "binary"
        match = selected or guess_syntax(src) or detect(head)
        if match:
            fh.seek(0)
            return outline(match, fh), match
        line_count, tail = head.count("\n"), head
        while chunk := fh.read(1 << 20):
            line_count += chunk.count("\n")
            tail = chunk
        if tail and not tail.endswith("\n"):
            line_count += 1
        return _unsupported_items(os.path.getsize(src), line_count), "unsupported"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="outliner",
        description="Print the structural outline of source files.",
    )
    ap.add_argument("files", nargs="*", metavar="FILE",
                    help="Files to outline (omit or use - for stdin)")
    ap.add_argument("-g", "--grep", metavar="EXPR",
                    help="Only show items whose signature matches EXPR (case-insensitive)")
    ap.add_argument("-s", "--syntax", metavar="LANG",
                    help=f"Override syntax auto-detection (available: {', '.join(NAMES)})")
    ap.add_argument("-t", "--type", action="append", metavar="LANG",
                    help="Only include files of this language or extension (repeatable)")
    ap.add_argument("-w", "--width", metavar="COLS", default="120",
                    help="Truncate output lines to COLS (0=unlimited, auto=terminal width, default=120)")
    ap.add_argument("-x", "--exclude", action="append", metavar="PATTERN",
                    help="Exclude matching files from directory walks, like .gitignore (repeatable)")
    args = ap.parse_args(argv)

    grep_re: re.Pattern | None = None
    if args.grep:
        try:
            grep_re = re.compile(args.grep, re.IGNORECASE)
        except re.error as exc:
            die(f"invalid --grep expression: {exc}")

    line_width: int
    if args.width == "auto":
        line_width = shutil.get_terminal_size(fallback=(120, 24)).columns
    else:
        try:
            line_width = int(args.width)
        except ValueError:
            die(f"invalid --width value: {args.width}")
        if line_width < 0:
            die(f"--width must be >= 0")

    if args.syntax:
        original_syntax = args.syntax
        args.syntax = syntax(args.syntax)
        if args.syntax is None:
            die(f"unknown syntax '{original_syntax}' (try a language name like 'python' or extension like '.py')")

    types = None
    if args.type:
        types = set()
        for name in args.type:
            r = syntax(name)
            if r is None:
                die(f"unknown --type '{name}' (try a language name like 'python' or extension like '.py')")
            types.add(r)

    sources = args.files or ["-"]
    if sources == ["-"] and sys.stdin.isatty():
        ap.print_help()
        return 0
    sources = _expand_sources(sources, types, args.exclude)
    multi = len(sources) > 1

    exit_code = 0
    for src in sources:
        try:
            items, _ = _outline_source(src, args.syntax)
        except OSError as exc:
            print(f"outliner: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        output_lines = _format_items(items, grep_re, line_width)

        if output_lines:
            if multi:
                print(f"\n==> {src} <==")
            print("\n".join(output_lines))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

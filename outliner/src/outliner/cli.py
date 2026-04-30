"""outliner — print structural outline of source files."""

import argparse
import fnmatch
import os
import re
import sys

from outliner.parsers import NAMES, EXTENSIONS, detect, outline
from outliner.types import OutlineItem


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


def _expand_sources(sources: list[str]) -> list[str]:
    result = []
    for src in sources:
        if src == "-" or not os.path.isdir(src):
            result.append(src)
            continue
        gi: dict[str, list[str]] = {}
        for root, dirs, files in os.walk(src):
            pats = _load_gitignore(root)
            if pats:
                gi[root] = pats
            active = [(d, gi[d]) for d in gi if d == root or root.startswith(d + os.sep)]

            def ignored(name: str, is_dir: bool, _root: str = root, _active=active) -> bool:
                for gi_dir, pats in _active:
                    rel = os.path.relpath(os.path.join(_root, name), gi_dir)
                    if _gitignore_match(name, rel, pats, is_dir):
                        return True
                return False

            dirs[:] = sorted(d for d in dirs if not ignored(d, True))
            for name in sorted(files):
                if os.path.splitext(name.lower())[1] in EXTENSIONS and not ignored(name, False):
                    result.append(os.path.join(root, name))
    return result


def _format_items(items: list[OutlineItem], grep: re.Pattern | None) -> list[str]:
    if grep:
        items = [it for it in items if grep.search(it.signature)]
    if not items:
        return []

    max_start_width = max(3, max(len(str(it.start)) for it in items))
    max_field_width = 2 * max_start_width + 1

    lines = []
    for it in items:
        start_str = str(it.start).rjust(max_start_width)
        combined = f"{start_str},{it.count}"
        lines.append(f"{combined.ljust(max_field_width)}  {it.signature}")
    return lines


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
    args = ap.parse_args(argv)

    grep_re: re.Pattern | None = None
    if args.grep:
        try:
            grep_re = re.compile(args.grep, re.IGNORECASE)
        except re.error as exc:
            print(f"outliner: invalid --grep expression: {exc}", file=sys.stderr)
            return 2

    sources = args.files or ["-"]
    if sources == ["-"] and sys.stdin.isatty():
        ap.print_help()
        return 0
    sources = _expand_sources(sources)
    multi = len(sources) > 1

    exit_code = 0
    for src in sources:
        try:
            if src == "-":
                text = sys.stdin.read()
            else:
                with open(src, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
        except OSError as exc:
            print(f"outliner: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        syntax = args.syntax or guess_syntax(src) or detect(text)

        if syntax is None:
            print(f"outliner: cannot auto-detect syntax for '{src}'; use --syntax",
                  file=sys.stderr)
            exit_code = 2
            continue

        items = outline(syntax, text)
        if items is None:
            available = ", ".join(NAMES)
            print(f"outliner: unsupported syntax '{syntax}'; available: {available}",
                  file=sys.stderr)
            exit_code = 2
            continue

        output_lines = _format_items(items, grep_re)

        if output_lines:
            if multi:
                print(f"\n==> {src} <==")
            print("\n".join(output_lines))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

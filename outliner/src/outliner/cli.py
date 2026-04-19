"""outline — print structural outline of source files."""

import argparse
import os
import re
import sys

from outliner.parsers import detect, outline, NAMES, EXTENSIONS
from outliner.types import OutlineItem


def guess_syntax(src: str) -> str | None:
    return EXTENSIONS.get(os.path.splitext(src.lower())[1])


def _format_items(items: list[OutlineItem], grep: re.Pattern | None) -> list[str]:
    if grep:
        items = [it for it in items if grep.search(it.signature)]
    if not items:
        return []

    max_start_width = max(len(str(it.start)) for it in items)
    max_field_width = max(len(f"{it.start},{it.count}") for it in items)

    lines = []
    for it in items:
        start_str = str(it.start).rjust(max_start_width)
        combined = f"{start_str},{it.count}"
        lines.append(f"{combined.ljust(max_field_width)}  {it.signature}")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="outline",
        description="Print the structural outline of source files.",
    )
    ap.add_argument("files", nargs="*", metavar="FILE",
                    help="Files to outline (omit or use - for stdin)")
    ap.add_argument("-g", "--grep", metavar="EXPR",
                    help="Only show items whose signature matches EXPR")
    ap.add_argument("-s", "--syntax", metavar="LANG",
                    help=f"Override syntax auto-detection (available: {', '.join(NAMES)})")
    args = ap.parse_args(argv)

    grep_re: re.Pattern | None = None
    if args.grep:
        try:
            grep_re = re.compile(args.grep)
        except re.error as exc:
            print(f"outline: invalid --grep expression: {exc}", file=sys.stderr)
            return 2

    sources: list[tuple[str, str | None]] = []
    if not args.files:
        sources = [("-", args.syntax)]
    else:
        for f in args.files:
            sources.append((f, args.syntax))

    multi = len(sources) > 1

    exit_code = 0
    for src, explicit_syntax in sources:
        try:
            if src == "-":
                text = sys.stdin.read()
            else:
                with open(src, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
        except OSError as exc:
            print(f"outline: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        syntax = explicit_syntax or guess_syntax(src) or detect(text)

        if syntax is None:
            print(f"outline: cannot auto-detect syntax for '{src}'; use --syntax",
                  file=sys.stderr)
            exit_code = 2
            continue

        items = outline(syntax, text)
        if items is None:
            available = ", ".join(NAMES)
            print(f"outline: unsupported syntax '{syntax}'; available: {available}",
                  file=sys.stderr)
            exit_code = 2
            continue

        output_lines = _format_items(items, grep_re)

        if multi:
            print(f"\n==> {src} <==")
        if output_lines:
            print("\n".join(output_lines))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

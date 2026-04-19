"""Smoke tests for the CLI entry point."""

import contextlib
import io
import sys
from pathlib import Path

from outliner.cli import main

FIXTURES = Path(__file__).parent / "fixtures" / "md"


def run(*args, stdin_text=None):
    """Run main() with captured stdout/stderr; return (stdout, stderr, rc)."""
    out, err = io.StringIO(), io.StringIO()
    old_stdin = sys.stdin
    if stdin_text is not None:
        sys.stdin = io.StringIO(stdin_text)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = main(list(args))
    finally:
        sys.stdin = old_stdin
    return out.getvalue(), err.getvalue(), rc


# ---------------------------------------------------------------------------
# Basic file outlines
# ---------------------------------------------------------------------------

def test_single_file():
    stdout, stderr, rc = run(str(FIXTURES / "atx.md"))
    assert rc == 0
    assert "Title" in stdout
    assert "Section One" in stdout


def test_multi_file_headers():
    f1 = str(FIXTURES / "atx.md")
    f2 = str(FIXTURES / "setext.md")
    stdout, _, rc = run(f1, f2)
    assert rc == 0
    assert "==> " in stdout
    assert "atx.md" in stdout
    assert "setext.md" in stdout


def test_grep_filters():
    stdout, _, rc = run("-g", "Section", str(FIXTURES / "atx.md"))
    assert rc == 0
    assert "Section" in stdout
    assert "Title" not in stdout


def test_grep_no_match_empty_output():
    stdout, _, rc = run("-g", "XXXXNOTFOUND", str(FIXTURES / "atx.md"))
    assert rc == 0
    assert stdout.strip() == ""


# ---------------------------------------------------------------------------
# Stdin
# ---------------------------------------------------------------------------

def test_stdin_no_syntax_uses_markdown_fallback():
    # No --syntax and no extension → markdown catch-all → empty outline, rc=0
    stdout, _, rc = run(stdin_text="")
    assert rc == 0
    assert stdout.strip() == ""


def test_stdin_with_syntax():
    md = "# Hello\n\nworld\n"
    stdout, _, rc = run("--syntax", "markdown", "-", stdin_text=md)
    assert rc == 0
    assert "Hello" in stdout


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_missing_file():
    _, stderr, rc = run("/nonexistent/path/file.md")
    assert rc == 1
    assert "outline:" in stderr


def test_unknown_extension_falls_back_to_markdown():
    # Unknown extension → content detection → markdown catch-all
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".unknown_ext_xyz", mode="w", delete=False) as f:
        f.write("# Hello\n\nworld\n")
        fname = f.name
    try:
        stdout, _, rc = run(fname)
        assert rc == 0
        assert "Hello" in stdout
    finally:
        os.unlink(fname)


def test_bad_grep_regex():
    _, stderr, rc = run("-g", "[invalid", str(FIXTURES / "atx.md"))
    assert rc == 2
    assert "invalid" in stderr.lower() or "--grep" in stderr


def test_unsupported_syntax():
    _, stderr, rc = run("--syntax", "cobol", str(FIXTURES / "atx.md"))
    assert rc == 2
    assert "unsupported syntax" in stderr
    assert "available:" in stderr


# ---------------------------------------------------------------------------
# Output format
# ---------------------------------------------------------------------------

def test_output_columns_aligned():
    stdout, _, rc = run(str(FIXTURES / "atx.md"))
    assert rc == 0
    lines = [l for l in stdout.splitlines() if l.strip()]
    # Each line must have a "start,count  signature" structure
    for line in lines:
        parts = line.split("  ", 1)
        assert len(parts) == 2, f"bad line: {line!r}"
        loc = parts[0].strip()
        assert "," in loc

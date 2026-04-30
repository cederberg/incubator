"""Smoke tests for the CLI entry point."""

import contextlib
import io
import os
import sys
import tempfile
from pathlib import Path

from outliner.cli import main, _expand_sources

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
    assert "outliner:" in stderr


def test_unknown_extension_falls_back_to_markdown():
    # Unknown extension → content detection → markdown catch-all
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
        parts = line.lstrip().split("  ", 1)
        assert len(parts) == 2, f"bad line: {line!r}"
        loc = parts[0].strip()
        assert "," in loc


# ---------------------------------------------------------------------------
# .gitignore support
# ---------------------------------------------------------------------------

def _make_pyfile(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("def foo(): pass\n")


def test_gitignore_excludes_files():
    with tempfile.TemporaryDirectory() as d:
        keep = os.path.join(d, "keep.py")
        skip = os.path.join(d, "ignore_me.py")
        _make_pyfile(keep)
        _make_pyfile(skip)
        with open(os.path.join(d, ".gitignore"), "w") as f:
            f.write("ignore_me.py\n")
        sources = _expand_sources([d])
        assert keep in sources
        assert skip not in sources


def test_gitignore_excludes_dir():
    with tempfile.TemporaryDirectory() as d:
        main_py = os.path.join(d, "main.py")
        gen_py = os.path.join(d, "build", "gen.py")
        _make_pyfile(main_py)
        _make_pyfile(gen_py)
        with open(os.path.join(d, ".gitignore"), "w") as f:
            f.write("build/\n")
        sources = _expand_sources([d])
        assert main_py in sources
        assert gen_py not in sources


def test_gitignore_negation():
    with tempfile.TemporaryDirectory() as d:
        a_py = os.path.join(d, "a.py")
        keep_py = os.path.join(d, "keep.py")
        _make_pyfile(a_py)
        _make_pyfile(keep_py)
        with open(os.path.join(d, ".gitignore"), "w") as f:
            f.write("*.py\n!keep.py\n")
        sources = _expand_sources([d])
        assert keep_py in sources
        assert a_py not in sources


def test_gitignore_subdirectory():
    with tempfile.TemporaryDirectory() as d:
        root_py = os.path.join(d, "root.py")
        util_py = os.path.join(d, "sub", "util.py")
        skip_py = os.path.join(d, "sub", "skip.py")
        _make_pyfile(root_py)
        _make_pyfile(util_py)
        _make_pyfile(skip_py)
        with open(os.path.join(d, "sub", ".gitignore"), "w") as f:
            f.write("skip.py\n")
        sources = _expand_sources([d])
        assert root_py in sources
        assert util_py in sources
        assert skip_py not in sources


def test_gitignore_does_not_affect_explicit_file():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "explicit.py")
        _make_pyfile(path)
        with open(os.path.join(d, ".gitignore"), "w") as f:
            f.write("*.py\n")
        sources = _expand_sources([path])
        assert path in sources

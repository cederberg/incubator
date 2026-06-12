"""Smoke tests for the CLI entry point."""

import contextlib
import io
import os
import sys
import tempfile
import types
from pathlib import Path

import outliner.cli as cli
import outliner.parsers as parsers
from outliner.cli import main, _expand_sources
from outliner.types import OutlineItem

FIXTURES = Path(__file__).parent / "fixtures" / "md"


def run(*args, stdin_text=None):
    """Run main() with captured stdout/stderr; return (stdout, stderr, rc)."""
    out, err = io.StringIO(), io.StringIO()
    old_stdin = sys.stdin
    if stdin_text is not None:
        sys.stdin = io.StringIO(stdin_text)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = main(list(args))
            except SystemExit as e:
                rc = e.code if e.code is not None else 0
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


def test_file_sources_are_passed_to_outline_as_rewound_handles(monkeypatch):
    def fake_outline(match, content):
        assert match == "markdown"
        assert hasattr(content, "read")
        assert content.tell() == 0
        assert content.read(1) == "#"
        return [OutlineItem(start=1, count=1, signature="# Title")]

    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write("# Title\n\nBody.\n")
        fname = f.name
    try:
        monkeypatch.setattr(cli, "outline", fake_outline)
        stdout, _, rc = run(fname)
        assert rc == 0
        assert "Title" in stdout
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# Stdin
# ---------------------------------------------------------------------------

def test_stdin_empty_produces_no_output():
    stdout, _, rc = run(stdin_text="")
    assert rc == 0
    assert stdout.strip() == ""


def test_stdin_unknown_content_reports_unsupported():
    stdout, _, rc = run(stdin_text="key: value\nother: 2\n")
    assert rc == 0
    assert "unsupported file" in stdout
    assert "2 lines" in stdout


def test_stdin_markdown_content_detected():
    stdout, _, rc = run(stdin_text="# Title\n\nBody text.\n")
    assert rc == 0
    assert "# Title" in stdout


def test_stdin_with_syntax():
    md = "# Hello\n\nworld\n"
    stdout, _, rc = run("--syntax", "markdown", "-", stdin_text=md)
    assert rc == 0
    assert "Hello" in stdout


def test_stdin_with_read_parser(monkeypatch):
    def read(fh):
        assert fh is sys.stdin
        assert hasattr(fh, "read")
        return [OutlineItem(start=1, count=1, signature=fh.read())]

    monkeypatch.setitem(parsers._MODULES, "stdin-stream-test", types.SimpleNamespace(read=read))
    stdout, _, rc = run("--syntax", "stdin-stream-test", "-", stdin_text="stream stdin")
    assert rc == 0
    assert "stream stdin" in stdout


def test_stdin_with_json_syntax():
    stdout, _, rc = run("--syntax", "json", "-", stdin_text='{"a": 1}\n{"b": 2}\n')
    assert rc == 0
    assert "ndjson" in stdout


def test_stdin_bom_stripped_before_detect():
    html = "\ufeff<!DOCTYPE html>\n<html>\n<body><h1>Hi</h1></body>\n</html>\n"
    stdout, _, rc = run("-", stdin_text=html)
    assert rc == 0
    assert "<h1>Hi</h1>" in stdout


def test_bom_file():
    with tempfile.NamedTemporaryFile(suffix=".json", mode="wb", delete=False) as f:
        f.write(b'\xef\xbb\xbf{"a": 1}\n')
        fname = f.name
    try:
        stdout, _, rc = run(fname)
        assert rc == 0
        assert ".a" in stdout
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_missing_file():
    _, stderr, rc = run("/nonexistent/path/file.md")
    assert rc == 1
    assert "outliner:" in stderr


def test_unknown_extension_with_heading_detects_markdown():
    with tempfile.NamedTemporaryFile(suffix=".unknown_ext_xyz", mode="w", delete=False) as f:
        f.write("# Hello\n\nworld\n")
        fname = f.name
    try:
        stdout, _, rc = run(fname)
        assert rc == 0
        assert "Hello" in stdout
    finally:
        os.unlink(fname)


def test_unknown_extension_reports_unsupported():
    with tempfile.NamedTemporaryFile(suffix=".unknown_ext_xyz", mode="w", delete=False) as f:
        f.write("key: value\nlist:\n  - a\n  - b\n")
        fname = f.name
    try:
        stdout, _, rc = run(fname)
        assert rc == 0
        assert "unsupported file" in stdout
        assert "4 lines" in stdout
    finally:
        os.unlink(fname)


def test_binary_file_reports_summary_instead_of_markdown_garbage():
    with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as f:
        f.write(b"\x1f\x8b\x08\x00# random compressed-ish bytes\x00\x00\xff")
        fname = f.name
    try:
        stdout, stderr, rc = run(fname)
        assert rc == 0
        assert stderr == ""
        assert "binary file" in stdout
        assert "B" in stdout
        assert stdout.strip().startswith("binary file")
        assert "#" not in stdout
    finally:
        os.unlink(fname)


def test_binary_file_guard_overrides_explicit_syntax():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"\x00# Not a heading\n")
        fname = f.name
    try:
        stdout, _, rc = run("--syntax", "markdown", fname)
        assert rc == 0
        assert "binary file" in stdout
        assert stdout.strip().startswith("binary file")
        assert "Not a heading" not in stdout
    finally:
        os.unlink(fname)


def test_bad_grep_regex():
    _, stderr, rc = run("-g", "[invalid", str(FIXTURES / "atx.md"))
    assert rc == 2
    assert "invalid" in stderr.lower() or "--grep" in stderr


def test_unsupported_syntax():
    _, stderr, rc = run("--syntax", "cobol", str(FIXTURES / "atx.md"))
    assert rc == 2
    assert "unknown syntax" in stderr


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
# Source expansion
# ---------------------------------------------------------------------------

def test_expand_sources_includes_javascript_family_extensions():
    with tempfile.TemporaryDirectory() as d:
        for name in ["a.js", "b.jsx", "c.ts", "d.tsx", "e.mjs", "f.cjs"]:
            Path(d, name).write_text("export function ok() {}\n")
        sources = {Path(src).name for src in _expand_sources([d])}
        assert {"a.js", "b.jsx", "c.ts", "d.tsx", "e.mjs", "f.cjs"} <= sources


def test_expand_sources_includes_unknown_extensions():
    with tempfile.TemporaryDirectory() as d:
        Path(d, "data.yaml").write_text("key: value\n")
        Path(d, "LICENSE").write_text("MIT License\n")
        sources = {Path(src).name for src in _expand_sources([d])}
        assert {"data.yaml", "LICENSE"} <= sources


def test_expand_sources_skips_hidden_dirs():
    with tempfile.TemporaryDirectory() as d:
        _make_pyfile(os.path.join(d, "main.py"))
        _make_pyfile(os.path.join(d, ".git", "hook.py"))
        sources = {Path(src).name for src in _expand_sources([d])}
        assert "main.py" in sources
        assert "hook.py" not in sources


def test_expand_sources_exclude_by_glob():
    with tempfile.TemporaryDirectory() as d:
        _make_pyfile(os.path.join(d, "main.py"))
        Path(d, "data.yaml").write_text("key: value\n")
        Path(d, "more.yaml").write_text("key: value\n")
        sources = {Path(src).name for src in _expand_sources([d], excludes=["*.yaml"])}
        assert sources == {"main.py"}


def test_expand_sources_exclude_dir_pattern():
    with tempfile.TemporaryDirectory() as d:
        _make_pyfile(os.path.join(d, "main.py"))
        _make_pyfile(os.path.join(d, "build", "gen.py"))
        sources = {Path(src).name for src in _expand_sources([d], excludes=["build/"])}
        assert sources == {"main.py"}


def test_expand_sources_exclude_repeatable():
    with tempfile.TemporaryDirectory() as d:
        _make_pyfile(os.path.join(d, "main.py"))
        Path(d, "a.lock").write_text("x\n")
        Path(d, "b.tmp").write_text("x\n")
        sources = {Path(src).name for src in _expand_sources([d], excludes=["*.lock", "*.tmp"])}
        assert sources == {"main.py"}


def test_exclude_does_not_affect_explicit_files():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "main.py")
        _make_pyfile(path)
        assert _expand_sources([path], excludes=["*.py"]) == [path]


def test_exclude_option_end_to_end():
    with tempfile.TemporaryDirectory() as d:
        _make_pyfile(os.path.join(d, "keep.py"))
        _make_pyfile(os.path.join(d, "skip.py"))
        stdout, _, rc = run("-x", "skip.py", d)
        assert rc == 0
        assert "keep.py" in stdout or "def foo" in stdout
        assert "skip.py" not in stdout


def test_expand_sources_type_filter_excludes_unknown():
    with tempfile.TemporaryDirectory() as d:
        _make_pyfile(os.path.join(d, "main.py"))
        Path(d, "data.yaml").write_text("key: value\n")
        sources = {Path(src).name for src in _expand_sources([d], {"python"})}
        assert sources == {"main.py"}


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


# ---------------------------------------------------------------------------
# --type filtering
# ---------------------------------------------------------------------------

def test_type_filters_by_language_name():
    with tempfile.TemporaryDirectory() as d:
        py = os.path.join(d, "test.py")
        md = os.path.join(d, "readme.md")
        _make_pyfile(py)
        Path(md).write_text("# Readme\n")
        stdout, _, rc = run("-t", "python", d)
        assert rc == 0
        assert "foo" in stdout
        assert "Readme" not in stdout


def test_type_accepts_extension():
    with tempfile.TemporaryDirectory() as d:
        py = os.path.join(d, "test.py")
        md = os.path.join(d, "readme.md")
        _make_pyfile(py)
        Path(md).write_text("# Readme\n")
        stdout, _, rc = run("--type", "py", d)
        assert rc == 0
        assert "foo" in stdout
        assert "Readme" not in stdout


def test_type_unknown_rejected():
    _, stderr, rc = run("--type", "cobol", ".")
    assert rc == 2
    assert "unknown" in stderr.lower()


def test_syntax_accepts_extension():
    md = "# Hello\n\nworld\n"
    stdout, _, rc = run("--syntax", "md", "-", stdin_text=md)
    assert rc == 0
    assert "Hello" in stdout

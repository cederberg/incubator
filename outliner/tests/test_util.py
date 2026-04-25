"""Tests for shared parser utilities."""

import outliner.parsers.util as util


def test_indent_level():
    assert util.indent_level("    foo") == 4
    assert util.indent_level("foo") == 0
    assert util.indent_level("  foo\n") == 2


def test_extract_signature():
    assert util.extract_signature(["def  foo(", "  x,", "  y)"]) == "def foo(x, y)"
    assert util.extract_signature(["void foo() {"], strip="{") == "void foo()"
    assert util.extract_signature(["foo( x, y)"]) == "foo(x, y)"
    assert util.extract_signature(["foo(x, )"]) == "foo(x)"


def test_extract_summary():
    assert util.extract_summary("Hello world. More text.") == "Hello world."
    assert util.extract_summary("Hello there! More text.") == "Hello there!"
    assert util.extract_summary("No sentence here", max_len=5) == "No se"
    assert util.extract_summary("Hello world. More.", max_len=5) == "Hello"
    assert util.extract_summary("") == ""
    # short prefix before punctuation is not a sentence boundary
    assert util.extract_summary("1. Introduction") == "1. Introduction"
    assert util.extract_summary("No. It worked.") == "No. It worked."


def test_seek_comment_start():
    is_comment = lambda raw, s: s.startswith("//")
    lines = ["// doc\n", "// comment\n", "void foo() {}\n"]
    assert util.seek_comment_start(lines, 2, is_comment) == 0
    lines = ["// doc\n", "\n", "// comment\n", "void foo() {}\n"]
    assert util.seek_comment_start(lines, 3, is_comment) == 2
    lines = ["void foo() {}\n"]
    assert util.seek_comment_start(lines, 0, is_comment) == 0


def test_seek_brace_end():
    assert util.seek_brace_end(["void foo() {", "    return;", "}"], 0) == 3
    assert util.seek_brace_end(["void foo() {", "    if (x) {", "    }", "}"], 0) == 4
    assert util.seek_brace_end(["function noop() {}"], 0) == 1

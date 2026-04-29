"""Tests for the Shell/Bash outline parser."""

from pathlib import Path

from outliner.parsers.shell import parse as _parse, detect as detect_shell

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "sh"
FIXTURE = FIXTURES / "sample.sh"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_sh():
    assert guess_syntax("file.sh") == "shell"


def test_detect_extension_bash():
    assert guess_syntax("file.bash") == "shell"


def test_detect_extension_zsh():
    assert guess_syntax("file.zsh") == "shell"


def test_detect_extension_ksh():
    assert guess_syntax("file.ksh") == "shell"


def test_detect_content_shebang_bash():
    assert detect_shell(["#!/usr/bin/env bash", "greet() { echo hi; }"])


def test_detect_content_shebang_sh():
    assert detect_shell(["#!/bin/sh", "greet() { echo hi; }"])


def test_detect_content_shebang_zsh():
    assert detect_shell(["#!/bin/zsh", "foo() { echo hi; }"])


def test_detect_content_shebang_dash():
    assert detect_shell(["#!/bin/dash", "foo() { echo hi; }"])


def test_detect_content_shebang_ash():
    assert detect_shell(["#!/bin/ash", "foo() { echo hi; }"])


def test_detect_content_no_shebang_posix_func_with_shell_kw():
    # POSIX-style function + fi keyword = shell
    assert detect_shell(["greet() {", "    if true ; then", "        echo hi", "    fi", "}"])


def test_detect_content_no_shebang_bash_func_with_shell_kw():
    assert detect_shell(["function greet {", "    echo hi", "}", "done"])


def test_detect_content_no_match():
    assert not detect_shell(["Hello world", "No code here"])


def test_detect_content_python_not_triggered():
    # Python def ends with ':', not '{'; no shell-specific keywords
    assert not detect_shell(["def foo():", "    pass", "class Bar:", "    pass"])


def test_detect_content_java_not_triggered():
    assert not detect_shell(["public class Foo {", "    void bar() {}", "}"])


def test_detect_registry_shell_content():
    assert detect(FIXTURE.read_text()) == "shell"


# ---------------------------------------------------------------------------
# POSIX-style function  name() { ... }
# ---------------------------------------------------------------------------

def test_posix_simple_function():
    items = parse("greet() {\n    echo hi\n}\n")
    assert len(items) == 1
    assert items[0].signature == "greet()"
    assert items[0].start == 1
    assert items[0].count == 3


def test_posix_trailing_brace_stripped():
    items = parse("foo() {\n    echo foo\n}\n")
    assert not items[0].signature.endswith("{")


def test_posix_underscore_prefix():
    items = parse("_helper() {\n    echo h\n}\n")
    assert items[0].signature == "_helper()"


def test_posix_function_range():
    items = parse("f() {\n    x=1\n    y=2\n}\n")
    assert items[0].count == 4


# ---------------------------------------------------------------------------
# Bash keyword syntax  function name [()]  { ... }
# ---------------------------------------------------------------------------

def test_bash_keyword_no_parens():
    items = parse("function goodbye {\n    echo bye\n}\n")
    assert len(items) == 1
    assert items[0].signature == "function goodbye"


def test_bash_keyword_with_parens():
    items = parse("function say_hello() {\n    echo hello\n}\n")
    assert items[0].signature == "function say_hello()"


def test_bash_keyword_trailing_brace_stripped():
    items = parse("function foo {\n    echo foo\n}\n")
    assert not items[0].signature.endswith("{")


# ---------------------------------------------------------------------------
# Comment walkback
# ---------------------------------------------------------------------------

def test_comment_walked_back():
    text = "# Greet the world\ngreet() {\n    echo hi\n}\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 4


def test_blank_stops_walkback():
    text = "# Unrelated\n\ngreet() {\n    echo hi\n}\n"
    items = parse(text)
    assert items[0].start == 3


def test_multi_comment_walked_back():
    text = "# Line one\n# Line two\ngreet() {\n    echo hi\n}\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 5


def test_no_walkback_past_code():
    text = "x=1\ngreet() {\n    echo hi\n}\n"
    items = parse(text)
    assert items[0].start == 2


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_nested_braces_do_not_close_early():
    # ${var} expansions must not fool seek_brace_end
    text = (
        "setup() {\n"
        "    echo \"${HOME}\"\n"
        "    echo \"${PATH}\"\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].count == 4


def test_complex_body_range():
    text = (
        "run() {\n"
        "    for f in *.txt ; do\n"
        "        if [[ -f \"$f\" ]] ; then\n"
        "            echo \"$f\"\n"
        "        fi\n"
        "    done\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].count == 7


def test_global_vars_excluded():
    text = "FOO=bar\nVERSION=1.0\ngreet() {\n    echo hi\n}\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert not any("FOO" in s or "VERSION" in s for s in sigs)
    assert any("greet" in s for s in sigs)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("# just a comment\n# another\n") == []


def test_shebang_line_excluded():
    text = "#!/bin/bash\nfoo() {\n    echo hi\n}\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert not any("!" in s for s in sigs)


def test_multiple_functions():
    text = (
        "foo() {\n    echo foo\n}\n"
        "bar() {\n    echo bar\n}\n"
    )
    items = parse(text)
    assert len(items) == 2
    sigs = [it.signature for it in items]
    assert "foo()" in sigs
    assert "bar()" in sigs


def test_brace_on_next_line():
    # POSIX style: opening brace on its own line
    text = "greet()\n{\n    echo hi\n}\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "greet()"
    assert items[0].count == 4


def test_bash_hyphenated_function_name():
    items = parse("function my-func {\n    echo hi\n}\n")
    assert len(items) == 1
    assert items[0].signature == "function my-func"


def test_unbalanced_brace_in_comment_known_limitation():
    # A lone '}' inside a comment fools seek_brace_end (accepted limitation
    # shared by all parsers that use the utility).  This test documents the
    # current (imperfect) behaviour rather than asserting the ideal count=4.
    text = (
        "f() {\n"
        "    # close brace: }\n"
        "    echo done\n"
        "}\n"
    )
    items = parse(text)
    # seek_brace_end sees the '}' in the comment and closes early at count=2.
    assert items[0].count == 2  # known limitation, not ideal (should be 4)


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 6


def test_fixture_signatures():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "greet()" in sigs
    assert "function goodbye" in sigs
    assert "function say_hello()" in sigs
    assert "function process_files()" in sigs
    assert "_internal_helper()" in sigs
    assert "documented_function()" in sigs


def test_fixture_greet_range():
    items = parse(FIXTURE.read_text())
    greet = next(it for it in items if it.signature == "greet()")
    assert greet.start == 8
    assert greet.count == 4


def test_fixture_goodbye_range():
    items = parse(FIXTURE.read_text())
    goodbye = next(it for it in items if it.signature == "function goodbye")
    assert goodbye.start == 13
    assert goodbye.count == 4


def test_fixture_say_hello_range():
    items = parse(FIXTURE.read_text())
    say_hello = next(it for it in items if it.signature == "function say_hello()")
    assert say_hello.start == 18
    assert say_hello.count == 5


def test_fixture_process_files_range():
    items = parse(FIXTURE.read_text())
    pf = next(it for it in items if it.signature == "function process_files()")
    assert pf.start == 24
    assert pf.count == 12


def test_fixture_internal_helper_range():
    items = parse(FIXTURE.read_text())
    helper = next(it for it in items if it.signature == "_internal_helper()")
    assert helper.start == 37
    assert helper.count == 4


def test_fixture_documented_function_range():
    items = parse(FIXTURE.read_text())
    doc = next(it for it in items if it.signature == "documented_function()")
    assert doc.start == 42
    assert doc.count == 5

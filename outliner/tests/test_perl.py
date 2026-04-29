"""Tests for the Perl outline parser."""

from pathlib import Path

from outliner.parsers.perl import parse as _parse, detect as detect_perl

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "pl"
FIXTURE = FIXTURES / "sample.pl"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_pl():
    assert guess_syntax("file.pl") == "perl"


def test_detect_extension_pm():
    assert guess_syntax("file.pm") == "perl"


def test_detect_extension_t():
    assert guess_syntax("file.t") == "perl"


def test_detect_content_shebang_perl():
    assert detect_perl(["#!/usr/bin/perl", "use strict;"])
    assert detect_perl(["#!/usr/bin/env perl", "sub foo { }"])


def test_detect_content_use_strict_with_sub():
    assert detect_perl(["use strict;", "sub greet { return 'hi'; }"])
    assert detect_perl(["use warnings;", "sub foo ($x) { $x }"])


def test_detect_content_package_doublecolon_with_sub():
    assert detect_perl(["package Foo::Bar;", "sub new { bless {}, shift }"])
    assert detect_perl(["package My::Module::Util;", "sub helper { }"])


def test_detect_content_no_match():
    assert not detect_perl(["Hello world", "No code here"])


def test_detect_content_python_not_triggered():
    assert not detect_perl(["def foo():", "    pass", "class Bar:", "    pass"])


def test_detect_content_ruby_not_triggered():
    # Ruby uses 'end' and attr_*, not use strict
    assert not detect_perl(["class Foo", "  def bar", "  end", "end"])


def test_detect_content_sub_alone_not_enough():
    # 'sub' without Perl-specific marker should not match
    assert not detect_perl(["sub greet {", "    return 1", "}"])


def test_detect_registry_perl_content():
    assert detect(FIXTURE.read_text()) == "perl"


# ---------------------------------------------------------------------------
# Simple inline unit tests — package
# ---------------------------------------------------------------------------

def test_simple_package_semicolon():
    items = parse("package Foo;\n\nsub bar { 1 }\n")
    sigs = [it.signature for it in items]
    assert "package Foo" in sigs


def test_package_signature_strips_semicolon():
    items = parse("package Foo;\n")
    assert items[0].signature == "package Foo"
    assert not items[0].signature.endswith(";")


def test_package_count_one_for_no_block():
    items = parse("package Foo;\n\nsub bar { 1 }\n")
    pkg = next(it for it in items if it.signature == "package Foo")
    assert pkg.count == 1


def test_package_block_style():
    text = "package Foo {\n    sub bar { 1 }\n}\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "package Foo" in sigs


def test_package_block_range_covers_methods():
    text = "package Foo {\n    sub bar { 1 }\n}\n"
    items = parse(text)
    pkg = next(it for it in items if it.signature == "package Foo")
    bar = next(it for it in items if "bar" in it.signature)
    assert pkg.start <= bar.start
    assert pkg.start + pkg.count >= bar.start + bar.count


def test_package_main():
    items = parse("package main;\n\nsub run { 1 }\n")
    sigs = [it.signature for it in items]
    assert "package main" in sigs


def test_package_double_colon():
    items = parse("package Foo::Bar;\n\nsub new { bless {}, shift }\n")
    sigs = [it.signature for it in items]
    assert "package Foo::Bar" in sigs


# ---------------------------------------------------------------------------
# Simple inline unit tests — sub
# ---------------------------------------------------------------------------

def test_simple_sub():
    items = parse("sub foo {\n    return 1;\n}\n")
    assert len(items) == 1
    assert items[0].signature == "sub foo"
    assert items[0].start == 1
    assert items[0].count == 3


def test_sub_with_signature():
    items = parse("sub greet ($name) {\n    return $name;\n}\n")
    assert items[0].signature == "sub greet ($name)"


def test_sub_with_multiple_args():
    items = parse("sub add ($x, $y) {\n    return $x + $y;\n}\n")
    assert items[0].signature == "sub add ($x, $y)"


def test_sub_private():
    items = parse("sub _helper {\n    return 'secret';\n}\n")
    assert items[0].signature == "sub _helper"


def test_sub_trailing_brace_stripped():
    items = parse("sub foo {\n    1;\n}\n")
    assert not items[0].signature.endswith("{")


def test_sub_range_covers_body():
    text = "sub foo {\n    my $x = 1;\n    my $y = 2;\n    $x + $y;\n}\n"
    items = parse(text)
    assert items[0].count == 5


def test_use_excluded():
    items = parse("use strict;\nuse warnings;\nsub foo { 1 }\n")
    sigs = [it.signature for it in items]
    assert not any("use" in s for s in sigs)


def test_anonymous_sub_excluded():
    items = parse("my $cb = sub { return 1; };\nsub named { 2 }\n")
    sigs = [it.signature for it in items]
    assert not any("my $cb" in s or "= sub" in s for s in sigs)
    assert any("named" in s for s in sigs)


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_sig_merged():
    text = (
        "sub fetch (\n"
        "    $self,\n"
        "    $item,\n"
        "    $distance,\n"
        ") {\n"
        "    return 1;\n"
        "}\n"
    )
    items = parse(text)
    assert len(items) == 1
    sig = items[0].signature
    assert sig.startswith("sub fetch (")
    assert "$self" in sig
    assert "$item" in sig
    assert "$distance" in sig


def test_multiline_sig_exact():
    text = (
        "sub fetch (\n"
        "    $self,\n"
        "    $item,\n"
        "    $distance = 1.0,\n"
        ") {\n"
        "    return 1;\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].signature == "sub fetch ($self, $item, $distance = 1.0)"


def test_multiline_sig_start_line():
    text = (
        "sub fetch (\n"
        "    $self,\n"
        "    $item,\n"
        ") {\n"
        "    return 1;\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].start == 1


def test_multiline_sig_range():
    text = (
        "sub fetch (\n"
        "    $self,\n"
        "    $item,\n"
        ") {\n"
        "    return 1;\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].count == 6


# ---------------------------------------------------------------------------
# Comment walkback
# ---------------------------------------------------------------------------

def test_comment_walked_back():
    text = "# Does something\nsub foo {\n    1;\n}\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 4


def test_blank_stops_walkback():
    text = "# Unrelated\n\nsub foo {\n    1;\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 3


def test_no_walkback_past_code():
    text = "my $x = 1;\nsub foo {\n    1;\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 2


def test_multiple_comment_lines_walked_back():
    text = "# Line one\n# Line two\nsub foo {\n    1;\n}\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 5


def test_comment_walked_back_for_package():
    text = "# The main package\npackage main;\n"
    items = parse(text)
    pkg = next(it for it in items if "main" in it.signature)
    assert pkg.start == 1


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_two_subs_non_overlapping():
    text = "sub foo {\n    1;\n}\n\nsub bar {\n    2;\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    bar = next(it for it in items if "bar" in it.signature)
    assert foo.start + foo.count <= bar.start


def test_nested_braces_in_body():
    text = (
        "sub fetch {\n"
        "    my %h = { key => 'val' };\n"
        "    return $h{key};\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].count == 4


# ---------------------------------------------------------------------------
# POD block filtering
# ---------------------------------------------------------------------------

def test_pod_example_code_excluded():
    text = (
        "sub real_sub { 1 }\n"
        "=head1 SYNOPSIS\n"
        "\n"
        "  sub example_in_docs { 1 }\n"
        "\n"
        "=cut\n"
        "sub another_real_sub { 2 }\n"
    )
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "sub real_sub" in sigs
    assert "sub another_real_sub" in sigs
    assert not any("example_in_docs" in s for s in sigs)


def test_pod_package_excluded():
    text = (
        "package Real;\n"
        "=pod\n"
        "\n"
        "  package FakeInDocs;\n"
        "\n"
        "=cut\n"
    )
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "package Real" in sigs
    assert not any("FakeInDocs" in s for s in sigs)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("# just a comment\n# another\n") == []


def test_no_sub_only_package():
    items = parse("package Foo;\n")
    assert len(items) == 1
    assert items[0].signature == "package Foo"


def test_inline_oneliner_count():
    items = parse("sub foo { return 1; }\n")
    assert items[0].count == 1


def test_prototype_declaration_excluded():
    # sub foo; (no body) should produce no item
    items = parse("use strict;\nsub foo;\nsub bar { 1 }\n")
    sigs = [it.signature for it in items]
    assert not any("foo" in s for s in sigs)
    assert any("bar" in s for s in sigs)


def test_package_deep_namespace():
    items = parse("package Foo::Bar::Baz;\n")
    assert items[0].signature == "package Foo::Bar::Baz"


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 11


def test_fixture_package_sigs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "package Animal" in sigs
    assert "package Dog" in sigs
    assert "package main" in sigs


def test_fixture_sub_sigs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("make_animal" in s for s in sigs)
    assert any("_helper" in s for s in sigs)
    assert any("speak" in s for s in sigs)


def test_fixture_multiline_fetch_sig():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetch" in it.signature)
    assert fetch.signature == "sub fetch ($self, $item, $distance = 1.0)"


def test_fixture_package_animal_start():
    items = parse(FIXTURE.read_text())
    pkg = next(it for it in items if it.signature == "package Animal")
    assert pkg.start == 7


def test_fixture_package_animal_count():
    items = parse(FIXTURE.read_text())
    pkg = next(it for it in items if it.signature == "package Animal")
    assert pkg.count == 1


def test_fixture_sub_new_animal_start():
    items = parse(FIXTURE.read_text())
    # Animal's new has comment at line 9
    news = [it for it in items if "sub new" in it.signature]
    animal_new = news[0]  # first 'new' belongs to Animal
    assert animal_new.start == 9


def test_fixture_sub_new_animal_count():
    items = parse(FIXTURE.read_text())
    news = [it for it in items if "sub new" in it.signature]
    animal_new = news[0]
    assert animal_new.count == 7  # comment + sub + 5 body lines


def test_fixture_sub_name_start():
    items = parse(FIXTURE.read_text())
    name_sub = next(it for it in items if it.signature == "sub name ($self)")
    assert name_sub.start == 17


def test_fixture_sub_name_count():
    items = parse(FIXTURE.read_text())
    name_sub = next(it for it in items if it.signature == "sub name ($self)")
    assert name_sub.count == 4  # comment + sub + body + }


def test_fixture_sub_speak_animal_start():
    items = parse(FIXTURE.read_text())
    speaks = [it for it in items if "speak" in it.signature]
    animal_speak = speaks[0]
    assert animal_speak.start == 22


def test_fixture_sub_speak_animal_count():
    items = parse(FIXTURE.read_text())
    speaks = [it for it in items if "speak" in it.signature]
    animal_speak = speaks[0]
    assert animal_speak.count == 3


def test_fixture_package_dog_start():
    items = parse(FIXTURE.read_text())
    pkg = next(it for it in items if it.signature == "package Dog")
    assert pkg.start == 30


def test_fixture_fetch_start():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetch" in it.signature)
    assert fetch.start == 43


def test_fixture_fetch_count():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetch" in it.signature)
    assert fetch.count == 8  # comment + sub fetch( + 3 args + ) { + body + }


def test_fixture_package_main_start():
    items = parse(FIXTURE.read_text())
    pkg = next(it for it in items if it.signature == "package main")
    assert pkg.start == 52


def test_fixture_make_animal_start():
    items = parse(FIXTURE.read_text())
    fn = next(it for it in items if "make_animal" in it.signature)
    assert fn.start == 54


def test_fixture_make_animal_count():
    items = parse(FIXTURE.read_text())
    fn = next(it for it in items if "make_animal" in it.signature)
    assert fn.count == 4  # comment + sub + body + }


def test_fixture_make_animal_sig():
    items = parse(FIXTURE.read_text())
    fn = next(it for it in items if "make_animal" in it.signature)
    assert fn.signature == "sub make_animal ($name, $kind = 'unknown')"

"""Tests for the Ruby outline parser."""

from pathlib import Path

from outliner.parsers.ruby import parse, detect as detect_ruby
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "rb"
FIXTURE = FIXTURES / "sample.rb"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_rb():
    assert guess_syntax("file.rb") == "ruby"


def test_detect_extension_rake():
    assert guess_syntax("file.rake") == "ruby"


def test_detect_extension_gemspec():
    assert guess_syntax("file.gemspec") == "ruby"


def test_detect_content_shebang():
    assert detect_ruby(["#!/usr/bin/env ruby", "puts 'hi'"])
    assert detect_ruby(["#!/usr/bin/ruby", "x = 1"])


def test_detect_content_attr_macro():
    assert detect_ruby(["class Foo", "  attr_reader :name", "end"])
    assert detect_ruby(["  attr_accessor :x, :y"])
    assert detect_ruby(["attr_writer :value"])


def test_detect_content_require_relative():
    assert detect_ruby(["require_relative './utils'"])
    assert detect_ruby(["require_relative '../lib/helper'"])


def test_detect_content_def_end_class():
    assert detect_ruby(["class Foo", "  def bar", "  end", "end"])
    assert detect_ruby(["module M", "  class C", "    def f", "    end", "  end", "end"])


def test_detect_content_no_match():
    assert not detect_ruby(["Hello world", "No code here"])


def test_detect_content_python_not_triggered():
    # Python def/class end with ':', not 'end'
    assert not detect_ruby(["def foo():", "    pass", "class Bar:", "    pass"])


def test_detect_content_java_not_triggered():
    assert not detect_ruby(["public class Foo {", "    void bar() {}", "}"])


def test_detect_registry_ruby_content():
    assert detect(FIXTURE.read_text()) == "ruby"


# ---------------------------------------------------------------------------
# Simple inline unit tests
# ---------------------------------------------------------------------------

def test_simple_module():
    items = parse("module Foo\nend\n")
    assert len(items) == 1
    assert items[0].signature == "module Foo"
    assert items[0].start == 1
    assert items[0].count == 2


def test_simple_class():
    items = parse("class Foo\nend\n")
    assert len(items) == 1
    assert items[0].signature == "class Foo"


def test_class_with_parent():
    items = parse("class Dog < Animal\nend\n")
    assert items[0].signature == "class Dog < Animal"


def test_simple_def():
    items = parse("def greet\n  'hello'\nend\n")
    assert len(items) == 1
    assert items[0].signature == "def greet"
    assert items[0].start == 1
    assert items[0].count == 3


def test_def_with_args():
    items = parse("def add(a, b)\n  a + b\nend\n")
    assert items[0].signature == "def add(a, b)"


def test_def_with_keyword_args():
    items = parse("def init(name:, kind: 'unknown')\n  @name = name\nend\n")
    assert items[0].signature == "def init(name:, kind: 'unknown')"


def test_class_method():
    items = parse("def self.create(name)\n  new(name)\nend\n")
    assert items[0].signature == "def self.create(name)"


def test_predicate_method():
    items = parse("def valid?\n  true\nend\n")
    assert items[0].signature == "def valid?"


def test_bang_method():
    items = parse("def save!\n  commit\nend\n")
    assert items[0].signature == "def save!"


def test_operator_method_equality():
    items = parse("class Pt\n  def ==(other)\n    true\n  end\nend\n")
    sigs = [it.signature for it in items]
    assert any("==" in s for s in sigs)


def test_operator_method_spaceship():
    items = parse("class Pt\n  def <=>(other)\n    0\n  end\nend\n")
    sigs = [it.signature for it in items]
    assert any("<=>" in s for s in sigs)


def test_operator_method_index():
    items = parse("class Arr\n  def [](i)\n    @data[i]\n  end\nend\n")
    sigs = [it.signature for it in items]
    assert any("[]" in s for s in sigs)


def test_attr_reader():
    items = parse("class Foo\n  attr_reader :name\nend\n")
    sigs = [it.signature for it in items]
    assert any("attr_reader :name" in s for s in sigs)


def test_attr_accessor():
    items = parse("class Foo\n  attr_accessor :x, :y\nend\n")
    sigs = [it.signature for it in items]
    assert any("attr_accessor :x, :y" in s for s in sigs)


def test_attr_writer():
    items = parse("class Foo\n  attr_writer :value\nend\n")
    sigs = [it.signature for it in items]
    assert any("attr_writer :value" in s for s in sigs)


def test_attr_single_line_count():
    items = parse("class Foo\n  attr_reader :name\nend\n")
    attr = next(it for it in items if "attr_reader" in it.signature)
    assert attr.count == 1


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_sig_merged():
    text = "def fetch(\n  item,\n  distance: 1.0\n)\n  true\nend\n"
    items = parse(text)
    assert len(items) == 1
    sig = items[0].signature
    assert "item" in sig
    assert "distance" in sig
    assert sig.startswith("def fetch(")


def test_multiline_sig_exact():
    text = "def greet(\n  name,\n  greeting: 'Hello'\n)\n  puts greeting\nend\n"
    items = parse(text)
    assert items[0].signature == "def greet(name, greeting: 'Hello')"


# ---------------------------------------------------------------------------
# Comment walkback
# ---------------------------------------------------------------------------

def test_comment_walked_back():
    text = "# Does something\ndef foo\n  42\nend\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 4


def test_blank_stops_walkback():
    text = "# Unrelated\n\ndef foo\n  42\nend\n"
    items = parse(text)
    assert items[0].start == 3


def test_indent_mismatch_stops_walkback():
    # Comment at a shallower indent should not be walked back
    text = "# top-level comment\nclass Foo\n  def bar\n    42\n  end\nend\n"
    items = parse(text)
    bar = next(it for it in items if "bar" in it.signature)
    assert bar.start == 3  # starts at def, not at the outer comment


def test_no_walkback_past_code():
    text = "x = 1\ndef foo\n  42\nend\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 2


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_module_range_covers_class():
    text = "module M\n  class C\n  end\nend\n"
    items = parse(text)
    mod = next(it for it in items if "module M" == it.signature)
    cls = next(it for it in items if "class C" in it.signature)
    assert mod.start <= cls.start
    assert mod.start + mod.count >= cls.start + cls.count


def test_class_range_covers_methods():
    text = "class Foo\n  def bar\n    1\n  end\n  def baz\n    2\n  end\nend\n"
    items = parse(text)
    cls = next(it for it in items if "class Foo" == it.signature)
    bar = next(it for it in items if "bar" in it.signature)
    baz = next(it for it in items if "baz" in it.signature)
    assert cls.start <= bar.start
    assert cls.start + cls.count >= baz.start + baz.count


def test_do_block_not_confused_with_method_end():
    # 'do...end' blocks inside a method must not prematurely close the method
    text = (
        "def process\n"
        "  items.each do |x|\n"
        "    puts x\n"
        "  end\n"
        "  :done\n"
        "end\n"
    )
    items = parse(text)
    assert len(items) == 1
    assert items[0].count == 6  # whole method, not just up to inner end


# ---------------------------------------------------------------------------
# Nesting and indentation in signatures
# ---------------------------------------------------------------------------

def test_module_method_indented():
    text = "module M\n  def helper\n    42\n  end\nend\n"
    items = parse(text)
    helper = next(it for it in items if "helper" in it.signature)
    assert helper.signature == "  def helper"


def test_class_method_indented():
    text = "class Foo\n  def bar\n    1\n  end\nend\n"
    items = parse(text)
    bar = next(it for it in items if "bar" in it.signature)
    assert bar.signature == "  def bar"


def test_nested_class_doubly_indented():
    text = "module M\n  class C\n    def f\n    end\n  end\nend\n"
    items = parse(text)
    f = next(it for it in items if "def f" in it.signature)
    assert f.signature == "    def f"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("# just a comment\n# another\n") == []


def test_constant_excluded():
    items = parse("module M\n  FOO = 42\nend\n")
    sigs = [it.signature for it in items]
    assert not any("FOO" in s for s in sigs)


def test_require_excluded():
    items = parse("require 'json'\nrequire_relative './x'\ndef foo\nend\n")
    sigs = [it.signature for it in items]
    assert not any("require" in s for s in sigs)


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 15


def test_fixture_module_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "module Animals" in sigs


def test_fixture_class_sigs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "  class Animal" in sigs
    assert "  class Dog < Animal" in sigs


def test_fixture_attr_sigs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "    attr_accessor :name, :kind" in sigs
    assert "    attr_reader :id" in sigs


def test_fixture_def_sigs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "    def initialize(name, kind: 'unknown')" in sigs
    assert "    def speak" in sigs
    assert "    def display_name" in sigs
    assert "    def self.create(name)" in sigs
    assert "    def secret_method" in sigs


def test_fixture_multiline_fetch_sig():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetch" in it.signature)
    assert fetch.signature == "    def fetch(item, distance: 1.0)"


def test_fixture_module_method_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "  def self.make_animal(name, kind = 'unknown')" in sigs


def test_fixture_standalone_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "def standalone_helper(x)" in sigs


def test_fixture_module_start_line():
    items = parse(FIXTURE.read_text())
    mod = next(it for it in items if it.signature == "module Animals")
    assert mod.start == 7  # comment at line 7, module at line 8


def test_fixture_module_range():
    items = parse(FIXTURE.read_text())
    mod = next(it for it in items if it.signature == "module Animals")
    assert mod.start == 7
    assert mod.count == 58  # lines 7-64 (comment through closing end)


def test_fixture_class_animal_range():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "  class Animal")
    assert animal.start == 11
    assert animal.count == 31  # lines 11-41 (comment through end)


def test_fixture_class_dog_range():
    items = parse(FIXTURE.read_text())
    dog = next(it for it in items if it.signature == "  class Dog < Animal")
    assert dog.start == 43
    assert dog.count == 17  # lines 43-59


def test_fixture_initialize_start_line():
    items = parse(FIXTURE.read_text())
    # The Animal.initialize has a comment at line 16
    init = next(
        it for it in items
        if "initialize(name, kind:" in it.signature
    )
    assert init.start == 16


def test_fixture_initialize_count():
    items = parse(FIXTURE.read_text())
    init = next(
        it for it in items
        if "initialize(name, kind:" in it.signature
    )
    assert init.count == 6  # comment + def + 3 body lines + end


def test_fixture_fetch_range():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetch" in it.signature)
    assert fetch.start == 53
    assert fetch.count == 6  # def fetch( through end


def test_fixture_standalone_helper_range():
    items = parse(FIXTURE.read_text())
    helper = next(it for it in items if "standalone_helper" in it.signature)
    assert helper.start == 66
    assert helper.count == 4  # comment + def + body + end


def test_fixture_module_covers_classes():
    items = parse(FIXTURE.read_text())
    mod = next(it for it in items if it.signature == "module Animals")
    animal = next(it for it in items if it.signature == "  class Animal")
    dog = next(it for it in items if "Dog" in it.signature)
    assert mod.start <= animal.start
    assert mod.start + mod.count >= animal.start + animal.count
    assert mod.start <= dog.start
    assert mod.start + mod.count >= dog.start + dog.count


def test_fixture_class_covers_methods():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "  class Animal")
    init = next(it for it in items if "initialize(name, kind:" in it.signature)
    assert animal.start < init.start
    assert animal.start + animal.count > init.start + init.count

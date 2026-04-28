"""Tests for the Scala outline parser."""

from pathlib import Path

from outliner.parsers.scala import parse, detect as detect_scala
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "scala"
FIXTURE = FIXTURES / "sample.scala"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_scala():
    assert guess_syntax("file.scala") == "scala"


def test_detect_content_case_class():
    assert detect_scala(["case class Foo(x: Int)", "object Bar {}"])


def test_detect_content_object_and_def():
    assert detect_scala(["object Foo {", "  def bar(): Int = 42", "}"])


def test_detect_content_no_match():
    assert not detect_scala(["Hello world", "No code here"])


def test_detect_content_java_not_triggered():
    # Java uses class/def differently; no 'object' declarations
    assert not detect_scala(["public class Foo {", "  void bar() {}"])


def test_detect_content_python_not_triggered():
    assert not detect_scala(["def foo():", "    pass"])


def test_detect_registry_scala_content():
    assert detect(FIXTURE.read_text()) == "scala"


# ---------------------------------------------------------------------------
# Simple def
# ---------------------------------------------------------------------------

def test_simple_def():
    items = parse("def foo(): Int = 42\n")
    assert any(it.signature.strip() == "def foo(): Int" for it in items)


def test_no_trailing_brace_in_sig():
    items = parse("object O {\n  def foo(): Int = {\n    42\n  }\n}\n")
    assert all(not it.signature.endswith("{") for it in items)


def test_abstract_def_no_equals():
    items = parse("trait T {\n  def foo(): String\n}\n")
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.signature.strip() == "def foo(): String"


def test_def_expression_body_stripped():
    items = parse("def greet(name: String): String = s\"Hello $name\"\n")
    greet = next(it for it in items if "greet" in it.signature)
    assert greet.signature == "def greet(name: String): String"


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_def_merged():
    src = (
        "object O {\n"
        "  def foo(\n"
        "      x: Int,\n"
        "      y: String,\n"
        "  ): Boolean = {\n"
        "    true\n"
        "  }\n"
        "}\n"
    )
    items = parse(src)
    foo = next(it for it in items if "foo" in it.signature)
    assert "x: Int" in foo.signature
    assert "y: String" in foo.signature
    assert not foo.signature.endswith("{")


def test_multiline_def_exact():
    src = (
        "object O {\n"
        "  def foo(\n"
        "      x: Int,\n"
        "      y: String,\n"
        "  ): Boolean = {\n"
        "    true\n"
        "  }\n"
        "}\n"
    )
    items = parse(src)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.signature == "  def foo(x: Int, y: String): Boolean"


def test_multiline_class_ctor():
    src = (
        "class Foo(\n"
        "    val x: Int,\n"
        "    val y: String,\n"
        ") extends Bar {\n"
        "  def baz(): Unit = {}\n"
        "}\n"
    )
    items = parse(src)
    foo = next(it for it in items if "Foo" in it.signature)
    assert foo.signature == "class Foo(val x: Int, val y: String) extends Bar"


# ---------------------------------------------------------------------------
# Class / trait / object declarations
# ---------------------------------------------------------------------------

def test_trait_declaration():
    items = parse("trait Animal {\n  def name: String\n}\n")
    assert any(it.signature == "trait Animal" for it in items)


def test_class_declaration():
    items = parse("class Dog(val name: String) extends Animal {\n  def speak() = \"Woof\"\n}\n")
    assert any(it.signature == "class Dog(val name: String) extends Animal" for it in items)


def test_case_class_declaration():
    items = parse("case class Cat(name: String, age: Int) extends Animal {\n  def speak() = \"Meow\"\n}\n")
    assert any(it.signature == "case class Cat(name: String, age: Int) extends Animal" for it in items)


def test_object_declaration():
    items = parse("object Foo {\n  def bar() = 1\n}\n")
    assert any(it.signature == "object Foo" for it in items)


def test_sealed_abstract_class():
    items = parse("sealed abstract class Shape\n")
    assert any(it.signature == "sealed abstract class Shape" for it in items)


def test_case_object():
    items = parse("case object None extends Option[Nothing]\n")
    assert any("None" in it.signature for it in items)


# ---------------------------------------------------------------------------
# Scala 3 features
# ---------------------------------------------------------------------------

def test_extension_declaration():
    src = "extension (s: String) {\n  def shout: String = s.toUpperCase + \"!\"\n}\n"
    items = parse(src)
    assert any(it.signature == "extension (s: String)" for it in items)


def test_given_with_equals():
    src = "given myOrd: Ordering[Int] = Ordering.Int\n"
    items = parse(src)
    assert any(it.signature == "given myOrd: Ordering[Int]" for it in items)


def test_given_anonymous():
    # Scala 3 anonymous given: type directly after 'given', no name
    src = "given Ordering[Int] = Ordering.Int\n"
    items = parse(src)
    assert any(it.signature == "given Ordering[Int]" for it in items)


def test_type_alias():
    src = "type AnimalMap = Map[String, Animal]\n"
    items = parse(src)
    assert any(it.signature == "type AnimalMap = Map[String, Animal]" for it in items)


def test_type_alias_with_type_bounds():
    # '<:' inside '[]' must not prematurely terminate collection
    src = "type Cmp[A <: Ordered[A]] = A\n"
    items = parse(src)
    assert any(it.signature == "type Cmp[A <: Ordered[A]] = A" for it in items)


def test_def_default_with_equals_in_string():
    # '=' inside a string default parameter is at paren depth > 0 and stays
    src = 'def foo(s: String = "x=y"): Int = 42\n'
    items = parse(src)
    assert any(it.signature == 'def foo(s: String = "x=y"): Int' for it in items)


# ---------------------------------------------------------------------------
# Comment / annotation walk-back
# ---------------------------------------------------------------------------

def test_doc_comment_walked_back():
    src = "/** Doc */\ntrait T {\n  def foo(): String\n}\n"
    items = parse(src)
    t = next(it for it in items if it.signature == "trait T")
    assert t.start == 1


def test_line_comment_walked_back():
    src = "// helper\ndef foo(): Int = 42\n"
    items = parse(src)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 1


def test_blank_stops_walkback():
    src = "/** Unrelated */\n\ntrait T {}\n"
    items = parse(src)
    t = next(it for it in items if "T" in it.signature)
    assert t.start == 3


def test_annotation_walked_back():
    src = "@deprecated\nclass Old {\n  def method(): Unit = {}\n}\n"
    items = parse(src)
    old = next(it for it in items if "Old" in it.signature)
    assert old.start == 1


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_class_range_covers_methods():
    src = (
        "class Foo {\n"
        "  def bar(): Int = 1\n"
        "  def baz(): Int = 2\n"
        "}\n"
    )
    items = parse(src)
    cls = next(it for it in items if it.signature == "class Foo")
    bar = next(it for it in items if "bar" in it.signature)
    baz = next(it for it in items if "baz" in it.signature)
    assert cls.start <= bar.start
    assert cls.start + cls.count >= baz.start + baz.count


def test_object_range_covers_methods():
    src = "object O {\n  def foo(): Int = 1\n}\n"
    items = parse(src)
    obj = next(it for it in items if it.signature == "object O")
    foo = next(it for it in items if "foo" in it.signature)
    assert obj.start < foo.start
    assert obj.start + obj.count >= foo.start + foo.count


def test_brace_body_range_correct():
    src = "def foo(): Int = {\n  1 + 1\n}\n"
    items = parse(src)
    assert items[0].count == 3


def test_abstract_def_range_is_minimal():
    src = "trait T {\n  def foo(): String\n}\n"
    items = parse(src)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.count == 1


def test_no_trailing_blank_in_range():
    src = "def foo(): Int = 1\n\ndef bar(): Int = 2\n"
    items = parse(src)
    foo = next(it for it in items if "foo" in it.signature)
    bar = next(it for it in items if "bar" in it.signature)
    assert foo.start + foo.count <= bar.start


# ---------------------------------------------------------------------------
# Exclusions
# ---------------------------------------------------------------------------

def test_import_excluded():
    items = parse("import scala.collection.mutable\n")
    assert items == []


def test_package_excluded():
    items = parse("package animals\n")
    assert items == []


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 21


def test_fixture_trait_sig():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "trait Animal" for it in items)


def test_fixture_class_sig():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "class Dog(val name: String, val breed: String) extends Animal" for it in items)


def test_fixture_case_class_sig():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "case class Cat(name: String, indoor: Boolean = true) extends Animal" for it in items)


def test_fixture_object_sig():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "object Cat" for it in items)


def test_fixture_sealed_abstract_class():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "sealed abstract class Shape" for it in items)


def test_fixture_extension_sig():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "extension (s: String)" for it in items)


def test_fixture_given_sig():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "given animalOrdering: Ordering[Cat]" for it in items)


def test_fixture_type_alias_sig():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "type AnimalMap = Map[String, Animal]" for it in items)


def test_fixture_imports_excluded():
    items = parse(FIXTURE.read_text())
    assert all("import" not in it.signature for it in items)


def test_fixture_package_excluded():
    items = parse(FIXTURE.read_text())
    assert all("package" not in it.signature for it in items)


def test_fixture_trait_start_and_count():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "trait Animal")
    assert animal.start == 6
    assert animal.count == 16


def test_fixture_class_dog_start_and_count():
    items = parse(FIXTURE.read_text())
    dog = next(it for it in items if "Dog" in it.signature)
    assert dog.start == 23
    assert dog.count == 17


def test_fixture_greet_multiline_sig():
    items = parse(FIXTURE.read_text())
    greet = next(it for it in items if "greet" in it.signature)
    assert greet.signature == "  def greet(message: String, times: Int = 1): String"


def test_fixture_greet_start_and_count():
    items = parse(FIXTURE.read_text())
    greet = next(it for it in items if "greet" in it.signature)
    assert greet.start == 14
    assert greet.count == 7


def test_fixture_fetch_sig():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetch" in it.signature)
    assert fetch.signature == "  def fetch(item: String, distance: Double = 1.0): Boolean"


def test_fixture_fetch_start_and_count():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetch" in it.signature)
    assert fetch.start == 31
    assert fetch.count == 8


def test_fixture_object_shapeutils_start_and_count():
    items = parse(FIXTURE.read_text())
    utils = next(it for it in items if it.signature == "object ShapeUtils")
    assert utils.start == 59
    assert utils.count == 7


def test_fixture_area_def_sig():
    items = parse(FIXTURE.read_text())
    area = next(it for it in items if "area" in it.signature)
    assert area.signature == "  def area(shape: Shape): Double"


def test_fixture_extension_start_and_count():
    items = parse(FIXTURE.read_text())
    ext = next(it for it in items if it.signature == "extension (s: String)")
    assert ext.start == 70
    assert ext.count == 5


def test_fixture_given_start_and_count():
    items = parse(FIXTURE.read_text())
    given = next(it for it in items if "animalOrdering" in it.signature)
    assert given.start == 76
    assert given.count == 2


def test_fixture_trait_contains_defs():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "trait Animal")
    name_def = next(it for it in items if it.signature == "  def name: String")
    assert animal.start < name_def.start
    assert animal.start + animal.count > name_def.start + name_def.count


def test_fixture_methods_indented():
    items = parse(FIXTURE.read_text())
    name_def = next(it for it in items if "name" in it.signature and "def" in it.signature)
    assert name_def.signature.startswith("  ")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("// just a comment\n/** another */\n") == []

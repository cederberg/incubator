"""Tests for the PHP outline parser."""

from pathlib import Path

from outliner.parsers.php import parse, detect as detect_php
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "php"
FIXTURE = FIXTURES / "sample.php"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_php():
    assert guess_syntax("file.php") == "php"


def test_detect_extension_phtml():
    assert guess_syntax("file.phtml") == "php"


def test_detect_content_open_tag():
    assert detect_php(["<?php", "", "namespace App;"])


def test_detect_content_open_tag_case_insensitive():
    assert detect_php(["<?PHP", "echo 'hi';"])


def test_detect_content_no_match():
    assert not detect_php(["Hello world", "No code here"])


def test_detect_content_python_not_triggered():
    assert not detect_php(["def foo():", "    pass"])


def test_detect_registry_php_content():
    assert detect(FIXTURE.read_text()) == "php"


# ---------------------------------------------------------------------------
# Inline unit tests — namespace
# ---------------------------------------------------------------------------

def test_namespace():
    items = parse("<?php\nnamespace App\\Models;\n")
    ns = next(it for it in items if "namespace" in it.signature)
    assert ns.signature == "namespace App\\Models"
    assert ns.start == 2
    assert ns.count == 1


def test_namespace_no_trailing_semicolon():
    items = parse("<?php\nnamespace Foo;\n")
    ns = items[0]
    assert not ns.signature.endswith(";")


# ---------------------------------------------------------------------------
# Inline unit tests — classes
# ---------------------------------------------------------------------------

def test_simple_class():
    items = parse("<?php\nclass Foo\n{\n}\n")
    assert len(items) == 1
    assert items[0].signature == "class Foo"
    assert items[0].start == 2


def test_no_trailing_brace():
    items = parse("<?php\nclass Foo\n{\n}\n")
    assert not items[0].signature.endswith("{")


def test_abstract_class():
    items = parse("<?php\nabstract class Animal\n{\n}\n")
    assert items[0].signature == "abstract class Animal"


def test_final_class():
    items = parse("<?php\nfinal class Singleton\n{\n}\n")
    assert items[0].signature == "final class Singleton"


def test_class_extends():
    items = parse("<?php\nclass Dog extends Animal\n{\n}\n")
    assert items[0].signature == "class Dog extends Animal"


def test_class_implements():
    items = parse("<?php\nclass Dog extends Animal implements Speakable\n{\n}\n")
    assert items[0].signature == "class Dog extends Animal implements Speakable"


def test_interface():
    items = parse("<?php\ninterface Runnable\n{\n    public function run(): void;\n}\n")
    sigs = [it.signature for it in items]
    assert "interface Runnable" in sigs


def test_trait():
    items = parse("<?php\ntrait HasId\n{\n}\n")
    assert items[0].signature == "trait HasId"


def test_enum():
    items = parse("<?php\nenum Status\n{\n    case Active;\n}\n")
    assert items[0].signature == "enum Status"


def test_backed_enum():
    items = parse("<?php\nenum Color: string\n{\n    case Red = 'red';\n}\n")
    assert items[0].signature == "enum Color: string"


# ---------------------------------------------------------------------------
# Inline unit tests — functions and methods
# ---------------------------------------------------------------------------

def test_simple_function():
    items = parse("<?php\nfunction greet(string $name): string\n{\n    return 'hi';\n}\n")
    assert len(items) == 1
    assert items[0].signature == "function greet(string $name): string"


def test_method():
    src = "<?php\nclass Foo\n{\n    public function bar(): void\n    {\n    }\n}\n"
    items = parse(src)
    sigs = [it.signature for it in items]
    assert "    public function bar(): void" in sigs


def test_static_method():
    src = "<?php\nclass Foo\n{\n    public static function create(): static\n    {\n    }\n}\n"
    items = parse(src)
    assert any("create" in it.signature for it in items)


def test_abstract_method_no_body():
    src = "<?php\nabstract class Foo\n{\n    abstract public function run(): void;\n}\n"
    items = parse(src)
    run = next(it for it in items if "run" in it.signature)
    assert run.signature == "    abstract public function run(): void"
    assert run.count == 1


def test_interface_method_no_body():
    src = "<?php\ninterface Runnable\n{\n    public function run(): void;\n}\n"
    items = parse(src)
    run = next(it for it in items if "run" in it.signature)
    assert run.count == 1


def test_no_trailing_brace_on_method():
    src = "<?php\nclass Foo\n{\n    public function bar(): void\n    {\n    }\n}\n"
    items = parse(src)
    bar = next(it for it in items if "bar" in it.signature)
    assert not bar.signature.endswith("{")


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_sig_merged():
    src = (
        "<?php\n"
        "function greet(\n"
        "    string $name,\n"
        "    int $times = 1\n"
        "): string {\n"
        "    return $name;\n"
        "}\n"
    )
    items = parse(src)
    assert len(items) == 1
    sig = items[0].signature
    assert sig.startswith("function greet(")
    assert "string $name" in sig
    assert "int $times = 1" in sig
    assert not sig.endswith("{")


def test_multiline_sig_exact():
    src = (
        "<?php\n"
        "function add(\n"
        "    int $a,\n"
        "    int $b\n"
        "): int {\n"
        "    return $a + $b;\n"
        "}\n"
    )
    items = parse(src)
    assert items[0].signature == "function add(int $a, int $b): int"


# ---------------------------------------------------------------------------
# Doc-comment walkback
# ---------------------------------------------------------------------------

def test_docblock_walked_back():
    src = "<?php\n/** Does something. */\nfunction foo(): void\n{\n}\n"
    items = parse(src)
    assert items[0].start == 2


def test_multiline_docblock_walked_back():
    src = (
        "<?php\n"
        "/**\n"
        " * Greets a user.\n"
        " */\n"
        "function greet(): void\n"
        "{\n"
        "}\n"
    )
    items = parse(src)
    assert items[0].start == 2


def test_blank_stops_walkback():
    src = (
        "<?php\n"
        "/** Unrelated. */\n"
        "\n"
        "function foo(): void\n"
        "{\n"
        "}\n"
    )
    items = parse(src)
    assert items[0].start == 4


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_class_range_covers_methods():
    src = (
        "<?php\n"
        "class Foo\n"
        "{\n"
        "    public function bar(): void\n"
        "    {\n"
        "    }\n"
        "    public function baz(): void\n"
        "    {\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    cls = next(it for it in items if it.signature == "class Foo")
    bar = next(it for it in items if "bar" in it.signature)
    baz = next(it for it in items if "baz" in it.signature)
    assert cls.start <= bar.start
    assert cls.start + cls.count >= baz.start + baz.count


def test_use_statement_excluded():
    src = "<?php\nuse Some\\Library;\nclass Foo\n{\n}\n"
    items = parse(src)
    assert all("use" not in it.signature for it in items)


def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("<?php\n// just a comment\n// another\n") == []


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 19


def test_fixture_namespace_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "namespace App\\Animals" in sigs


def test_fixture_abstract_class_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "abstract class Animal" in sigs


def test_fixture_interface_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "interface Speakable" in sigs


def test_fixture_trait_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "trait HasMetadata" in sigs


def test_fixture_enum_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "enum Status: string" in sigs


def test_fixture_constructor_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "    public function __construct(string $name, int $age)" in sigs


def test_fixture_multiline_from_array_sig():
    items = parse(FIXTURE.read_text())
    fa = next(it for it in items if "fromArray" in it.signature)
    assert fa.signature == (
        "    public static function fromArray(array $data, bool $validate = false): static"
    )


def test_fixture_abstract_method_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "    abstract public function speak(): string" in sigs


def test_fixture_interface_methods_no_body():
    items = parse(FIXTURE.read_text())
    speak = next(
        it for it in items
        if it.signature == "    public function speak(): string" and it.count == 1
    )
    shout = next(it for it in items if "shout" in it.signature)
    assert speak.count == 1
    assert shout.count == 1


def test_fixture_free_function_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "function make_animal(string $name, int $age = 0): Animal" in sigs


def test_fixture_abstract_class_start_line():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if "abstract class Animal" in it.signature)
    assert animal.start == 8


def test_fixture_abstract_class_range():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if "abstract class Animal" in it.signature)
    assert animal.start == 8
    assert animal.count == 45


def test_fixture_constructor_start_line():
    items = parse(FIXTURE.read_text())
    ctor = next(it for it in items if "__construct" in it.signature)
    assert ctor.start == 16


def test_fixture_from_array_start_line():
    items = parse(FIXTURE.read_text())
    fa = next(it for it in items if "fromArray" in it.signature)
    assert fa.start == 38


def test_fixture_free_function_start_line():
    items = parse(FIXTURE.read_text())
    fn = next(it for it in items if "make_animal" in it.signature)
    assert fn.start == 105


def test_fixture_class_contains_methods():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if "abstract class Animal" in it.signature)
    ctor = next(it for it in items if "__construct" in it.signature)
    assert animal.start < ctor.start
    assert animal.start + animal.count > ctor.start + ctor.count


def test_fixture_use_excluded():
    items = parse(FIXTURE.read_text())
    assert all("use" not in it.signature for it in items)


def test_fixture_enum_range():
    items = parse(FIXTURE.read_text())
    status = next(it for it in items if "enum Status" in it.signature)
    assert status.start == 89
    assert status.count == 15


def test_fixture_enum_contains_method():
    items = parse(FIXTURE.read_text())
    status = next(it for it in items if "enum Status" in it.signature)
    label = next(it for it in items if "label" in it.signature)
    assert status.start < label.start
    assert status.start + status.count >= label.start + label.count

"""Tests for the Python outline parser."""

from pathlib import Path

from outliner.parsers.python import parse, detect as detect_python
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "py"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_py():
    assert guess_syntax("file.py") == "python"


def test_detect_extension_pyw():
    assert guess_syntax("file.pyw") == "python"


def test_detect_content_shebang():
    assert detect_python(["#!/usr/bin/env python3", "x = 1"])
    assert detect_python(["#!/usr/bin/env python", "def foo(): pass"])


def test_detect_content_colon_syntax():
    # Python uses ':' to end def/class; Java/C/JS use '{'
    assert detect_python(["def foo():", "    pass"])
    assert detect_python(["class Foo:", "    pass"])
    assert detect_python(["async def bar():", "    pass"])


def test_detect_content_java_not_triggered():
    # Java class declarations end with '{', not ':'
    assert not detect_python(["public class Foo {", "    void bar() {}"])


def test_detect_content_no_match():
    assert not detect_python(["Hello world", "No code here"])


def test_detect_registry_python_content():
    assert detect((FIXTURES / "sample.py").read_text()) == "python"


# ---------------------------------------------------------------------------
# Simple functions
# ---------------------------------------------------------------------------

def test_simple_function():
    items = parse("def foo():\n    pass\n")
    assert len(items) == 1
    assert items[0].signature == "def foo()"
    assert items[0].start == 1
    assert items[0].count == 2


def test_function_with_args_and_return():
    items = parse("def foo(x: int, y: str = 'hi') -> bool:\n    return True\n")
    assert items[0].signature == "def foo(x: int, y: str = 'hi') -> bool"


def test_trailing_colon_stripped():
    items = parse("def foo():\n    pass\n")
    assert not items[0].signature.endswith(":")


def test_async_function():
    items = parse("async def fetch(url: str) -> dict:\n    pass\n")
    assert items[0].signature == "async def fetch(url: str) -> dict"


def test_private_function():
    items = parse("def _helper(x: int) -> int:\n    return x * 2\n")
    assert items[0].signature == "def _helper(x: int) -> int"


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_signature_merged():
    text = "def foo(\n    x: int,\n    y: str,\n) -> bool:\n    return True\n"
    items = parse(text)
    assert len(items) == 1
    sig = items[0].signature
    assert sig.startswith("def foo(")
    assert "x: int" in sig
    assert "y: str" in sig
    assert not sig.endswith(":")


def test_multiline_signature_exact():
    # Bracket spacing is cleaned up: '( arg' → '(arg', 'arg )' → 'arg)'
    text = (
        "def greet(\n"
        "    name: str,\n"
        "    greeting: str = 'Hello',\n"
        ") -> str:\n"
        "    return f'{greeting}, {name}'\n"
    )
    items = parse(text)
    assert items[0].signature == "def greet(name: str, greeting: str = 'Hello') -> str"


def test_fixture_complex_factory_sig():
    items = parse((FIXTURES / "sample.py").read_text())
    factory = next(it for it in items if "complex_factory" in it.signature)
    assert factory.signature == 'def complex_factory(name: str, size: int = 0, verbose: bool = False) -> "Animal"'


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

def test_simple_class():
    items = parse("class Foo:\n    pass\n")
    assert items[0].signature == "class Foo"
    assert not items[0].signature.endswith(":")


def test_class_with_base():
    items = parse("class Dog(Animal):\n    pass\n")
    assert items[0].signature == "class Dog(Animal)"


def test_class_methods_included():
    text = "class Foo:\n    def bar(self):\n        pass\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "class Foo" in sigs
    assert "def bar(self)" in sigs


# ---------------------------------------------------------------------------
# Comment / decorator walkback
# ---------------------------------------------------------------------------

def test_comment_walked_back():
    text = "# A comment\ndef foo():\n    pass\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 3


def test_decorator_walked_back():
    text = "@property\ndef foo(self):\n    return 1\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 3


def test_comment_and_decorator_walked_back():
    text = "# doc\n@staticmethod\ndef foo():\n    pass\n"
    items = parse(text)
    assert items[0].start == 1


def test_multiple_decorators():
    text = "@app.route('/')\n@login_required\ndef index():\n    pass\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 4


def test_no_walkback_past_code():
    text = "x = 1\ndef foo():\n    pass\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 2


def test_blank_line_between_comment_and_def():
    text = "# unrelated\n\ndef foo():\n    pass\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 3


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_function_range_covers_body():
    text = "def foo():\n    x = 1\n    y = 2\n    return x + y\n"
    items = parse(text)
    assert items[0].count == 4


def test_nested_function_appears():
    text = "def outer():\n    def inner():\n        pass\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "def outer()" in sigs
    assert "def inner()" in sigs


def test_outer_range_covers_inner():
    text = "def outer():\n    def inner():\n        pass\n"
    items = parse(text)
    outer = next(it for it in items if it.signature == "def outer()")
    inner = next(it for it in items if it.signature == "def inner()")
    assert outer.start <= inner.start
    assert outer.start + outer.count >= inner.start + inner.count


def test_class_range_covers_methods():
    text = (
        "class Foo:\n"
        "    def bar(self):\n"
        "        pass\n"
        "\n"
        "    def baz(self):\n"
        "        pass\n"
    )
    items = parse(text)
    cls = next(it for it in items if it.signature == "class Foo")
    bar = next(it for it in items if "bar" in it.signature)
    baz = next(it for it in items if "baz" in it.signature)
    assert cls.start <= bar.start
    assert cls.start + cls.count >= baz.start + baz.count


def test_trailing_blank_not_in_range():
    text = "def foo():\n    pass\n\ndef bar():\n    pass\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    bar = next(it for it in items if "bar" in it.signature)
    assert foo.start + foo.count <= bar.start


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

def test_fixture_class_signatures():
    items = parse((FIXTURES / "sample.py").read_text())
    sigs = [it.signature for it in items]
    assert "class Animal" in sigs
    assert "class Dog(Animal)" in sigs


def test_fixture_function_signatures():
    items = parse((FIXTURES / "sample.py").read_text())
    sigs = [it.signature for it in items]
    assert any("make_animal" in s for s in sigs)
    assert any("fetch_animal" in s for s in sigs)
    assert any("_helper" in s for s in sigs)


def test_fixture_method_signatures():
    items = parse((FIXTURES / "sample.py").read_text())
    sigs = [it.signature for it in items]
    assert any("__init__" in s for s in sigs)
    assert any("speak" in s for s in sigs)
    assert any("display_name" in s for s in sigs)
    assert any("species" in s for s in sigs)
    assert any("from_dict" in s for s in sigs)


def test_fixture_class_range_contains_methods():
    items = parse((FIXTURES / "sample.py").read_text())
    animal = next(it for it in items if it.signature == "class Animal")
    init = next(it for it in items if "__init__" in it.signature)
    assert animal.start < init.start
    assert animal.start + animal.count > init.start + init.count


def test_fixture_multiline_fetch_sig():
    items = parse((FIXTURES / "sample.py").read_text())
    # Dog.fetch has a multi-line signature
    fetch = next(
        it for it in items
        if it.signature.startswith("def fetch(") and "item" in it.signature
    )
    assert fetch.signature == "def fetch(self, item: str, distance: float = 1.0) -> bool"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("# just a comment\n# another\n") == []

"""Tests for the C# outline parser."""

from pathlib import Path

from outliner.parsers.csharp import parse, detect as detect_csharp
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "cs"
FIXTURE = FIXTURES / "sample.cs"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_cs():
    assert guess_syntax("file.cs") == "csharp"


def test_detect_content_namespace_class():
    assert detect_csharp(["using System;", "", "namespace Foo", "{", "    public class Bar {", "    }"])


def test_detect_content_using_interface():
    assert detect_csharp(["using System.Collections.Generic;", "public interface IFoo {", "}"])


def test_detect_content_no_match():
    assert not detect_csharp(["Hello world", "No code here"])


def test_detect_content_class_alone_not_enough():
    # class without using/namespace is ambiguous — should not trigger
    assert not detect_csharp(["class Foo {", "    void bar() {}", "}"])


def test_detect_registry_csharp_content():
    assert detect(FIXTURE.read_text()) == "csharp"


# ---------------------------------------------------------------------------
# Namespace
# ---------------------------------------------------------------------------

def test_namespace_detected():
    items = parse("namespace Foo\n{\n    public class Bar {}\n}\n")
    sigs = [it.signature for it in items]
    assert any("namespace Foo" in s for s in sigs)


def test_namespace_range_covers_class():
    items = parse("namespace Foo\n{\n    public class Bar\n    {\n    }\n}\n")
    ns = next(it for it in items if "namespace" in it.signature)
    cls = next(it for it in items if "class Bar" in it.signature)
    assert ns.start <= cls.start
    assert ns.start + ns.count >= cls.start + cls.count


# ---------------------------------------------------------------------------
# Type declarations
# ---------------------------------------------------------------------------

def test_simple_class():
    items = parse("public class Foo\n{\n}\n")
    assert any("class Foo" in it.signature for it in items)


def test_no_trailing_brace_in_sig():
    items = parse("public class Foo\n{\n}\n")
    cls = next(it for it in items if "class Foo" in it.signature)
    assert not cls.signature.endswith("{")


def test_interface():
    items = parse("public interface IBar\n{\n}\n")
    assert any("interface IBar" in it.signature for it in items)


def test_struct():
    items = parse("public struct Point\n{\n    public int X;\n}\n")
    assert any("struct Point" in it.signature for it in items)


def test_enum():
    items = parse("public enum Status\n{\n    Active,\n    Inactive\n}\n")
    assert any("enum Status" in it.signature for it in items)


def test_record():
    items = parse("public record Metadata(string Source);\n")
    assert any("record Metadata" in it.signature for it in items)


def test_generic_class():
    items = parse("public class Container<T> where T : class\n{\n}\n")
    assert any("Container<T>" in it.signature for it in items)


# ---------------------------------------------------------------------------
# Methods
# ---------------------------------------------------------------------------

def test_simple_method():
    code = "public class Foo\n{\n    public void Bar()\n    {\n    }\n}\n"
    items = parse(code)
    assert any("void Bar()" in it.signature for it in items)


def test_method_no_trailing_brace():
    code = "public class Foo\n{\n    public void Bar()\n    {\n    }\n}\n"
    items = parse(code)
    bar = next(it for it in items if "Bar" in it.signature)
    assert not bar.signature.endswith("{")


def test_constructor():
    code = "public class Animal\n{\n    public Animal(string name)\n    {\n    }\n}\n"
    items = parse(code)
    assert any("Animal(string name)" in it.signature for it in items)


def test_method_with_return_type():
    code = "public class Foo\n{\n    public string GetName() => _name;\n}\n"
    items = parse(code)
    assert any("GetName()" in it.signature for it in items)


def test_multiline_method_sig():
    code = (
        "public class Foo\n{\n"
        "    public async Task<string> FetchDataAsync(\n"
        "        string endpoint,\n"
        "        bool useCache = true)\n"
        "    {\n"
        "        return endpoint;\n"
        "    }\n"
        "}\n"
    )
    items = parse(code)
    fetch = next(it for it in items if "FetchDataAsync" in it.signature)
    assert "endpoint" in fetch.signature
    assert "useCache" in fetch.signature


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def test_property_detected():
    code = "public class Foo\n{\n    public string Name { get; set; }\n}\n"
    items = parse(code)
    assert any("Name" in it.signature for it in items)


def test_property_full_body():
    code = (
        "public class Foo\n{\n"
        "    public string Name\n"
        "    {\n"
        "        get => _name;\n"
        "        set => _name = value;\n"
        "    }\n"
        "}\n"
    )
    items = parse(code)
    assert any("Name" in it.signature for it in items)


# ---------------------------------------------------------------------------
# Attributes (walk-back)
# ---------------------------------------------------------------------------

def test_attribute_walked_back():
    code = "[Serializable]\npublic class Foo\n{\n}\n"
    items = parse(code)
    cls = next(it for it in items if "class Foo" in it.signature)
    assert cls.start == 1


def test_doc_comment_walked_back():
    code = "/// <summary>A class.</summary>\npublic class Foo\n{\n}\n"
    items = parse(code)
    cls = next(it for it in items if "class Foo" in it.signature)
    assert cls.start == 1


def test_multiline_doc_comment_walked_back():
    code = (
        "/// <summary>\n"
        "/// Multiline doc.\n"
        "/// </summary>\n"
        "public class Foo\n{\n}\n"
    )
    items = parse(code)
    cls = next(it for it in items if "class Foo" in it.signature)
    assert cls.start == 1
    assert cls.count == 6


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_detects_csharp():
    assert detect_csharp(FIXTURE.read_text().splitlines()[:50])


def test_fixture_namespace():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("namespace Animals" in s for s in sigs)


def test_fixture_class_signatures():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("class Animal" in s for s in sigs)
    assert any("class Container" in s for s in sigs)
    assert any("class AnimalTagAttribute" in s for s in sigs)


def test_fixture_interface():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("interface ISpeakable" in s for s in sigs)


def test_fixture_enum():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("enum Status" in s for s in sigs)


def test_fixture_struct():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("struct Point" in s for s in sigs)


def test_fixture_record():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("record Metadata" in s for s in sigs)


def test_fixture_methods():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("Speak()" in s for s in sigs)
    assert any("FetchDataAsync" in s for s in sigs)
    assert any("FromParts" in s for s in sigs)
    assert any("ToString()" in s for s in sigs)


def test_fixture_properties():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("Name" in s and "get" not in s for s in sigs)
    assert any("Age" in s for s in sigs)


def test_fixture_multiline_method_merged():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "FetchDataAsync" in it.signature)
    assert "endpoint" in fetch.signature
    assert "useCache" in fetch.signature


def test_fixture_multiline_static_method_merged():
    items = parse(FIXTURE.read_text())
    fp = next(it for it in items if "FromParts" in it.signature)
    assert "name" in fp.signature
    assert "validate" in fp.signature


def test_fixture_class_range_covers_methods():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature.strip().startswith("public class Animal"))
    # Use methods that are definitely inside Animal (not ISpeakable)
    methods = [it for it in items if "virtual" in it.signature and "Speak" in it.signature
               or "FetchDataAsync" in it.signature]
    assert methods, "Expected at least one Animal method"
    for m in methods:
        assert animal.start <= m.start
        assert animal.start + animal.count >= m.start + m.count


def test_fixture_attribute_walkback():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature.strip().startswith("public class Animal"))
    # [Serializable] is at line 10, /// summary starts at line 8
    assert animal.start <= 8


def test_fixture_namespace_range_covers_classes():
    items = parse(FIXTURE.read_text())
    ns = next(it for it in items if "namespace Animals" in it.signature and "Utilities" not in it.signature)
    animal = next(it for it in items if "class Animal" in it.signature)
    assert ns.start <= animal.start
    assert ns.start + ns.count >= animal.start + animal.count


# ---------------------------------------------------------------------------
# Explicit interface implementations
# ---------------------------------------------------------------------------

def test_explicit_interface_impl():
    code = (
        "public class Foo : IDisposable\n{\n"
        "    void IDisposable.Dispose()\n    {\n    }\n"
        "}\n"
    )
    items = parse(code)
    assert any("Dispose" in it.signature for it in items)


def test_explicit_interface_impl_with_return():
    code = (
        "public class Foo : IFormattable\n{\n"
        "    string IFormattable.ToString(string fmt, IFormatProvider fp)\n"
        "    {\n        return fmt;\n    }\n"
        "}\n"
    )
    items = parse(code)
    assert any("ToString" in it.signature for it in items)


# ---------------------------------------------------------------------------
# event / delegate
# ---------------------------------------------------------------------------

def test_event_excluded():
    code = "public class Foo\n{\n    public event EventHandler DataReceived;\n}\n"
    items = parse(code)
    assert not any("DataReceived" in it.signature for it in items)


def test_delegate_detected():
    code = "public delegate string Transformer(string input);\n"
    items = parse(code)
    assert any("Transformer" in it.signature for it in items)


# ---------------------------------------------------------------------------
# global using / file-scoped namespace
# ---------------------------------------------------------------------------

def test_global_using_excluded():
    items = parse("global using System.IO;\npublic class Foo {}\n")
    assert not any("using" in it.signature for it in items)


def test_file_scoped_namespace_no_semicolon():
    items = parse("namespace Foo.Bar;\npublic class Baz\n{\n}\n")
    ns = next(it for it in items if "namespace" in it.signature)
    assert not ns.signature.endswith(";")
    assert ns.signature == "namespace Foo.Bar"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_using():
    items = parse("using System;\nusing System.IO;\n")
    assert items == []

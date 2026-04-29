"""Tests for the Java outline parser."""

from pathlib import Path

from outliner.parsers.java import parse as _parse, detect as detect_java

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "java"
FIXTURE = FIXTURES / "sample.java"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_java():
    assert guess_syntax("file.java") == "java"


def test_detect_content_package_class():
    assert detect_java(["package com.example;", "", "public class Foo {", "}"])


def test_detect_content_import_interface():
    assert detect_java(["import java.util.List;", "public interface Bar {", "}"])


def test_detect_content_no_match():
    assert not detect_java(["Hello world", "No code here"])


def test_detect_content_class_alone_not_enough():
    # class keyword alone is not sufficient — could be Groovy/Kotlin/etc.
    assert not detect_java(["class Foo {", "    void bar() {}", "}"])


def test_detect_registry_java_content():
    assert detect(FIXTURE.read_text()) == "java"


# ---------------------------------------------------------------------------
# Inline unit tests
# ---------------------------------------------------------------------------

def test_simple_class():
    items = parse("public class Foo {\n}\n")
    assert len(items) == 1
    assert items[0].signature == "public class Foo"
    assert items[0].start == 1
    assert items[0].count == 2


def test_no_trailing_brace():
    items = parse("public class Foo {\n}\n")
    assert not items[0].signature.endswith("{")


def test_interface():
    items = parse("public interface Bar {\n}\n")
    assert items[0].signature == "public interface Bar"


def test_enum():
    items = parse("public enum Color {\n    RED, GREEN, BLUE;\n}\n")
    assert items[0].signature == "public enum Color"


def test_record_type():
    items = parse("public record Point(int x, int y) {\n}\n")
    assert len(items) == 1
    assert items[0].signature == "public record Point(int x, int y)"


def test_annotation_type():
    items = parse("public @interface MyTag {\n}\n")
    assert items[0].signature == "public @interface MyTag"


def test_simple_method():
    src = "public class Foo {\n    public void bar() {\n    }\n}\n"
    items = parse(src)
    sigs = [it.signature for it in items]
    assert "    public void bar()" in sigs


def test_method_no_trailing_brace():
    src = "public class Foo {\n    public void bar() {\n    }\n}\n"
    items = parse(src)
    bar = next(it for it in items if "bar" in it.signature)
    assert not bar.signature.endswith("{")


def test_constructor():
    src = "public class Foo {\n    public Foo(int x) {\n    }\n}\n"
    items = parse(src)
    sigs = [it.signature for it in items]
    assert "    public Foo(int x)" in sigs


def test_interface_method_no_body():
    src = "public interface Runnable {\n    void run();\n}\n"
    items = parse(src)
    sigs = [it.signature for it in items]
    assert "    void run()" in sigs


def test_throws_clause_in_sig():
    src = "public class Foo {\n    public void bar() throws IOException {\n    }\n}\n"
    items = parse(src)
    bar = next(it for it in items if "bar" in it.signature)
    assert "throws IOException" in bar.signature


def test_synchronized_block_not_detected():
    src = (
        "public class Foo {\n"
        "    public void bar() {\n"
        "        synchronized (this) {\n"
        "            doWork();\n"
        "        }\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    sigs = [it.signature for it in items]
    assert not any("synchronized" in s for s in sigs)


def test_nested_generic_return_type():
    src = (
        "import java.util.Map;\n"
        "public class Foo {\n"
        "    public Map<String, List<Integer>> getMap() {\n"
        "        return null;\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    assert any("getMap" in it.signature for it in items)


def test_generic_method_type_params():
    src = (
        "public class Foo {\n"
        "    public <T extends Comparable<T>> T max(T a, T b) {\n"
        "        return a.compareTo(b) >= 0 ? a : b;\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    assert any("max" in it.signature for it in items)


def test_multiline_sig_merged():
    src = (
        "public class Foo {\n"
        "    public String greet(\n"
        "            String name,\n"
        "            int times) {\n"
        "        return name;\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    greet = next(it for it in items if "greet" in it.signature)
    assert greet.signature == "    public String greet(String name, int times)"


def test_javadoc_walked_back():
    src = (
        "public class Foo {\n"
        "    /** Does something. */\n"
        "    public void bar() {\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    bar = next(it for it in items if "bar" in it.signature)
    assert bar.start == 2


def test_annotation_walked_back():
    src = (
        "public class Foo {\n"
        "    @Override\n"
        "    public String toString() {\n"
        "        return \"\";\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    ts = next(it for it in items if "toString" in it.signature)
    assert ts.start == 2


def test_blank_stops_walkback():
    src = (
        "public class Foo {\n"
        "    /** Unrelated. */\n"
        "\n"
        "    public void bar() {\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    bar = next(it for it in items if "bar" in it.signature)
    assert bar.start == 4


def test_import_excluded():
    src = "import java.util.List;\npublic class Foo {\n}\n"
    items = parse(src)
    assert all("import" not in it.signature for it in items)


def test_class_range_covers_methods():
    src = (
        "public class Foo {\n"
        "    public void bar() {\n"
        "    }\n"
        "    public void baz() {\n"
        "    }\n"
        "}\n"
    )
    items = parse(src)
    cls = next(it for it in items if it.signature == "public class Foo")
    bar = next(it for it in items if "bar" in it.signature)
    baz = next(it for it in items if "baz" in it.signature)
    assert cls.start <= bar.start
    assert cls.start + cls.count >= baz.start + baz.count


def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("// just a comment\n// another\n") == []


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 22


def test_fixture_class_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "public class Animal" in sigs


def test_fixture_interface_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "public interface Speakable" in sigs


def test_fixture_enum_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "public enum Status" in sigs


def test_fixture_annotation_type_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "public @interface AnimalTag" in sigs


def test_fixture_nested_class_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "    public static class Metadata" in sigs


def test_fixture_constructor_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "    public Animal(String name, int age)" in sigs


def test_fixture_multiline_from_parts_sig():
    items = parse(FIXTURE.read_text())
    fp = next(it for it in items if "fromParts" in it.signature)
    assert fp.signature == (
        "    public static Optional<Animal> fromParts("
        "String name, int age, boolean validate)"
    )


def test_fixture_interface_method_no_body():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "    String speak()" in sigs


def test_fixture_annotation_element_sigs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert '    String value() default ""' in sigs
    assert "    int priority() default 0" in sigs


def test_fixture_class_start_line():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "public class Animal")
    # javadoc starts at line 6
    assert animal.start == 6


def test_fixture_constructor_start_line():
    items = parse(FIXTURE.read_text())
    ctor = next(it for it in items if "Animal(String" in it.signature)
    # javadoc starts at line 15
    assert ctor.start == 15


def test_fixture_from_parts_start_line():
    items = parse(FIXTURE.read_text())
    fp = next(it for it in items if "fromParts" in it.signature)
    # javadoc starts at line 53
    assert fp.start == 53


def test_fixture_class_range():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "public class Animal")
    assert animal.start == 6
    assert animal.count == 86  # lines 6-91 (body includes groupByTag + synchronized)


def test_fixture_class_contains_constructor():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "public class Animal")
    ctor = next(it for it in items if "Animal(String" in it.signature)
    assert animal.start < ctor.start
    assert animal.start + animal.count > ctor.start + ctor.count


def test_fixture_imports_excluded():
    items = parse(FIXTURE.read_text())
    assert all("import" not in it.signature for it in items)


def test_fixture_enum_constants_excluded():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert not any("ACTIVE" in s or "INACTIVE" in s or "ARCHIVED" in s for s in sigs)


def test_fixture_throws_in_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("throws IOException" in s for s in sigs)


def test_fixture_synchronized_not_in_items():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert not any("synchronized" in s for s in sigs)


def test_fixture_record_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "public record Point(double x, double y)" in sigs


def test_fixture_record_method():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "    public double distance()" in sigs


def test_fixture_complex_generic_sig():
    items = parse(FIXTURE.read_text())
    gbt = next(it for it in items if "groupByTag" in it.signature)
    assert gbt.signature == (
        "    public static Map<String, List<Animal>> groupByTag("
        "Map<String, List<Animal>> source, boolean deepCopy)"
    )

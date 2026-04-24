"""Tests for the Go outline parser."""

from pathlib import Path

from outliner.parsers.go import parse, detect as detect_go
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "go"
FIXTURE = FIXTURES / "sample.go"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_go():
    assert guess_syntax("file.go") == "go"


def test_detect_content_package_func():
    assert detect_go(["package main", "", "func main() {", "}"])


def test_detect_content_no_match():
    assert not detect_go(["Hello world", "No code here"])


def test_detect_content_no_package():
    assert not detect_go(["func foo() {", "}"])


def test_detect_registry_go_content():
    assert detect(FIXTURE.read_text()) == "go"


# ---------------------------------------------------------------------------
# Simple functions
# ---------------------------------------------------------------------------

def test_simple_function():
    items = parse("func foo(x int) bool {\n\treturn true\n}\n")
    assert len(items) == 1
    assert items[0].signature == "func foo(x int) bool"
    assert items[0].start == 1
    assert items[0].count == 3


def test_no_trailing_brace():
    items = parse("func foo() {\n\treturn\n}\n")
    assert not items[0].signature.endswith("{")


def test_function_no_args():
    items = parse("func Noop() {\n}\n")
    assert items[0].signature == "func Noop()"


def test_function_multiple_returns():
    items = parse("func split(s string) (string, error) {\n\treturn s, nil\n}\n")
    assert items[0].signature == "func split(s string) (string, error)"


# ---------------------------------------------------------------------------
# Methods
# ---------------------------------------------------------------------------

def test_method_with_pointer_receiver():
    items = parse("func (d *Driver) Name() string {\n\treturn d.name\n}\n")
    assert items[0].signature == "func (d *Driver) Name() string"


def test_method_with_value_receiver():
    items = parse("func (c Config) Addr() string {\n\treturn c.Host\n}\n")
    assert items[0].signature == "func (c Config) Addr() string"


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_sig_merged():
    text = (
        "func Foo(\n"
        "\tx int,\n"
        "\ty string,\n"
        ") error {\n"
        "\treturn nil\n"
        "}\n"
    )
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "func Foo(x int, y string) error"


def test_multiline_sig_with_receiver():
    text = (
        "func (d *Driver) Fetch(\n"
        "\tctx context.Context,\n"
        "\tkey string,\n"
        ") (string, error) {\n"
        "\treturn \"\", nil\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].signature == "func (d *Driver) Fetch(ctx context.Context, key string) (string, error)"


# ---------------------------------------------------------------------------
# Type declarations
# ---------------------------------------------------------------------------

def test_type_struct():
    text = "type Config struct {\n\tHost string\n}\n"
    items = parse(text)
    assert items[0].signature == "type Config struct"
    assert not items[0].signature.endswith("{")


def test_type_interface():
    text = "type Stringer interface {\n\tString() string\n}\n"
    items = parse(text)
    assert items[0].signature == "type Stringer interface"


def test_type_definition():
    items = parse("type ErrCode int\n")
    assert items[0].signature == "type ErrCode int"
    assert items[0].start == 1
    assert items[0].count == 1


def test_type_func():
    items = parse("type Handler func()\n")
    assert items[0].signature == "type Handler func()"


def test_type_alias():
    items = parse("type MyInt = int\n")
    assert items[0].signature == "type MyInt = int"


# ---------------------------------------------------------------------------
# Doc-comment walkback
# ---------------------------------------------------------------------------

def test_doc_comment_walked_back():
    text = "// Foo does something.\nfunc Foo() {\n}\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 3


def test_multiple_doc_comments_walked_back():
    text = "// Foo does something.\n// It is great.\nfunc Foo() {\n}\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 4


def test_blank_stops_walkback():
    text = "// unrelated\n\nfunc Foo() {\n}\n"
    items = parse(text)
    assert items[0].start == 3


def test_doc_comment_on_type():
    text = "// Config is config.\ntype Config struct {\n\tX int\n}\n"
    items = parse(text)
    assert items[0].start == 1


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_func_range_covers_body():
    text = "func foo() {\n\tx := 1\n\ty := 2\n\treturn x + y\n}\n"
    items = parse(text)
    assert items[0].count == 5


def test_type_struct_range_covers_body():
    text = "type Config struct {\n\tHost string\n\tPort int\n}\n"
    items = parse(text)
    assert items[0].count == 4


def test_type_interface_range_covers_body():
    text = "type Doer interface {\n\tDo() error\n\tUndo() error\n}\n"
    items = parse(text)
    assert items[0].count == 4


def test_consecutive_funcs_no_overlap():
    text = "func foo() {\n}\n\nfunc bar() {\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    bar = next(it for it in items if "bar" in it.signature)
    assert foo.start + foo.count <= bar.start


def test_import_excluded():
    text = 'import (\n\t"fmt"\n)\nfunc foo() {\n}\n'
    items = parse(text)
    assert all("import" not in it.signature for it in items)


def test_package_excluded():
    text = "package main\n\nfunc foo() {\n}\n"
    items = parse(text)
    assert all("package" not in it.signature for it in items)


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_functions():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("New" in s for s in sigs)
    assert any("StartLogging" in s for s in sigs)
    assert any("Fetch" in s for s in sigs)
    assert any("String" in s for s in sigs)
    assert any("helper" in s for s in sigs)


def test_fixture_types():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "type Config struct" in sigs
    assert "type Driver struct" in sigs
    assert "type Stringer interface" in sigs
    assert "type ErrCode int" in sigs
    assert "type fetchOption func()" in sigs


def test_fixture_multiline_fetch_sig():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "Fetch" in it.signature)
    assert fetch.signature == (
        "func (d *Driver) Fetch("
        "ctx context.Context, key string, opts ...fetchOption"
        ") (string, error)"
    )


def test_fixture_var_const_excluded():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert not any(s.startswith("const") or s.startswith("var") for s in sigs)


def test_fixture_doc_comments_in_range():
    items = parse(FIXTURE.read_text())
    new_fn = next(it for it in items if it.signature == "func New(cfg *Config) *Driver")
    # doc comment "// New creates..." is line before func
    assert new_fn.start == 43  # doc comment is line 43, func is line 44


def test_fixture_new_range():
    items = parse(FIXTURE.read_text())
    new_fn = next(it for it in items if it.signature == "func New(cfg *Config) *Driver")
    assert new_fn.count == 4  # doc + func line + body + closing }


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("// just a comment\n// another\n") == []


def test_package_only():
    assert parse("package main\n") == []

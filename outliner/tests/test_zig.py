"""Tests for the Zig outline parser."""

from pathlib import Path

from outliner.parsers.zig import parse as _parse, detect as detect_zig

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "zig"
FIXTURE = FIXTURES / "sample.zig"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_zig():
    assert guess_syntax("file.zig") == "zig"


def test_detect_content_import_and_fn():
    assert detect_zig(['const std = @import("std");', "", "pub fn main() void {}"])


def test_detect_content_no_import_no_fn():
    assert not detect_zig(["Hello world", "No code here"])


def test_detect_content_import_without_fn():
    assert not detect_zig(['const std = @import("std");', "const x = 1;"])


def test_detect_content_fn_without_zig_marker():
    # Go/Rust/C also have fn — require @import() as co-occurring Zig marker
    assert not detect_zig(["fn foo(x: u32) u32 {", "    return x;", "}"])


def test_detect_registry_zig_content():
    assert detect(FIXTURE.read_text()) == "zig"


# ---------------------------------------------------------------------------
# Simple fn declarations
# ---------------------------------------------------------------------------

def test_simple_fn():
    items = parse("const std = @import(\"std\");\nfn foo() void {}\n")
    assert any(it.signature == "fn foo() void" for it in items)


def test_pub_fn():
    items = parse("const std = @import(\"std\");\npub fn bar() u32 { return 0; }\n")
    assert any(it.signature == "pub fn bar() u32" for it in items)


def test_no_trailing_brace():
    items = parse("fn foo() void {}\n")
    assert all(not it.signature.endswith("{") for it in items)


def test_error_union_return():
    items = parse("fn foo() !void {}\n")
    assert any(it.signature == "fn foo() !void" for it in items)


def test_pointer_return_type():
    items = parse("fn foo() []const u8 { return \"hi\"; }\n")
    assert any(it.signature == "fn foo() []const u8" for it in items)


def test_error_set_return_type():
    # error{...} in return type must not be stripped as the body opener
    src = "fn foo(x: u32) error{OOM}!u32 {\n    return x;\n}\n"
    items = parse(src)
    assert len(items) == 1
    assert items[0].signature == "fn foo(x: u32) error{OOM}!u32"


# ---------------------------------------------------------------------------
# Struct / enum / union declarations
# ---------------------------------------------------------------------------

def test_struct_declaration():
    items = parse("const Foo = struct {};\n")
    assert any(it.signature == "const Foo = struct" for it in items)


def test_enum_declaration():
    items = parse("const Color = enum { red, green, blue };\n")
    assert any(it.signature == "const Color = enum" for it in items)


def test_union_declaration():
    items = parse("const Val = union { a: u32, b: f64 };\n")
    assert any(it.signature == "const Val = union" for it in items)


def test_tagged_union_declaration():
    items = parse("const Act = union(enum) { a, b };\n")
    assert any(it.signature == "const Act = union(enum)" for it in items)


def test_pub_struct():
    items = parse("pub const Widget = struct {};\n")
    assert any(it.signature == "pub const Widget = struct" for it in items)


# ---------------------------------------------------------------------------
# Exclusions
# ---------------------------------------------------------------------------

def test_import_excluded():
    items = parse('const std = @import("std");\n')
    assert items == []


def test_plain_const_excluded():
    items = parse("const MAX: usize = 100;\n")
    assert items == []


def test_string_const_excluded():
    items = parse('const NAME = "MyApp";\n')
    assert items == []


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_fn_sig_merged():
    src = (
        "pub fn fetch(\n"
        "    alloc: Allocator,\n"
        "    url: []const u8,\n"
        ") !Response {\n"
        "}\n"
    )
    items = parse(src)
    assert len(items) == 1
    sig = items[0].signature
    assert sig.startswith("pub fn fetch(")
    assert "alloc: Allocator" in sig
    assert "url: []const u8" in sig
    assert not sig.endswith("{")


def test_multiline_fn_sig_exact():
    src = (
        "pub fn fetch(\n"
        "    alloc: Allocator,\n"
        "    url: []const u8,\n"
        ") !Response {\n"
        "}\n"
    )
    items = parse(src)
    assert items[0].signature == "pub fn fetch(alloc: Allocator, url: []const u8) !Response"


# ---------------------------------------------------------------------------
# Comment walk-back
# ---------------------------------------------------------------------------

def test_doc_comment_walked_back():
    src = "/// Does something.\nfn foo() void {}\n"
    items = parse(src)
    assert items[0].start == 1
    assert items[0].count == 2


def test_regular_comment_walked_back():
    src = "// Helper function\nfn foo() void {}\n"
    items = parse(src)
    assert items[0].start == 1


def test_blank_stops_walkback():
    src = "/// Unrelated.\n\nfn foo() void {}\n"
    items = parse(src)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 3


def test_no_walkback_past_other_item():
    src = "fn bar() void {}\n\nfn foo() void {}\n"
    items = parse(src)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 3


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_fn_range_covers_body():
    src = "fn foo() u32 {\n    return 42;\n}\n"
    items = parse(src)
    assert items[0].count == 3


def test_struct_range_covers_body():
    src = (
        "const Foo = struct {\n"
        "    x: u32,\n"
        "    y: u32,\n"
        "};\n"
    )
    items = parse(src)
    assert items[0].count == 4


def test_struct_range_covers_methods():
    src = (
        "const Foo = struct {\n"
        "    pub fn bar(self: Foo) u32 {\n"
        "        return self.x;\n"
        "    }\n"
        "};\n"
    )
    items = parse(src)
    foo = next(it for it in items if it.signature == "const Foo = struct")
    bar = next(it for it in items if "bar" in it.signature)
    assert foo.start <= bar.start
    assert foo.start + foo.count >= bar.start + bar.count


def test_method_indented_in_struct():
    src = (
        "const Foo = struct {\n"
        "    pub fn bar(self: Foo) void {}\n"
        "};\n"
    )
    items = parse(src)
    bar = next(it for it in items if "bar" in it.signature)
    assert bar.signature.startswith("    ")


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 9


def test_fixture_struct_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "const Animal = struct" in sigs


def test_fixture_enum_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "const Kind = enum" in sigs


def test_fixture_union_sig():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "const Action = union(enum)" in sigs


def test_fixture_fn_sigs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("makeAnimal" in s for s in sigs)
    assert any("fetchAnimal" in s for s in sigs)
    assert any("helper" in s for s in sigs)


def test_fixture_method_sigs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("init" in s for s in sigs)
    assert any("displayName" in s for s in sigs)
    assert any("greet" in s for s in sigs)


def test_fixture_methods_indented():
    items = parse(FIXTURE.read_text())
    init = next(it for it in items if "init" in it.signature)
    assert init.signature.startswith("    ")


def test_fixture_imports_excluded():
    items = parse(FIXTURE.read_text())
    assert all("@import" not in it.signature for it in items)


def test_fixture_plain_consts_excluded():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert not any("MAX_ITEMS" in s for s in sigs)
    assert not any("APP_NAME" in s for s in sigs)


def test_fixture_animal_start_line():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "const Animal = struct")
    assert animal.start == 8


def test_fixture_animal_count():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "const Animal = struct")
    assert animal.count == 26


def test_fixture_init_start_and_count():
    items = parse(FIXTURE.read_text())
    init = next(it for it in items if "init" in it.signature and "Animal" in it.signature)
    assert init.start == 13
    assert init.count == 4


def test_fixture_greet_multiline_sig():
    items = parse(FIXTURE.read_text())
    greet = next(it for it in items if "greet" in it.signature)
    assert greet.signature == "    pub fn greet(self: *const Animal, greeting: []const u8, times: usize) !void"


def test_fixture_greet_start_and_count():
    items = parse(FIXTURE.read_text())
    greet = next(it for it in items if "greet" in it.signature)
    assert greet.start == 23
    assert greet.count == 10


def test_fixture_fetchanimal_start_and_count():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetchAnimal" in it.signature)
    assert fetch.start == 54
    assert fetch.count == 9


def test_fixture_helper_start_and_count():
    items = parse(FIXTURE.read_text())
    helper = next(it for it in items if "helper" in it.signature)
    assert helper.start == 64
    assert helper.count == 3


def test_fixture_struct_contains_methods():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "const Animal = struct")
    init = next(it for it in items if "init" in it.signature)
    assert animal.start < init.start
    assert animal.start + animal.count > init.start + init.count


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("// just a comment\n/// another\n") == []

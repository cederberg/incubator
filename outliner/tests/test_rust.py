"""Tests for the Rust outline parser."""

from pathlib import Path

from outliner.parsers.rust import parse, detect as detect_rust
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "rs"
FIXTURE = FIXTURES / "sample.rs"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_rs():
    assert guess_syntax("file.rs") == "rust"


def test_detect_content_fn_and_impl():
    assert detect_rust([
        "impl Animal {",
        "    pub fn new(name: &str, age: u32) -> Self {",
        "        Animal { name: name.to_string(), age }",
        "    }",
        "}",
    ])


def test_detect_content_fn_and_arrow():
    assert detect_rust([
        "pub fn factorial(n: u64) -> u64 {",
        "    n",
        "}",
    ])


def test_detect_content_fn_and_derive():
    assert detect_rust([
        "#[derive(Debug)]",
        "pub struct Foo { x: i32 }",
        "pub fn make() -> Foo { Foo { x: 0 } }",
    ])


def test_detect_content_not_go():
    assert not detect_rust([
        "package main",
        "func main() {",
        '    fmt.Println("hello")',
        "}",
    ])


def test_detect_content_not_java():
    assert not detect_rust([
        "public class Animal {",
        "    public String name;",
        "    public void speak() {}",
        "}",
    ])


def test_detect_content_not_javascript():
    assert not detect_rust([
        "function foo() {",
        "    return 42;",
        "}",
        "class Bar {}",
    ])


def test_detect_registry_rust_content():
    assert detect(FIXTURE.read_text()) == "rust"


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def test_simple_function():
    items = parse("pub fn foo() -> i32 {\n    42\n}\n")
    assert len(items) == 1
    assert items[0].signature == "pub fn foo() -> i32"
    assert items[0].start == 1
    assert items[0].count == 3


def test_function_no_trailing_brace():
    items = parse("pub fn foo() -> i32 {\n    42\n}\n")
    assert not items[0].signature.endswith("{")


def test_async_function():
    items = parse("pub async fn fetch(url: &str) -> String {\n    todo!()\n}\n")
    assert items[0].signature == "pub async fn fetch(url: &str) -> String"


def test_unsafe_function():
    items = parse("pub unsafe fn raw(ptr: *const u8) -> u8 {\n    *ptr\n}\n")
    assert items[0].signature == "pub unsafe fn raw(ptr: *const u8) -> u8"


def test_multiline_signature_merged():
    text = (
        "pub fn from_parts(\n"
        "    name: String,\n"
        "    age: u32,\n"
        ") -> Option<Animal> {\n"
        "    None\n"
        "}\n"
    )
    items = parse(text)
    assert len(items) == 1
    sig = items[0].signature
    assert "from_parts" in sig
    assert "name: String" in sig
    assert "age: u32" in sig
    assert not sig.endswith("{")


def test_multiline_signature_exact():
    text = (
        "pub fn from_parts(\n"
        "    name: String,\n"
        "    age: u32,\n"
        "    validate: bool,\n"
        ") -> Option<Animal> {\n"
        "    None\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].signature == "pub fn from_parts(name: String, age: u32, validate: bool) -> Option<Animal>"


def test_multiline_where_clause():
    text = (
        "pub fn parse_animal<'a, F>(\n"
        "    input: &'a str,\n"
        "    factory: F,\n"
        ") -> Option<Animal>\n"
        "where\n"
        "    F: Fn(&'a str) -> Option<Animal>,\n"
        "{\n"
        "    factory(input)\n"
        "}\n"
    )
    items = parse(text)
    assert len(items) == 1
    sig = items[0].signature
    assert "parse_animal" in sig
    assert "input" in sig
    assert "factory" in sig


def test_trait_method_no_body():
    items = parse("pub trait Foo {\n    fn bar(&self) -> i32;\n}\n")
    bar = next(it for it in items if "bar" in it.signature)
    assert not bar.signature.endswith(";")
    assert bar.count == 1


def test_use_statements_excluded():
    items = parse("use std::fmt;\nuse std::collections::HashMap;\n\npub fn foo() {}\n")
    assert all("use" not in it.signature for it in items)


# ---------------------------------------------------------------------------
# Structs
# ---------------------------------------------------------------------------

def test_struct():
    items = parse("pub struct Animal {\n    pub name: String,\n}\n")
    assert any("struct Animal" in it.signature for it in items)


def test_struct_no_trailing_brace():
    items = parse("pub struct Foo {\n    x: i32,\n}\n")
    it = next(i for i in items if "struct Foo" in i.signature)
    assert not it.signature.endswith("{")


def test_struct_attribute_walked_back():
    items = parse("#[derive(Debug)]\npub struct Foo {\n    x: i32,\n}\n")
    it = next(i for i in items if "struct Foo" in i.signature)
    assert it.start == 1


def test_struct_range_covers_body():
    text = "pub struct Animal {\n    pub name: String,\n    age: u32,\n}\n"
    items = parse(text)
    it = next(i for i in items if "struct Animal" in i.signature)
    assert it.count == 4


def test_generic_struct():
    items = parse("pub struct Pair<T, U> {\n    first: T,\n    second: U,\n}\n")
    assert any("struct Pair" in it.signature for it in items)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

def test_enum():
    items = parse("pub enum Status {\n    Active,\n    Inactive,\n}\n")
    assert any("enum Status" in it.signature for it in items)


def test_enum_range_covers_body():
    text = "pub enum Status {\n    Active,\n    Inactive,\n    Archived,\n}\n"
    items = parse(text)
    it = next(i for i in items if "enum Status" in i.signature)
    assert it.count == 5


# ---------------------------------------------------------------------------
# Traits
# ---------------------------------------------------------------------------

def test_trait():
    text = "pub trait Speakable {\n    fn speak(&self) -> String;\n}\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert any("trait Speakable" in s for s in sigs)
    assert any("fn speak" in s for s in sigs)


def test_trait_range_covers_methods():
    text = (
        "pub trait Speakable {\n"
        "    fn speak(&self) -> String;\n"
        "\n"
        "    fn shout(&self) -> String {\n"
        "        self.speak().to_uppercase()\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    trait = next(it for it in items if "trait Speakable" in it.signature)
    speak = next(it for it in items if "fn speak" in it.signature)
    assert trait.start <= speak.start
    assert trait.start + trait.count >= speak.start + speak.count


# ---------------------------------------------------------------------------
# Impl blocks
# ---------------------------------------------------------------------------

def test_impl_block():
    text = "impl Animal {\n    pub fn new() -> Self { Animal {} }\n}\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert any("impl Animal" in s for s in sigs)
    assert any("fn new" in s for s in sigs)


def test_impl_trait_for_type():
    text = (
        "impl fmt::Display for Animal {\n"
        "    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {\n"
        "        write!(f, \"{}\")\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    sigs = [it.signature for it in items]
    assert any("impl fmt::Display for Animal" in s for s in sigs)
    assert any("fn fmt" in s for s in sigs)


def test_impl_range_covers_methods():
    text = (
        "impl Animal {\n"
        "    pub fn new(name: &str, age: u32) -> Self {\n"
        "        Animal { name: name.to_string(), age }\n"
        "    }\n"
        "\n"
        "    pub fn name(&self) -> &str {\n"
        "        &self.name\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    impl_block = next(it for it in items if it.signature == "impl Animal")
    new_fn = next(it for it in items if "fn new" in it.signature)
    assert impl_block.start <= new_fn.start
    assert impl_block.start + impl_block.count >= new_fn.start + new_fn.count


def test_impl_generic():
    text = (
        "impl<T: Clone, U: Clone> Pair<T, U> {\n"
        "    pub fn new(first: T, second: U) -> Self {\n"
        "        Pair { first, second }\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    sigs = [it.signature for it in items]
    assert any("impl" in s and "Pair" in s for s in sigs)


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

def test_type_alias():
    items = parse("pub type Registry = HashMap<String, Animal>;\n")
    assert len(items) == 1
    assert "type Registry" in items[0].signature


def test_type_alias_no_trailing_semicolon():
    items = parse("pub type Registry = HashMap<String, Animal>;\n")
    assert not items[0].signature.endswith(";")


# ---------------------------------------------------------------------------
# Mod blocks
# ---------------------------------------------------------------------------

def test_mod_block():
    text = (
        "mod utils {\n"
        "    pub fn double(x: u32) -> u32 {\n"
        "        x * 2\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    sigs = [it.signature for it in items]
    assert any("mod utils" in s for s in sigs)
    assert any("fn double" in s for s in sigs)


def test_mod_range_covers_contents():
    text = (
        "mod utils {\n"
        "    pub fn double(x: u32) -> u32 {\n"
        "        x * 2\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    mod = next(it for it in items if "mod utils" in it.signature)
    fn = next(it for it in items if "fn double" in it.signature)
    assert mod.start <= fn.start
    assert mod.start + mod.count >= fn.start + fn.count


# ---------------------------------------------------------------------------
# Doc comment / attribute walkback
# ---------------------------------------------------------------------------

def test_doc_comment_walked_back():
    text = "/// Doc comment\nfn foo() -> i32 {\n    42\n}\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 4


def test_attribute_walked_back():
    text = "#[derive(Debug)]\npub struct Foo {\n    x: i32,\n}\n"
    items = parse(text)
    assert items[0].start == 1


def test_multi_attr_and_doc_walked_back():
    text = (
        "#[derive(Debug)]\n"
        "#[serde(rename_all = \"camelCase\")]\n"
        "pub struct Foo {\n"
        "    x: i32,\n"
        "}\n"
    )
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 5


def test_blank_stops_walkback():
    text = "/// unrelated\n\nfn foo() -> i32 {\n    42\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 3


def test_no_walkback_past_code():
    text = "let x = 1;\nfn foo() -> i32 {\n    42\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 2


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_function_range_covers_body():
    text = "fn foo() -> i32 {\n    let x = 1;\n    let y = 2;\n    x + y\n}\n"
    items = parse(text)
    assert items[0].count == 5


def test_outer_range_covers_inner():
    text = (
        "impl Foo {\n"
        "    pub fn bar(&self) -> i32 {\n"
        "        42\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    outer = next(it for it in items if "impl Foo" in it.signature)
    inner = next(it for it in items if "fn bar" in it.signature)
    assert outer.start <= inner.start
    assert outer.start + outer.count >= inner.start + inner.count


def test_method_indentation_in_signature():
    text = "impl Foo {\n    pub fn bar(&self) -> i32 {\n        42\n    }\n}\n"
    items = parse(text)
    bar = next(it for it in items if "bar" in it.signature)
    assert bar.signature.startswith("    ")


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 23


def test_fixture_structs():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "pub struct Animal" in sigs
    assert any("struct Pair" in s for s in sigs)


def test_fixture_enum():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "pub enum Status" in sigs


def test_fixture_trait():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "pub trait Speakable" in sigs


def test_fixture_impls():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "impl Animal" in sigs
    assert "impl Speakable for Animal" in sigs
    assert "impl fmt::Display for Animal" in sigs
    assert any("impl" in s and "Pair" in s for s in sigs)


def test_fixture_functions():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("fn factorial" in s for s in sigs)
    assert any("fn parse_animal" in s for s in sigs)


def test_fixture_methods():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("fn new" in s for s in sigs)
    assert any("fn name" in s for s in sigs)
    assert any("fn from_parts" in s for s in sigs)
    assert any("fn is_older_than" in s for s in sigs)
    assert any("fn speak" in s for s in sigs)
    assert any("fn shout" in s for s in sigs)


def test_fixture_type_alias():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("type Registry" in s for s in sigs)


def test_fixture_mod():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert "mod utils" in sigs


def test_fixture_impl_range_covers_methods():
    items = parse(FIXTURE.read_text())
    impl_animal = next(it for it in items if it.signature == "impl Animal")
    new_fn = next(
        it for it in items
        if "fn new" in it.signature and it.start > impl_animal.start
    )
    assert impl_animal.start + impl_animal.count > new_fn.start


def test_fixture_trait_range_covers_methods():
    items = parse(FIXTURE.read_text())
    trait = next(it for it in items if it.signature == "pub trait Speakable")
    speak = next(
        it for it in items
        if "fn speak" in it.signature and it.start > trait.start
    )
    assert trait.start <= speak.start
    assert trait.start + trait.count >= speak.start + speak.count


def test_fixture_struct_animal_start():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "pub struct Animal")
    # doc comment starts at line 6 (1-based)
    assert animal.start == 6


def test_fixture_struct_animal_range():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature == "pub struct Animal")
    assert animal.count == 9  # lines 6-14


def test_fixture_from_parts_exact():
    items = parse(FIXTURE.read_text())
    fn = next(
        it for it in items
        if it.signature.lstrip().startswith("pub fn from_parts(")
    )
    assert fn.signature.strip() == (
        "pub fn from_parts(name: String, age: u32, validate: bool) -> Option<Animal>"
    )


def test_fixture_multiline_parse_animal():
    items = parse(FIXTURE.read_text())
    fn = next(it for it in items if "parse_animal" in it.signature)
    assert "input" in fn.signature
    assert "factory" in fn.signature


def test_fixture_trait_speak_indented():
    items = parse(FIXTURE.read_text())
    # fn speak inside the trait has leading indent
    speak_in_trait = next(
        it for it in items
        if "fn speak" in it.signature
        and it.signature.startswith("    ")
        and it.count == 2  # doc + declaration (no body)
    )
    assert speak_in_trait.signature == "    fn speak(&self) -> String"


def test_fixture_use_excluded():
    items = parse(FIXTURE.read_text())
    assert all("use " not in it.signature for it in items)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("// just a comment\n/// another\n") == []


def test_only_use_statements():
    assert parse("use std::fmt;\nuse std::collections::HashMap;\n") == []

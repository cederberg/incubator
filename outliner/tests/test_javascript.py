"""Tests for the JavaScript/TypeScript outline parser."""

from pathlib import Path

from outliner.parsers.javascript import parse, detect as detect_js
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "js"
FIXTURE = FIXTURES / "sample.ts"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_js():
    assert guess_syntax("file.js") == "javascript"


def test_detect_extension_jsx():
    assert guess_syntax("file.jsx") == "javascript"


def test_detect_extension_ts():
    assert guess_syntax("file.ts") == "javascript"


def test_detect_extension_tsx():
    assert guess_syntax("file.tsx") == "javascript"


def test_detect_content_class_and_function():
    assert detect_js([
        "class Animal {",
        "    constructor(name) { this.name = name; }",
        "}",
        "function makeAnimal(name) { return new Animal(name); }",
    ])


def test_detect_content_ts_interface():
    assert detect_js([
        "export interface Speakable {",
        "    speak(): string;",
        "}",
        "export class Dog implements Speakable {",
        "    speak() { return 'woof'; }",
        "}",
    ])


def test_detect_content_ts_enum():
    assert detect_js([
        "export enum Status { Active, Inactive }",
        "const x: Status = Status.Active;",
    ])


def test_detect_content_arrow_const():
    assert detect_js([
        "const greet = (name: string): string => {",
        "    return `Hello, ${name}`;",
        "};",
    ])


def test_detect_content_not_python():
    assert not detect_js([
        "def foo():",
        "    pass",
        "class Bar:",
        "    pass",
    ])


def test_detect_content_not_go():
    assert not detect_js([
        "package main",
        "func main() {",
        '    fmt.Println("hello")',
        "}",
    ])


def test_detect_content_not_java():
    assert not detect_js([
        "public class Animal {",
        "    public String name;",
        "    public void speak() {}",
        "}",
    ])


def test_detect_registry_ts_content():
    assert detect(FIXTURE.read_text()) == "javascript"


# ---------------------------------------------------------------------------
# Function declarations
# ---------------------------------------------------------------------------

def test_simple_function():
    items = parse("function foo() {\n    return 1;\n}\n")
    assert len(items) == 1
    assert items[0].signature == "function foo()"
    assert items[0].start == 1
    assert items[0].count == 3


def test_function_no_trailing_brace():
    items = parse("function foo() {\n    return 1;\n}\n")
    assert not items[0].signature.endswith("{")


def test_async_function():
    items = parse("async function fetchData(url) {\n    return null;\n}\n")
    assert items[0].signature == "async function fetchData(url)"


def test_exported_function():
    items = parse("export function makeAnimal(name, age) {\n    return {};\n}\n")
    assert items[0].signature == "export function makeAnimal(name, age)"


def test_multiline_function_signature():
    text = (
        "export async function fetchAnimal(\n"
        "    id,\n"
        "    factory,\n"
        ") {\n"
        "    return null;\n"
        "}\n"
    )
    items = parse(text)
    assert len(items) == 1
    sig = items[0].signature
    assert "fetchAnimal" in sig
    assert "id" in sig
    assert "factory" in sig
    assert not sig.endswith("{")


def test_multiline_ts_function_exact():
    text = (
        "export async function fetchAnimal<T extends Animal>(\n"
        "    id: string,\n"
        "    factory: (data: unknown) => T,\n"
        "): Promise<T | null> {\n"
        "    return null;\n"
        "}\n"
    )
    items = parse(text)
    assert len(items) == 1
    sig = items[0].signature
    assert "fetchAnimal" in sig
    assert "id: string" in sig
    assert not sig.endswith("{")


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

def test_simple_class():
    items = parse("class Foo {\n    bar() { return 1; }\n}\n")
    sigs = [it.signature for it in items]
    assert "class Foo" in sigs


def test_class_no_trailing_brace():
    items = parse("class Foo {\n    bar() {}\n}\n")
    cls = next(it for it in items if "class Foo" in it.signature)
    assert not cls.signature.endswith("{")


def test_exported_class():
    items = parse("export class Animal {\n    constructor() {}\n}\n")
    sigs = [it.signature for it in items]
    assert "export class Animal" in sigs


def test_class_extends():
    items = parse("export class Dog extends Animal {\n    fetch() {}\n}\n")
    sigs = [it.signature for it in items]
    assert any("class Dog extends Animal" in s for s in sigs)


def test_class_implements():
    items = parse("export class Animal implements Speakable {\n    speak() {}\n}\n")
    sigs = [it.signature for it in items]
    assert any("class Animal implements Speakable" in s for s in sigs)


def test_class_range_covers_methods():
    text = (
        "class Foo {\n"
        "    bar() {\n"
        "        return 1;\n"
        "    }\n"
        "\n"
        "    baz() {\n"
        "        return 2;\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    cls = next(it for it in items if it.signature == "class Foo")
    bar = next(it for it in items if "bar" in it.signature)
    baz = next(it for it in items if "baz" in it.signature)
    assert cls.start <= bar.start
    assert cls.start + cls.count >= baz.start + baz.count


def test_multiline_class_constructor():
    text = (
        "export class Dog extends Animal {\n"
        "    constructor(\n"
        "        name,\n"
        "        age,\n"
        "        breed,\n"
        "    ) {\n"
        "        super(name, age);\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    ctor = next(it for it in items if "constructor" in it.signature)
    assert "name" in ctor.signature
    assert "breed" in ctor.signature


# ---------------------------------------------------------------------------
# TypeScript: interface, type alias, enum, namespace
# ---------------------------------------------------------------------------

def test_ts_interface():
    items = parse("export interface Speakable {\n    speak(): string;\n}\n")
    assert any("interface Speakable" in it.signature for it in items)


def test_ts_interface_no_trailing_brace():
    items = parse("interface Foo {\n    bar(): void;\n}\n")
    it = next(i for i in items if "interface Foo" in i.signature)
    assert not it.signature.endswith("{")


def test_ts_type_alias():
    items = parse("export type AnimalFactory = (name: string) => Animal;\n")
    assert any("type AnimalFactory" in it.signature for it in items)


def test_ts_type_alias_no_trailing_semicolon():
    items = parse("export type Foo = string | number;\n")
    it = next(i for i in items if "type Foo" in i.signature)
    assert not it.signature.endswith(";")


def test_ts_enum():
    items = parse("export enum Status {\n    Active = 'active',\n    Inactive = 'inactive',\n}\n")
    assert any("enum Status" in it.signature for it in items)


def test_ts_namespace():
    text = (
        "export namespace Utils {\n"
        "    export function clamp(value: number): number {\n"
        "        return value;\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    sigs = [it.signature for it in items]
    assert any("namespace Utils" in s for s in sigs)
    assert any("function clamp" in s for s in sigs)


def test_ts_namespace_range_covers_contents():
    text = (
        "export namespace Utils {\n"
        "    export function clamp(value: number): number {\n"
        "        return value;\n"
        "    }\n"
        "}\n"
    )
    items = parse(text)
    ns = next(it for it in items if "namespace Utils" in it.signature)
    fn = next(it for it in items if "function clamp" in it.signature)
    assert ns.start <= fn.start
    assert ns.start + ns.count >= fn.start + fn.count


# ---------------------------------------------------------------------------
# Arrow functions and function expressions (top-level const/let)
# ---------------------------------------------------------------------------

def test_const_arrow_function():
    items = parse("export const greet = (name) => {\n    return `Hello ${name}`;\n};\n")
    assert any("greet" in it.signature for it in items)


def test_const_arrow_function_signature():
    items = parse("export const greet = (name: string): string => {\n    return name;\n};\n")
    sigs = [it.signature for it in items]
    assert any("const greet" in s for s in sigs)


def test_const_function_expression():
    items = parse("export let helperFn = function(x: number): number {\n    return x * 2;\n};\n")
    assert any("helperFn" in it.signature for it in items)


def test_multiline_arrow_function():
    text = (
        "export const processAnimals = (\n"
        "    animals: Animal[],\n"
        "    predicate: (a: Animal) => boolean,\n"
        "): Animal[] => {\n"
        "    return animals.filter(predicate);\n"
        "};\n"
    )
    items = parse(text)
    fn = next(it for it in items if "processAnimals" in it.signature)
    assert "animals" in fn.signature
    assert "predicate" in fn.signature


def test_plain_const_excluded():
    items = parse("export const MAX_ANIMALS = 100;\nexport const NAME = 'foo';\n")
    assert len(items) == 0


def test_const_class_expression():
    text = (
        "export const AnonymousCat = class extends Animal {\n"
        "    meow() { return 'meow'; }\n"
        "};\n"
    )
    items = parse(text)
    assert any("AnonymousCat" in it.signature for it in items)


# ---------------------------------------------------------------------------
# Decorators (TypeScript)
# ---------------------------------------------------------------------------

def test_decorator_walked_back():
    text = "@injectable()\nexport class Animal {\n    constructor() {}\n}\n"
    items = parse(text)
    cls = next(it for it in items if "class Animal" in it.signature)
    assert cls.start == 1


def test_multiple_decorators_walked_back():
    text = "@injectable()\n@logged\nexport class Animal {\n    constructor() {}\n}\n"
    items = parse(text)
    cls = next(it for it in items if "class Animal" in it.signature)
    assert cls.start == 1
    assert cls.count >= 3


# ---------------------------------------------------------------------------
# Comment walkback
# ---------------------------------------------------------------------------

def test_jsdoc_walked_back():
    text = "/** JSDoc */\nfunction foo() {\n    return 1;\n}\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].count == 4


def test_line_comment_walked_back():
    text = "// A comment\nfunction foo() {\n    return 1;\n}\n"
    items = parse(text)
    assert items[0].start == 1


def test_blank_stops_walkback():
    text = "/** unrelated */\n\nfunction foo() {\n    return 1;\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 3


def test_no_walkback_past_code():
    text = "const x = 1;\nfunction foo() {\n    return 1;\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 2


# ---------------------------------------------------------------------------
# Import exclusion
# ---------------------------------------------------------------------------

def test_imports_excluded():
    text = (
        'import { EventEmitter } from "events";\n'
        'import type { Readable } from "stream";\n'
        "\n"
        "function foo() { return 1; }\n"
    )
    items = parse(text)
    assert all("import" not in it.signature for it in items)
    assert len(items) == 1


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_function_range_covers_body():
    text = "function foo() {\n    const x = 1;\n    const y = 2;\n    return x + y;\n}\n"
    items = parse(text)
    assert items[0].count == 5


def test_trailing_blank_not_in_range():
    text = "function foo() {\n    return 1;\n}\n\nfunction bar() {\n    return 2;\n}\n"
    items = parse(text)
    foo = next(it for it in items if "foo" in it.signature)
    bar = next(it for it in items if "bar" in it.signature)
    assert foo.start + foo.count <= bar.start


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 24


def test_fixture_enum():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("enum Status" in s for s in sigs)


def test_fixture_type_alias():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("type AnimalFactory" in s for s in sigs)


def test_fixture_interface():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("interface Speakable" in s for s in sigs)


def test_fixture_namespace():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("namespace Utils" in s for s in sigs)


def test_fixture_classes():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("class Animal" in s for s in sigs)
    assert any("class Dog" in s for s in sigs)


def test_fixture_functions():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("makeAnimal" in s for s in sigs)
    assert any("fetchAnimal" in s for s in sigs)


def test_fixture_arrow_functions():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("createRegistry" in s for s in sigs)
    assert any("processAnimals" in s for s in sigs)


def test_fixture_constants_excluded():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert not any("MAX_ANIMALS" in s for s in sigs)
    assert not any("DEFAULT_NAME" in s for s in sigs)


def test_fixture_imports_excluded():
    items = parse(FIXTURE.read_text())
    assert all("import" not in it.signature for it in items)


def test_fixture_class_range_covers_methods():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if "class Animal" in it.signature and "Dog" not in it.signature)
    ctor = next(it for it in items if "constructor" in it.signature and it.start > animal.start)
    assert animal.start + animal.count > ctor.start


def test_fixture_decorator_walkback():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if "class Animal" in it.signature and "Dog" not in it.signature)
    # @injectable() and @logged decorators precede the class
    assert animal.start <= 35  # decorators start around line 33


def test_fixture_multiline_static_fromObject():
    items = parse(FIXTURE.read_text())
    fn = next(it for it in items if "fromObject" in it.signature)
    assert "data" in fn.signature
    assert "validate" in fn.signature


def test_fixture_multiline_fetch_sig():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetch(" in it.signature and "item" in it.signature)
    assert "item: string" in fetch.signature
    assert "distance: number" in fetch.signature


# ---------------------------------------------------------------------------
# Edge cases and additional coverage
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("// just a comment\n/* another */\n") == []


def test_only_imports():
    assert parse('import foo from "bar";\nimport type { X } from "y";\n') == []


def test_export_default_function_anonymous_excluded():
    # Anonymous default export has no name — excluded intentionally
    items = parse("export default function() {\n    return 1;\n}\n")
    assert len(items) == 0


def test_const_fn_type_annotation_with_arrow():
    # Const with function-type annotation (contains =>) — must still be detected
    items = parse("export const transform: (x: number) => number = (x) => x * 2;\n")
    assert any("transform" in it.signature for it in items)


def test_multiline_type_alias_count():
    # Multi-line union type: count covers all lines to semicolon
    text = "export type Status =\n    | Active\n    | Inactive;\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].count == 3


def test_nested_type_alias_indented():
    # Type alias inside namespace gets indent prefix
    text = "export namespace Utils {\n    export type Range = { min: number; max: number };\n}\n"
    items = parse(text)
    alias = next(it for it in items if "Range" in it.signature)
    assert alias.signature.startswith("    ")

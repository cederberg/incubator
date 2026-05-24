"""Tests for the JavaScript/TypeScript outline parser."""

from pathlib import Path

from outliner.cli import guess_syntax
from outliner.parsers import detect
from outliner.parsers.javascript import parse as _parse, detect as detect_js


def parse(text):
    return list(_parse(text))


FIXTURES = Path(__file__).parent / "fixtures"
JS_FIXTURE = FIXTURES / "js" / "sample.js"
JSX_FIXTURE = FIXTURES / "js" / "component.jsx"
TS_FIXTURE = FIXTURES / "ts" / "sample.ts"
TSX_FIXTURE = FIXTURES / "ts" / "component.tsx"


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


def test_detect_extension_mjs():
    assert guess_syntax("file.mjs") == "javascript"


def test_detect_extension_cjs():
    assert guess_syntax("file.cjs") == "javascript"


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
    assert detect(TS_FIXTURE.read_text()) == "javascript"


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


def test_ts_interface_includes_methods_and_excludes_value_fields():
    items = parse("interface Foo {\n    value: string;\n    run(): void;\n}\n")
    assert [it.signature for it in items] == ["interface Foo", "    run(): void"]


def test_ts_type_alias():
    items = parse("export type AnimalFactory = (name: string) => Animal;\n")
    assert any("type AnimalFactory" in it.signature for it in items)


def test_ts_type_alias_no_trailing_semicolon():
    items = parse("export type Foo = string | number;\n")
    it = next(i for i in items if "type Foo" in i.signature)
    assert not it.signature.endswith(";")


def test_object_type_alias_includes_methods_and_excludes_value_fields():
    items = parse("type Foo = {\n    value: string;\n    run(): void;\n};\n")
    assert [it.signature for it in items] == ["type Foo", "    run(): void"]


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
    greet = next(it for it in items if "greet" in it.signature)
    assert greet.count == 3


def test_const_arrow_function_signature():
    items = parse("export const greet = (name: string): string => {\n    return name;\n};\n")
    sigs = [it.signature for it in items]
    assert any("const greet" in s for s in sigs)


def test_const_function_expression():
    items = parse("export let helperFn = function(x: number): number {\n    return x * 2;\n};\n")
    helper = next(it for it in items if "helperFn" in it.signature)
    assert helper.count == 3


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


def test_multiline_destructured_arrow_range_covers_body():
    text = (
        "const render = ({\n"
        "    value,\n"
        "}: Props) => {\n"
        "    return value;\n"
        "};\n"
    )
    items = parse(text)
    assert [it.signature for it in items] == ["const render = ({ value, }: Props)"]
    assert items[0].count == 5


def test_arrow_returning_multiline_template_has_complete_range():
    text = (
        "const animation = (factor: number) => `\n"
        "0% { transform: scale(${factor}); }\n"
        "100% { transform: scale(1); }\n"
        "`;\n"
    )
    items = parse(text)
    assert [it.signature for it in items] == ["const animation = (factor: number)"]
    assert items[0].count == 4


def test_arrow_with_multiline_object_type_annotation():
    text = (
        "export const ToastIcon: React.FC<{\n"
        "    toast: Toast;\n"
        "}> = ({ toast }) => {\n"
        "    return toast.icon;\n"
        "};\n"
    )
    items = parse(text)
    assert [it.signature for it in items] == [
        "export const ToastIcon: React.FC<{ toast: Toast; }> = ({ toast })"
    ]
    assert items[0].count == 5


def test_multiline_typed_value_does_not_capture_following_arrow():
    text = (
        "const options: {\n"
        "    enabled: boolean;\n"
        "} = {\n"
        "    enabled: true,\n"
        "};\n"
        "const later = () => {\n"
        "    return true;\n"
        "};\n"
    )
    items = parse(text)
    assert [it.signature for it in items] == ["const later = ()"]


def test_plain_const_excluded():
    items = parse("export const MAX_ANIMALS = 100;\nexport const NAME = 'foo';\n")
    assert len(items) == 0


def test_const_class_expression():
    text = (
        "export const AnonymousCat = class extends Animal {\n"
        "    name = 'cat';\n"
        "    meow() { return 'meow'; }\n"
        "};\n"
    )
    items = parse(text)
    cat = next(it for it in items if "AnonymousCat" in it.signature)
    assert cat.count == 4


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
# JavaScript fixture tests
# ---------------------------------------------------------------------------

def test_js_fixture_core_declarations():
    items = parse(JS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("class Animal" in s for s in sigs)
    assert any("class Dog" in s for s in sigs)
    assert any("makeAnimal" in s for s in sigs)
    assert any("createRegistry" in s for s in sigs)
    assert any("processAnimals" in s for s in sigs)
    assert any("normalizeName" in s for s in sigs)
    assert any("helperFn" in s for s in sigs)
    assert any("AnonymousCat" in s for s in sigs)


def test_js_fixture_includes_class_members_and_excludes_constants():
    items = parse(JS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("constructor" in s for s in sigs)
    assert any("speak" in s for s in sigs)
    assert not any("MAX_ANIMALS" in s for s in sigs)


def test_js_fixture_function_value_ranges_cover_body():
    items = parse(JS_FIXTURE.read_text())
    registry = next(it for it in items if "createRegistry" in it.signature)
    helper = next(it for it in items if "helperFn" in it.signature)
    cat = next(it for it in items if "AnonymousCat" in it.signature)
    assert registry.count == 6
    assert helper.count == 5
    assert cat.count == 6


def test_jsx_fixture_component_declarations():
    items = parse(JSX_FIXTURE.read_text())
    assert [it.signature for it in items] == [
        "export function Card({ title, children })",
        "export const Badge = ({ label })",
    ]
    assert [it.count for it in items] == [3, 3]


def test_iife_exposes_module_declarations_and_class_members():
    items = parse(
        "(function (window) {\n"
        "    class AdminApp {\n"
        "        start() {\n"
        "            function local() {}\n"
        "        }\n"
        "    }\n"
        "    function helper() {}\n"
        "    window.AdminApp = AdminApp;\n"
        "})(window);\n"
    )
    sigs = [it.signature.strip() for it in items]
    assert sigs == ["class AdminApp", "start()", "function helper()"]
    assert not any("local" in sig for sig in sigs)


def test_assigned_iife_exposes_direct_declarations_only():
    items = parse(
        "var library = (function () {\n"
        "    function exported() {}\n"
        "    function outer() {\n"
        "        function local() {}\n"
        "    }\n"
        "})();\n"
    )
    sigs = [it.signature.strip() for it in items]
    assert sigs[0] == "var library = (function ()"
    assert "function exported()" in sigs
    assert "function outer()" in sigs
    assert not any("local" in sig for sig in sigs)


def test_unary_iife_exposes_direct_declarations_only():
    items = parse(
        "!function () {\n"
        "    function exported() {}\n"
        "    function outer() {\n"
        "        function local() {}\n"
        "    }\n"
        "}();\n"
    )
    sigs = [it.signature.strip() for it in items]
    assert sigs == ["function exported()", "function outer()"]


def test_semicolon_guarded_iife_exposes_direct_declarations_only():
    items = parse(
        ";(function () {\n"
        "    function exported() {}\n"
        "    function outer() {\n"
        "        function local() {}\n"
        "    }\n"
        "}());\n"
    )
    sigs = [it.signature.strip() for it in items]
    assert sigs == ["function exported()", "function outer()"]


def test_amd_factory_exposes_direct_declarations_only():
    items = parse(
        "define(['exports'], (function (exports) { 'use strict';\n"
        "    function exported() {}\n"
        "    function outer() {\n"
        "        function local() {}\n"
        "    }\n"
        "}));\n"
    )
    sigs = [it.signature.strip() for it in items]
    assert sigs == ["function exported()", "function outer()"]


def test_property_functions_expose_commonjs_api():
    items = parse(
        "var file = module.exports = {};\n"
        "file.exists = function() {\n"
        "    return true;\n"
        "};\n"
        "file.expand = function(...args) {\n"
        "    return args;\n"
        "};\n"
    )
    assert [it.signature for it in items] == [
        "file.exists = function()",
        "file.expand = function(...args)",
    ]
    assert [it.count for it in items] == [3, 3]


def test_property_arrows_expose_commonjs_api():
    items = parse(
        "exports.read = path => path;\n"
        "module.exports.sync = path => {\n"
        "    return true;\n"
        "};\n"
    )
    assert [it.signature for it in items] == [
        "exports.read = path => path",
        "module.exports.sync = path",
    ]
    assert [it.count for it in items] == [1, 3]


def test_prototype_object_includes_callable_members_and_excludes_value_fields():
    items = parse(
        "Widget.prototype = {\n"
        "    start: function() {\n"
        "        return true;\n"
        "    },\n"
        "    stop() {},\n"
        "    poll: () => false,\n"
        "    enabled: true,\n"
        "    callback: helper\n"
        "};\n"
    )
    assert [it.signature for it in items] == [
        "Widget.prototype =",
        "    start: function()",
        "    stop()",
        "    poll: () => false",
    ]
    assert [it.count for it in items] == [9, 3, 1, 1]


def test_chained_prototype_object_is_a_callable_member_container():
    items = parse("Dispatch.prototype = dispatch.prototype = {\n    call: function() {}\n};\n")
    assert [it.signature for it in items] == [
        "Dispatch.prototype = dispatch.prototype =",
        "    call: function()",
    ]


def test_plain_object_methods_remain_excluded():
    items = parse("const options = {\n    start() {},\n    stop: function() {}\n};\n")
    assert items == []


# ---------------------------------------------------------------------------
# TypeScript fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(TS_FIXTURE.read_text())
    assert len(items) == 43


def test_fixture_enum():
    items = parse(TS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("enum Status" in s for s in sigs)


def test_fixture_type_alias():
    items = parse(TS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("type AnimalFactory" in s for s in sigs)


def test_fixture_object_type_alias_range_excludes_plain_fields():
    items = parse(TS_FIXTURE.read_text())
    alias = next(it for it in items if "type ColorSummary" in it.signature)
    assert alias.count == 5
    assert not any("red: number" in it.signature or "green: number" in it.signature for it in items)


def test_fixture_interface():
    items = parse(TS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("interface Speakable" in s for s in sigs)


def test_fixture_namespace():
    items = parse(TS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("namespace Utils" in s for s in sigs)


def test_fixture_classes():
    items = parse(TS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("class Animal" in s for s in sigs)
    assert any("class Dog" in s for s in sigs)


def test_fixture_functions():
    items = parse(TS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("makeAnimal" in s for s in sigs)
    assert any("fetchAnimal" in s for s in sigs)


def test_fixture_arrow_functions():
    items = parse(TS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("createRegistry" in s for s in sigs)
    assert any("processAnimals" in s for s in sigs)


def test_fixture_constants_excluded():
    items = parse(TS_FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert not any("MAX_ANIMALS" in s for s in sigs)
    assert not any("DEFAULT_NAME" in s for s in sigs)


def test_fixture_imports_excluded():
    items = parse(TS_FIXTURE.read_text())
    assert all("import" not in it.signature for it in items)


def test_fixture_class_range_covers_methods():
    items = parse(TS_FIXTURE.read_text())
    animal = next(it for it in items if "class Animal" in it.signature and "Dog" not in it.signature)
    ctor = next(it for it in items if "constructor" in it.signature and it.start > animal.start)
    assert animal.start + animal.count > ctor.start


def test_fixture_decorator_walkback():
    text = TS_FIXTURE.read_text()
    items = parse(text)
    animal = next(it for it in items if "class Animal" in it.signature and "Dog" not in it.signature)
    class_line = text.splitlines().index("export class Animal implements Speakable {") + 1
    leading_lines = text.splitlines()[animal.start - 1:class_line - 1]
    assert "@injectable()" in leading_lines
    assert "@logged" in leading_lines


def test_fixture_multiline_static_fromObject():
    items = parse(TS_FIXTURE.read_text())
    fn = next(it for it in items if "fromObject" in it.signature)
    assert "data" in fn.signature
    assert "validate" in fn.signature


def test_fixture_multiline_fetch_sig():
    items = parse(TS_FIXTURE.read_text())
    fetch = next(it for it in items if "fetch(" in it.signature and "item" in it.signature)
    assert "item: string" in fetch.signature
    assert "distance: number" in fetch.signature


def test_tsx_fixture_component_declarations():
    items = parse(TSX_FIXTURE.read_text())
    assert [it.signature for it in items] == [
        "type Props<T>",
        "export interface ViewProps",
        "export function View({ title }: ViewProps): JSX.Element",
        "export const Box = <T,>({ value, render }: Props<T>): JSX.Element",
    ]
    assert [it.count for it in items] == [1, 3, 3, 3]


def test_fixture_commented_constructor_signature_excludes_parameter_docs():
    items = parse(TS_FIXTURE.read_text())
    constructor = next(it for it in items if "constructor" in it.signature and "breed" in it.signature)
    assert constructor.signature == "    constructor(name: string, age: number, breed: string)"


def test_fixture_exposes_ambient_namespace_declarations_and_members():
    sigs = [it.signature.strip() for it in parse(TS_FIXTURE.read_text())]
    expected = [
        "declare namespace palette",
        "type Level",
        "interface Painter",
        "paint(text: string): string",
        "(text: string): string",
        "blend(foreground: string, background: string): string",
        "namespace nested",
        "interface Formatter",
        "format(value: string): string",
        "declare const palette: palette.Painter &",
    ]
    assert all(signature in sigs for signature in expected)
    excluded = [
        "readonly level: Level",
        "readonly primary: string",
        "readonly secondary: string",
        "readonly formatter: | string | ((value: string) => string)",
        "supportsColor: boolean",
    ]
    assert all(signature not in sigs for signature in excluded)
    assert all("fake(value: string)" not in signature for signature in sigs)
    assert not any(signature.startswith(("foreground: string", "background: string")) for signature in sigs)


def test_fixture_exposes_abstract_module_and_global_declarations():
    sigs = [it.signature.strip() for it in parse(TS_FIXTURE.read_text())]
    expected = [
        "export declare abstract class AbstractPainter",
        "abstract clear(): void",
        "abstract reset(): void",
        "abstract draw(): void",
        'declare module "palette-plugin"',
        "export function activate(): void",
        "declare global",
        "interface Window",
    ]
    assert all(signature in sigs for signature in expected)
    assert "readonly palette: palette.Painter" not in sigs


def test_ts_export_assignment():
    items = parse("export = palette;\n")
    assert [it.signature for it in items] == ["export = palette"]


# ---------------------------------------------------------------------------
# Edge cases and additional coverage
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("// just a comment\n/* another */\n") == []


def test_only_imports():
    assert parse('import foo from "bar";\nimport type { X } from "y";\n') == []


def test_export_default_function_anonymous_included():
    items = parse("export default function() {\n    return 1;\n}\n")
    assert [it.signature for it in items] == ["export default function()"]
    assert items[0].count == 3


def test_standalone_anonymous_function_expression_excluded():
    items = parse("(function() {\n    return 1;\n})();\n")
    assert items == []


def test_const_fn_type_annotation_with_arrow():
    # Const with function-type annotation (contains =>) — must still be detected
    items = parse("export const transform: (x: number) => number = (x) => x * 2;\n")
    assert any("transform" in it.signature for it in items)


def test_regex_literal_does_not_extend_arrow_signature():
    text = (
        "const slash = (value) => value.replace(/\\//g, \"\\\\\");\n"
        "const later = () => true;\n"
    )
    items = parse(text)
    assert [it.signature for it in items] == [
        'const slash = (value) => value.replace(/\\//g, "\\\\")',
        "const later = () => true",
    ]
    assert [it.count for it in items] == [1, 1]


def test_nested_template_literal_does_not_extend_arrow_range():
    text = (
        "const glob = ({suffix}) => {\n"
        "    return `${suffix ? `/*${suffix}` : \"\"}`;\n"
        "};\n"
        "const later = () => true;\n"
    )
    items = parse(text)
    assert [it.signature for it in items] == [
        "const glob = ({suffix})",
        "const later = () => true",
    ]
    assert [it.count for it in items] == [3, 1]


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


def test_class_members_included():
    text = "class Foo {\n    constructor() {}\n    bar() {}\n}\n"
    items = parse(text)
    assert [it.signature for it in items] == ["class Foo", "    constructor()", "    bar()"]


def test_class_includes_function_valued_fields_and_excludes_value_fields():
    text = (
        "class Foo {\n"
        "    value = 1;\n"
        "    handle = () => {\n"
        "        return;\n"
        "    };\n"
        "    parse: (value: string) => string = (value) => value;\n"
        "}\n"
    )
    items = parse(text)
    assert [it.signature for it in items] == [
        "class Foo",
        "    handle = ()",
        "    parse: (value: string) => string = (value) => value",
    ]


def test_nested_functions_excluded():
    text = (
        "export function top() {\n"
        "    function inner() {}\n"
        "    const local = () => 1;\n"
        "}\n"
    )
    items = parse(text)
    assert [it.signature for it in items] == ["export function top()"]


def test_nested_namespace_declarations_included():
    text = (
        "export namespace A {\n"
        "    export namespace B {\n"
        "        export function deep() {}\n"
        "    }\n"
        "    export function ok() {}\n"
        "}\n"
    )
    items = parse(text)
    sigs = [it.signature for it in items]
    assert any("namespace A" in s for s in sigs)
    assert any("namespace B" in s for s in sigs)
    assert any("function ok" in s for s in sigs)
    assert any("function deep" in s for s in sigs)


def test_type_alias_generic_default_kept():
    items = parse("export type Box<T = string> = { value: T };\n")
    assert items[0].signature == "export type Box<T = string>"

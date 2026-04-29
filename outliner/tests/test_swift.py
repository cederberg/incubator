"""Tests for the Swift outline parser."""

from pathlib import Path

from outliner.parsers.swift import parse as _parse, detect as detect_swift

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "swift"
FIXTURE = FIXTURES / "sample.swift"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_swift():
    assert guess_syntax("file.swift") == "swift"


def test_detect_content_fileprivate():
    assert detect_swift(["fileprivate func helper() -> Int {", "    return 0", "}"])


def test_detect_content_fileprivate_yaml_not_triggered():
    # "fileprivate:" as a YAML key must not trigger Swift detection
    assert not detect_swift(["fileprivate: true", "name: foo"])


def test_detect_content_actor():
    assert detect_swift(["actor DataStore {", "    func get() -> Int { 0 }", "}"])


def test_detect_content_func_colon_params():
    assert detect_swift(["func greet(name: String) -> String {", '    return "hi"', "}"])


def test_detect_content_open_class():
    assert detect_swift(["open class Animal {", "    func speak() -> String { '' }", "}"])


def test_detect_content_not_go():
    assert not detect_swift(["package main", "func main() {", '    fmt.Println("hello")', "}"])


def test_detect_content_not_rust():
    assert not detect_swift(["fn main() {", '    println!("hi");', "}"])


def test_detect_content_no_match():
    assert not detect_swift(["Hello world", "No code here"])


def test_detect_registry_swift_content():
    assert detect(FIXTURE.read_text()) == "swift"


# ---------------------------------------------------------------------------
# Type declarations — class, struct, enum, protocol, actor
# ---------------------------------------------------------------------------

def test_simple_class():
    items = parse("class Foo {\n}\n")
    assert any("class Foo" in it.signature for it in items)


def test_no_trailing_brace_in_sig():
    items = parse("class Foo {\n}\n")
    cls = next(it for it in items if "class Foo" in it.signature)
    assert not cls.signature.endswith("{")


def test_struct_detected():
    items = parse("struct Point {\n    var x: Double\n}\n")
    assert any("struct Point" in it.signature for it in items)


def test_enum_detected():
    items = parse("enum Status {\n    case active\n}\n")
    assert any("enum Status" in it.signature for it in items)


def test_protocol_detected():
    items = parse("protocol Speakable {\n    func speak() -> String\n}\n")
    assert any("protocol Speakable" in it.signature for it in items)


def test_actor_detected():
    items = parse("actor DataStore {\n    func get() -> Int { 0 }\n}\n")
    assert any("actor DataStore" in it.signature for it in items)


def test_open_class():
    items = parse("open class Animal {\n}\n")
    assert any("Animal" in it.signature for it in items)


def test_generic_class():
    items = parse("class Container<T: Equatable> {\n}\n")
    assert any("Container" in it.signature for it in items)


# ---------------------------------------------------------------------------
# Functions and methods
# ---------------------------------------------------------------------------

def test_simple_func():
    items = parse("func greet() -> String {\n    return ''\n}\n")
    assert len(items) == 1
    assert items[0].signature == "func greet() -> String"


def test_func_with_labeled_params():
    items = parse("func greet(name: String) -> String {\n    return name\n}\n")
    assert items[0].signature == "func greet(name: String) -> String"


def test_func_no_trailing_brace():
    items = parse("func foo() {\n}\n")
    assert not items[0].signature.endswith("{")


def test_method_in_class():
    code = "class Foo {\n    func bar() -> Int {\n        return 0\n    }\n}\n"
    items = parse(code)
    sigs = [it.signature for it in items]
    assert any("bar()" in s for s in sigs)


def test_static_method():
    code = "class Foo {\n    static func create() -> Foo {\n        return Foo()\n    }\n}\n"
    items = parse(code)
    assert any("static func create()" in it.signature for it in items)


def test_class_func_not_false_type():
    # "class func" must not be matched as type declaration named "func"
    code = "class Foo {\n    class func make() -> Foo {\n        return Foo()\n    }\n}\n"
    items = parse(code)
    sigs = [it.signature for it in items]
    assert any("class func make()" in s for s in sigs)
    assert not any(s.strip() == "class func" for s in sigs)


def test_class_var_excluded():
    # "class var" is a stored/computed property, not a type declaration
    code = "class Foo {\n    class var count: Int { return 0 }\n}\n"
    items = parse(code)
    sigs = [it.signature for it in items]
    assert not any("count" in s for s in sigs)


def test_override_method():
    code = "class Dog: Animal {\n    override func speak() -> String {\n        return 'Woof'\n    }\n}\n"
    items = parse(code)
    assert any("override func speak()" in it.signature for it in items)


def test_async_throws_func():
    items = parse("func load(url: URL) async throws -> Data {\n    return Data()\n}\n")
    assert any("async throws -> Data" in it.signature for it in items)


def test_operator_func():
    items = parse("func ==(lhs: Foo, rhs: Foo) -> Bool {\n    return true\n}\n")
    assert any("==" in it.signature for it in items)


def test_nonisolated_unsafe_func():
    # Swift 6: nonisolated(unsafe) modifier
    items = parse("nonisolated(unsafe) func foo() -> Int {\n    return 0\n}\n")
    assert any("foo()" in it.signature for it in items)


def test_single_line_body_not_in_sig():
    # Inline body content must not appear in the signature
    items = parse("func foo() -> Int { return 0 }\n")
    assert items[0].signature == "func foo() -> Int"


def test_protocol_method_no_body():
    items = parse("protocol Foo {\n    func bar() -> Int\n}\n")
    sigs = [it.signature for it in items]
    assert any("bar()" in s for s in sigs)


# ---------------------------------------------------------------------------
# init / deinit
# ---------------------------------------------------------------------------

def test_init_detected():
    code = "class Foo {\n    init(name: String) {\n        self.name = name\n    }\n}\n"
    items = parse(code)
    assert any("init(" in it.signature for it in items)


def test_required_init():
    code = "class Foo {\n    required init(coder: NSCoder) {\n    }\n}\n"
    items = parse(code)
    assert any("init(coder:" in it.signature for it in items)


def test_convenience_init():
    code = "class Foo {\n    convenience init(value: Int) {\n        self.init()\n    }\n}\n"
    items = parse(code)
    assert any("init(value:" in it.signature for it in items)


def test_deinit_detected():
    code = "class Foo {\n    deinit {\n        cleanup()\n    }\n}\n"
    items = parse(code)
    assert any("deinit" in it.signature for it in items)


# ---------------------------------------------------------------------------
# Extension
# ---------------------------------------------------------------------------

def test_extension_detected():
    items = parse("extension Animal {\n    func describe() -> String {\n        return name\n    }\n}\n")
    sigs = [it.signature for it in items]
    assert any("extension Animal" in s for s in sigs)


def test_extension_conformance():
    items = parse("extension Dog: CustomStringConvertible {\n}\n")
    assert any("extension Dog" in it.signature for it in items)


def test_extension_range_covers_method():
    code = (
        "extension Animal {\n"
        "    func describe() -> String {\n"
        "        return name\n"
        "    }\n"
        "}\n"
    )
    items = parse(code)
    ext = next(it for it in items if "extension Animal" in it.signature)
    meth = next(it for it in items if "describe()" in it.signature)
    assert ext.start <= meth.start
    assert ext.start + ext.count >= meth.start + meth.count


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_sig_merged():
    code = (
        "func process(\n"
        "    data: Data,\n"
        "    options: Options\n"
        ") -> Result {\n"
        "    return .success\n"
        "}\n"
    )
    items = parse(code)
    assert len(items) == 1
    sig = items[0].signature
    assert "data: Data" in sig
    assert "options: Options" in sig
    assert not sig.endswith("{")


def test_fixture_multiline_fetch_sig():
    items = parse(FIXTURE.read_text())
    fetch = next(it for it in items if "fetchData" in it.signature)
    assert "from url: URL" in fetch.signature
    assert "timeout: TimeInterval" in fetch.signature
    assert not fetch.signature.endswith("{")
    # No stray space before the closing paren
    assert " )" not in fetch.signature


def test_fixture_multiline_process_sig():
    items = parse(FIXTURE.read_text())
    proc = next(it for it in items if "processAnimals" in it.signature)
    assert "animals: [Animal]" in proc.signature
    assert "transform:" in proc.signature


# ---------------------------------------------------------------------------
# Comment / attribute walkback
# ---------------------------------------------------------------------------

def test_doc_comment_walked_back():
    code = "/// A greeting function.\nfunc greet() -> String {\n    return 'hi'\n}\n"
    items = parse(code)
    assert items[0].start == 1


def test_attribute_walked_back():
    code = "@discardableResult\nfunc greet() -> String {\n    return 'hi'\n}\n"
    items = parse(code)
    assert items[0].start == 1


def test_doc_and_attribute_walked_back():
    code = "/// Docs.\n@discardableResult\nfunc greet() -> String {\n    return 'hi'\n}\n"
    items = parse(code)
    assert items[0].start == 1
    assert items[0].count == 5


def test_no_walkback_past_code():
    code = "let x = 1\nfunc foo() {\n}\n"
    items = parse(code)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 2


def test_blank_line_stops_walkback():
    code = "/// unrelated\n\nfunc foo() {\n}\n"
    items = parse(code)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 3


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_class_range_covers_methods():
    code = (
        "class Foo {\n"
        "    func bar() -> Int {\n"
        "        return 0\n"
        "    }\n"
        "\n"
        "    func baz() -> Int {\n"
        "        return 1\n"
        "    }\n"
        "}\n"
    )
    items = parse(code)
    cls = next(it for it in items if it.signature.strip() == "class Foo")
    bar = next(it for it in items if "bar()" in it.signature)
    baz = next(it for it in items if "baz()" in it.signature)
    assert cls.start <= bar.start
    assert cls.start + cls.count >= baz.start + baz.count


def test_func_range_covers_body():
    code = "func foo() {\n    let x = 1\n    let y = 2\n    return x + y\n}\n"
    items = parse(code)
    assert items[0].count == 5


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_detects_swift():
    assert detect_swift(FIXTURE.read_text().splitlines()[:50])


def test_fixture_protocol_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("protocol Speakable" in s for s in sigs)
    assert any("protocol Feedable" in s for s in sigs)


def test_fixture_enum_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("enum Status" in s for s in sigs)


def test_fixture_struct_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("struct Point" in s for s in sigs)


def test_fixture_class_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("class Animal" in s for s in sigs)
    assert any("class Dog" in s for s in sigs)


def test_fixture_actor_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("actor DataStore" in s for s in sigs)


def test_fixture_extension_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("extension Animal" in s for s in sigs)
    assert any("extension Dog" in s for s in sigs)


def test_fixture_init_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("init(name:" in s for s in sigs)


def test_fixture_deinit_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("deinit" in s for s in sigs)


def test_fixture_protocol_methods_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("speak()" in s for s in sigs)
    assert any("feed(amount:" in s for s in sigs)


def test_fixture_free_functions_detected():
    items = parse(FIXTURE.read_text())
    sigs = [it.signature for it in items]
    assert any("makeAnimal" in s for s in sigs)
    assert any("processAnimals" in s for s in sigs)


def test_fixture_class_range_covers_methods():
    items = parse(FIXTURE.read_text())
    animal = next(it for it in items if it.signature.strip().startswith("open class Animal"))
    init_item = next(it for it in items if "init(name: String, age: Int)" in it.signature)
    fetch_item = next(it for it in items if "fetchData" in it.signature)
    assert animal.start <= init_item.start
    assert animal.start + animal.count >= fetch_item.start + fetch_item.count


def test_fixture_doc_comment_walkback():
    items = parse(FIXTURE.read_text())
    # "Base animal class." doc comment appears before `open class Animal`
    animal = next(it for it in items if it.signature.strip().startswith("open class Animal"))
    # The doc comment "/// Base animal class." should be included
    assert animal.start <= 53  # doc comment at line 53, class at line 54


def test_fixture_attribute_walkback():
    items = parse(FIXTURE.read_text())
    # @discardableResult precedes fetchData
    fetch_item = next(it for it in items if "fetchData" in it.signature)
    # @discardableResult and /// Fetch ... are both before the func line
    assert fetch_item.count > 5  # should include the comment + attribute + body


# ---------------------------------------------------------------------------
# Inline empty body stripping
# ---------------------------------------------------------------------------

def test_inline_empty_body_stripped():
    items = parse("extension Foo: Sendable {}\n")
    assert items[0].signature == "extension Foo: Sendable"


def test_inline_body_stripped_with_where():
    items = parse("extension Foo: Sendable where Value: Sendable {}\n")
    assert items[0].signature == "extension Foo: Sendable where Value: Sendable"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse("// just a comment\n// another\n") == []


def test_import_excluded():
    items = parse("import Foundation\nimport UIKit\n")
    assert items == []

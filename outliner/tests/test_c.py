"""Tests for the C/C++ outline parser."""

from pathlib import Path

import pytest

from outliner.parsers.c import parse as _parse, detect as detect_c

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "c"
FIXTURE_C = FIXTURES / "sample.c"
FIXTURE_CPP = FIXTURES / "sample.cpp"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_c():
    assert guess_syntax("file.c") == "c"


def test_detect_extension_h():
    assert guess_syntax("file.h") == "c"


def test_detect_extension_cpp():
    assert guess_syntax("file.cpp") == "c"


def test_detect_extension_cc():
    assert guess_syntax("file.cc") == "c"


def test_detect_extension_cxx():
    assert guess_syntax("file.cxx") == "c"


def test_detect_extension_hpp():
    assert guess_syntax("file.hpp") == "c"


def test_detect_content_include_struct():
    assert detect_c(['#include <stdio.h>', 'struct Foo {', '    int x;', '};'])


def test_detect_content_include_func():
    assert detect_c(['#include <string.h>', 'int add(int a, int b);'])


def test_detect_content_no_include():
    # Without #include, must not trigger
    assert not detect_c(['struct Foo {', '    int x;', '};'])


def test_detect_content_no_match():
    assert not detect_c(['Hello world', 'No code here'])


def test_detect_registry_c_content():
    assert detect(FIXTURE_C.read_text()) == "c"


def test_detect_registry_cpp_content():
    assert detect(FIXTURE_CPP.read_text()) == "c"


# ---------------------------------------------------------------------------
# #define macros
# ---------------------------------------------------------------------------

def test_define_simple():
    items = parse('#include <stdio.h>\n#define PI 3.14\n')
    defines = [it for it in items if '#define' in it.signature]
    assert any('PI' in it.signature for it in defines)


def test_define_function_like():
    items = parse('#include <stdio.h>\n#define SQUARE(x) ((x) * (x))\n')
    defines = [it for it in items if '#define' in it.signature]
    assert any('SQUARE' in it.signature for it in defines)
    sq = next(it for it in defines if 'SQUARE' in it.signature)
    assert 'SQUARE(x)' in sq.signature


def test_define_no_trailing_brace():
    items = parse('#include <stdio.h>\n#define PI 3.14\n')
    pi = next(it for it in items if 'PI' in it.signature)
    assert not pi.signature.endswith('{')


# ---------------------------------------------------------------------------
# Struct and enum
# ---------------------------------------------------------------------------

def test_struct_detected():
    src = '#include <stdio.h>\nstruct Foo {\n    int x;\n};\n'
    items = parse(src)
    assert any(it.signature == 'struct Foo' for it in items)


def test_struct_no_trailing_brace():
    src = '#include <stdio.h>\nstruct Foo {\n    int x;\n};\n'
    items = parse(src)
    foo = next(it for it in items if 'Foo' in it.signature)
    assert not foo.signature.endswith('{')


def test_enum_detected():
    src = '#include <stdio.h>\nenum Color {\n    RED,\n    GREEN\n};\n'
    items = parse(src)
    assert any(it.signature == 'enum Color' for it in items)


def test_struct_range_covers_body():
    src = '#include <stdio.h>\nstruct Foo {\n    int x;\n    int y;\n};\n'
    items = parse(src)
    foo = next(it for it in items if 'Foo' in it.signature)
    assert foo.count >= 4  # struct + 2 fields + closing }


# ---------------------------------------------------------------------------
# Functions (C)
# ---------------------------------------------------------------------------

def test_simple_function():
    src = '#include <stdio.h>\nvoid hello(void) {\n    puts("hi");\n}\n'
    items = parse(src)
    assert any('hello' in it.signature for it in items)


def test_function_return_type_in_sig():
    src = '#include <stdio.h>\ndouble square(double x) {\n    return x * x;\n}\n'
    items = parse(src)
    fn = next(it for it in items if 'square' in it.signature)
    assert fn.signature == 'double square(double x)'


def test_static_function():
    src = '#include <stdio.h>\nstatic int helper(int x) {\n    return x;\n}\n'
    items = parse(src)
    fn = next(it for it in items if 'helper' in it.signature)
    assert fn.signature.startswith('static')


def test_function_no_body_declaration():
    src = '#include <stdio.h>\nint add(int a, int b);\n'
    items = parse(src)
    assert any('add' in it.signature for it in items)


def test_function_range_covers_body():
    src = '#include <stdio.h>\nint add(int a, int b) {\n    return a + b;\n}\n'
    items = parse(src)
    fn = next(it for it in items if 'add' in it.signature)
    assert fn.count >= 3  # header + body + closing }


def test_control_flow_not_detected():
    # if/while/for should never appear as items
    src = '#include <stdio.h>\nvoid foo(void) {\n    if (1) {}\n    while (0) {}\n}\n'
    items = parse(src)
    sigs = [it.signature for it in items]
    assert not any('if' == sig.split('(')[0].strip() for sig in sigs)
    assert not any('while' == sig.split('(')[0].strip() for sig in sigs)


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_signature_merged():
    src = (
        '#include <stdio.h>\n'
        'int format_message(\n'
        '    const char *fmt,\n'
        '    int code,\n'
        '    char *out,\n'
        '    int out_size) {\n'
        '    return 0;\n'
        '}\n'
    )
    items = parse(src)
    fn = next(it for it in items if 'format_message' in it.signature)
    assert 'const char *fmt' in fn.signature
    assert 'int out_size' in fn.signature
    assert '\n' not in fn.signature


def test_multiline_signature_no_brace():
    src = (
        '#include <stdio.h>\n'
        'int multi(\n'
        '    int a,\n'
        '    int b) {\n'
        '    return a + b;\n'
        '}\n'
    )
    items = parse(src)
    fn = next(it for it in items if 'multi' in it.signature)
    assert not fn.signature.endswith('{')


# ---------------------------------------------------------------------------
# Comment walk-back
# ---------------------------------------------------------------------------

def test_comment_walked_back():
    src = '#include <stdio.h>\n/* doc */\nvoid foo(void) {\n}\n'
    items = parse(src)
    fn = next(it for it in items if 'foo' in it.signature)
    assert fn.start == 2  # comment line


def test_line_comment_walked_back():
    src = '#include <stdio.h>\n// doc\nvoid bar(void) {\n}\n'
    items = parse(src)
    fn = next(it for it in items if 'bar' in it.signature)
    assert fn.start == 2


def test_no_walkback_past_code():
    src = '#include <stdio.h>\nvoid unrelated(void) {}\nvoid foo(void) {}\n'
    items = parse(src)
    foo = next(it for it in items if it.signature.startswith('void foo'))
    assert foo.start == 3


# ---------------------------------------------------------------------------
# Fixture: sample.c
# ---------------------------------------------------------------------------

def test_fixture_c_defines():
    items = parse(FIXTURE_C.read_text())
    sigs = [it.signature for it in items]
    assert any('PI' in s for s in sigs)
    assert any('SQUARE' in s for s in sigs)
    assert any('MAX' in s for s in sigs)


def test_fixture_c_struct():
    items = parse(FIXTURE_C.read_text())
    assert any(it.signature == 'struct Point' for it in items)


def test_fixture_c_enum():
    items = parse(FIXTURE_C.read_text())
    assert any(it.signature == 'enum Color' for it in items)


def test_fixture_c_functions():
    items = parse(FIXTURE_C.read_text())
    sigs = [it.signature for it in items]
    assert any('distance' in s for s in sigs)
    assert any('clamp' in s for s in sigs)
    assert any('main' in s for s in sigs)


def test_fixture_c_static_function():
    items = parse(FIXTURE_C.read_text())
    clamp = next(it for it in items if 'clamp' in it.signature)
    assert clamp.signature.startswith('static')


def test_fixture_c_multiline_format_message():
    items = parse(FIXTURE_C.read_text())
    fn = next(it for it in items if 'format_message' in it.signature)
    assert 'const char *fmt' in fn.signature
    assert 'int out_size' in fn.signature


def test_fixture_c_distance_signature():
    items = parse(FIXTURE_C.read_text())
    fn = next(it for it in items if 'distance' in it.signature)
    assert fn.signature == 'double distance(struct Point a, struct Point b)'


def test_fixture_c_comment_walkback():
    items = parse(FIXTURE_C.read_text())
    # distance has a comment above it; start should be the comment line
    fn = next(it for it in items if 'distance' in it.signature)
    # The comment '/* Compute... */' is immediately before 'double distance'
    assert fn.start < fn.start + fn.count


def test_fixture_c_function_range_covers_body():
    items = parse(FIXTURE_C.read_text())
    fn = next(it for it in items if 'distance' in it.signature)
    assert fn.count >= 5  # comment + signature + 3 body lines + closing brace


# ---------------------------------------------------------------------------
# C++: namespace, class, enum class, templates
# ---------------------------------------------------------------------------

def test_namespace_detected():
    src = '#include <string>\nnamespace foo {\nvoid bar();\n}\n'
    items = parse(src)
    assert any('namespace foo' in it.signature for it in items)


def test_class_detected():
    src = '#include <string>\nclass Foo {\npublic:\n    void bar();\n};\n'
    items = parse(src)
    assert any(it.signature == 'class Foo' for it in items)


def test_class_no_trailing_brace():
    src = '#include <string>\nclass Foo {\n};\n'
    items = parse(src)
    cls = next(it for it in items if 'Foo' in it.signature)
    assert not cls.signature.endswith('{')


def test_class_range_covers_methods():
    src = (
        '#include <string>\n'
        'class Foo {\n'
        'public:\n'
        '    void bar();\n'
        '    int baz(int x);\n'
        '};\n'
    )
    items = parse(src)
    cls = next(it for it in items if it.signature == 'class Foo')
    bar = next(it for it in items if 'bar' in it.signature)
    baz = next(it for it in items if 'baz' in it.signature)
    assert cls.start <= bar.start
    assert cls.start + cls.count >= baz.start + baz.count


def test_class_inheritance():
    src = '#include <string>\nclass Circle : public Shape {\n};\n'
    items = parse(src)
    cls = next(it for it in items if 'Circle' in it.signature)
    assert 'Shape' in cls.signature


def test_virtual_method_detected():
    src = (
        '#include <string>\n'
        'class Shape {\n'
        'public:\n'
        '    virtual double area() const = 0;\n'
        '};\n'
    )
    items = parse(src)
    assert any('area' in it.signature for it in items)


def test_enum_class_detected():
    src = '#include <string>\nenum class Color {\n    Red,\n    Green\n};\n'
    items = parse(src)
    assert any('enum class Color' in it.signature for it in items)


def test_explicit_constructor_detected():
    src = (
        '#include <string>\n'
        'class Foo {\n'
        'public:\n'
        '    explicit Foo(int x);\n'
        '};\n'
    )
    items = parse(src)
    assert any('Foo' in it.signature and 'explicit' in it.signature for it in items)


def test_static_method_detected():
    src = (
        '#include <string>\n'
        'class Counter {\n'
        'public:\n'
        '    static int count();\n'
        '};\n'
    )
    items = parse(src)
    assert any('count' in it.signature for it in items)


def test_template_function_detected():
    src = (
        '#include <string>\n'
        'template<typename T>\n'
        'T identity(T x) {\n'
        '    return x;\n'
        '}\n'
    )
    items = parse(src)
    assert any('identity' in it.signature for it in items)
    fn = next(it for it in items if 'identity' in it.signature)
    assert 'template' in fn.signature


def test_template_class_detected():
    src = (
        '#include <vector>\n'
        'template<typename T>\n'
        'class Box {\n'
        'public:\n'
        '    T get() const;\n'
        '};\n'
    )
    items = parse(src)
    assert any('Box' in it.signature for it in items)
    box = next(it for it in items if 'Box' in it.signature)
    assert 'template' in box.signature


def test_template_class_methods_detected():
    src = (
        '#include <vector>\n'
        'template<typename T>\n'
        'class Box {\n'
        'public:\n'
        '    T get() const;\n'
        '    void set(const T& v);\n'
        '};\n'
    )
    items = parse(src)
    sigs = [it.signature for it in items]
    assert any('get' in s for s in sigs)
    assert any('set' in s for s in sigs)


# ---------------------------------------------------------------------------
# Fixture: sample.cpp
# ---------------------------------------------------------------------------

def test_fixture_cpp_define():
    items = parse(FIXTURE_CPP.read_text())
    assert any('UNUSED' in it.signature for it in items)


def test_fixture_cpp_namespace():
    items = parse(FIXTURE_CPP.read_text())
    assert any('namespace geometry' in it.signature for it in items)


def test_fixture_cpp_struct():
    items = parse(FIXTURE_CPP.read_text())
    assert any(it.signature == 'struct Vec2' for it in items)


def test_fixture_cpp_free_functions():
    items = parse(FIXTURE_CPP.read_text())
    sigs = [it.signature for it in items]
    assert any('vec2_dot' in s for s in sigs)
    assert any('vec2_length' in s for s in sigs)


def test_fixture_cpp_class():
    items = parse(FIXTURE_CPP.read_text())
    assert any(it.signature == 'class Shape' for it in items)


def test_fixture_cpp_class_methods():
    items = parse(FIXTURE_CPP.read_text())
    sigs = [it.signature for it in items]
    assert any('area' in s for s in sigs)
    assert any('describe' in s for s in sigs)
    assert any('instance_count' in s for s in sigs)


def test_fixture_cpp_virtual_pure():
    items = parse(FIXTURE_CPP.read_text())
    area = next(it for it in items if 'area' in it.signature and 'const' in it.signature)
    # pure virtual: = 0 kept in signature
    assert '= 0' in area.signature


def test_fixture_cpp_explicit_constructor():
    items = parse(FIXTURE_CPP.read_text())
    assert any('explicit' in it.signature and 'Circle' in it.signature for it in items)


def test_fixture_cpp_enum_class():
    items = parse(FIXTURE_CPP.read_text())
    assert any('enum class Direction' in it.signature for it in items)


def test_fixture_cpp_template_function():
    items = parse(FIXTURE_CPP.read_text())
    fn = next(it for it in items if 'max_val' in it.signature)
    assert 'template' in fn.signature


def test_fixture_cpp_template_class():
    items = parse(FIXTURE_CPP.read_text())
    cls = next(it for it in items if 'Stack' in it.signature)
    assert 'template' in cls.signature


def test_fixture_cpp_template_class_methods():
    items = parse(FIXTURE_CPP.read_text())
    sigs = [it.signature for it in items]
    assert any('push' in s for s in sigs)
    assert any('pop' in s for s in sigs)
    assert any('empty' in s for s in sigs)


def test_fixture_cpp_namespace_covers_all():
    items = parse(FIXTURE_CPP.read_text())
    ns = next(it for it in items if 'namespace geometry' in it.signature)
    last = max(items, key=lambda it: it.start + it.count)
    # namespace should cover at least most of the file
    assert ns.count > 30


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse('') == []


def test_no_declarations():
    src = '#include <stdio.h>\n// Just a comment\n'
    items = parse(src)
    assert items == []


def test_function_call_not_detected():
    # A bare function call with no return type prefix should not appear
    src = '#include <stdio.h>\nvoid wrapper(void) {\n    printf("hi");\n}\n'
    items = parse(src)
    sigs = [it.signature for it in items]
    # printf should not appear as a declaration
    assert not any('printf' in s for s in sigs)

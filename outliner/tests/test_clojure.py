"""Tests for the Clojure outline parser."""

from pathlib import Path

from outliner.parsers.clojure import parse as _parse, detect as detect_clojure

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "clj"
FIXTURE = FIXTURES / "sample.clj"


# ---------------------------------------------------------------------------
# Extension / content detection
# ---------------------------------------------------------------------------

def test_detect_extension_clj():
    assert guess_syntax("file.clj") == "clojure"


def test_detect_extension_cljs():
    assert guess_syntax("file.cljs") == "clojure"


def test_detect_extension_cljc():
    assert guess_syntax("file.cljc") == "clojure"


def test_detect_content_ns():
    assert detect_clojure(["(ns my.app.core)", "(defn foo [x] x)"])


def test_detect_content_ns_with_require():
    assert detect_clojure(["(ns my.app", "  (:require [clojure.string :as str]))"])


def test_detect_content_defn_and_def():
    # defn + def together (no ns) is still Clojure
    assert detect_clojure(["(defn foo [x] x)", "(def bar 42)"])


def test_detect_content_defn_alone_not_triggered():
    # defn alone is not enough — could be a snippet
    assert not detect_clojure(["(defn foo [x] x)"])


def test_detect_content_no_match():
    assert not detect_clojure(["Hello world", "No code here"])


def test_detect_content_python_not_triggered():
    assert not detect_clojure(["def foo():", "    pass"])


def test_detect_registry_clojure_content():
    assert detect(FIXTURE.read_text()) == "clojure"


# ---------------------------------------------------------------------------
# Signature format — defn
# ---------------------------------------------------------------------------

def test_simple_defn_signature():
    items = parse("(defn foo [x y]\n  (+ x y))\n")
    assert len(items) == 1
    assert items[0].signature == "(defn foo [x y])"


def test_defn_docstring_not_in_sig():
    items = parse('(defn greet\n  "Hello doc."\n  [name]\n  (str "Hi " name))\n')
    assert len(items) == 1
    assert "Hello doc" not in items[0].signature
    assert items[0].signature == "(defn greet [name])"


def test_defn_params_included_in_sig():
    items = parse("(defn add [x y]\n  (+ x y))\n")
    assert "[x y]" in items[0].signature


def test_defn_no_trailing_paren_body():
    # Signature should end with ) closing the sig, not extend into body
    items = parse("(defn foo [x]\n  (* x x))\n")
    assert items[0].signature == "(defn foo [x])"


def test_defn_private():
    items = parse("(defn- helper [x]\n  (* x 2))\n")
    assert items[0].signature == "(defn- helper [x])"


def test_async_not_confused():
    # No special treatment needed; just verify normal defn works
    items = parse("(defn process [data]\n  data)\n")
    assert items[0].signature == "(defn process [data])"


# ---------------------------------------------------------------------------
# Multi-line signatures
# ---------------------------------------------------------------------------

def test_multiline_vector_merged():
    src = "(defn f\n  [arg1 arg2\n   arg3]\n  arg1)\n"
    items = parse(src)
    assert len(items) == 1
    sig = items[0].signature
    assert "arg1" in sig
    assert "arg2" in sig
    assert "arg3" in sig
    assert sig == "(defn f [arg1 arg2 arg3])"


def test_multiarity_sig_is_name_only():
    src = "(defn multi\n  ([x] x)\n  ([x y] (+ x y)))\n"
    items = parse(src)
    assert items[0].signature == "(defn multi)"


# ---------------------------------------------------------------------------
# Other top-level forms
# ---------------------------------------------------------------------------

def test_ns_form_included():
    items = parse("(ns my.app\n  (:require [clojure.string :as str]))\n")
    assert any("ns" in it.signature for it in items)
    assert items[0].signature == "(ns my.app)"


def test_def_form_included():
    items = parse("(defn foo [x] x)\n(def PI 3.14159)\n")
    assert any("PI" in it.signature for it in items)


def test_def_simple_value():
    items = parse("(def answer 42)\n")
    assert items[0].signature == "(def answer 42)"


def test_defmacro_signature():
    items = parse("(defmacro my-when [test & body]\n  `(if ~test (do ~@body)))\n")
    assert items[0].signature == "(defmacro my-when [test & body])"


def test_defrecord_signature():
    items = parse("(defrecord Point [x y])\n")
    assert items[0].signature == "(defrecord Point [x y])"


def test_deftype_signature():
    items = parse("(deftype Box [w h]\n  Object\n  (toString [_] (str w h)))\n")
    assert items[0].signature == "(deftype Box [w h])"


def test_defprotocol_signature():
    items = parse("(defprotocol Drawable\n  (draw [this])\n  (area [this]))\n")
    assert items[0].signature == "(defprotocol Drawable)"


def test_defmulti_signature():
    items = parse("(defmulti greet :language)\n")
    assert items[0].signature == "(defmulti greet :language)"


# ---------------------------------------------------------------------------
# Comment walk-back
# ---------------------------------------------------------------------------

def test_comment_walked_back():
    src = ";; Do something.\n(defn foo [x]\n  x)\n"
    items = parse(src)
    assert items[0].start == 1
    assert items[0].count == 3


def test_blank_stops_walkback():
    src = ";; Unrelated comment.\n\n(defn foo [x]\n  x)\n"
    items = parse(src)
    assert items[0].start == 3


def test_no_walkback_past_code():
    src = "(def x 1)\n(defn foo [y]\n  y)\n"
    items = parse(src)
    foo = next(it for it in items if "foo" in it.signature)
    assert foo.start == 2


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_single_line_form_range():
    items = parse("(def PI 3.14)\n")
    assert items[0].start == 1
    assert items[0].count == 1


def test_multiline_defn_range():
    src = "(defn foo [x]\n  (* x x))\n"
    items = parse(src)
    assert items[0].count == 2


def test_deftype_range_covers_body():
    src = "(deftype Box [w h]\n  Object\n  (toString [_] \"\"))\n"
    items = parse(src)
    assert items[0].count == 3


# ---------------------------------------------------------------------------
# Exclusions
# ---------------------------------------------------------------------------

def test_defonce_excluded():
    # defonce is not in the listed forms
    items = parse("(defonce state (atom {}))\n")
    assert items == []


def test_let_binding_not_top_level():
    # (defn inside let at top level of file is still a top-level line)
    # Only match forms starting at column 0 with no indentation
    items = parse("  (defn foo [x] x)\n")
    assert items == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_only_comments():
    assert parse(";; Just a comment\n;; another line\n") == []


def test_string_with_parens_not_counted():
    # Parens inside string literals must not confuse depth tracking
    items = parse('(defn msg []\n  "(hello) world")\n')
    assert len(items) == 1
    assert items[0].count == 2


# ---------------------------------------------------------------------------
# Fixture tests
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse(FIXTURE.read_text())
    assert len(items) == 12


def test_fixture_ns_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(ns outliner.sample)" for it in items)


def test_fixture_ns_start_and_count():
    items = parse(FIXTURE.read_text())
    ns = next(it for it in items if "ns" in it.signature)
    assert ns.start == 3
    assert ns.count == 2


def test_fixture_def_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(def max-size 100)" for it in items)


def test_fixture_def_start():
    items = parse(FIXTURE.read_text())
    defv = next(it for it in items if "max-size" in it.signature)
    assert defv.start == 6
    assert defv.count == 1


def test_fixture_greet_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(defn greet [name])" for it in items)


def test_fixture_greet_start_and_count():
    items = parse(FIXTURE.read_text())
    greet = next(it for it in items if "greet" in it.signature)
    assert greet.start == 8
    assert greet.count == 5


def test_fixture_add_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(defn add [x y])" for it in items)


def test_fixture_complex_fn_multiline_sig():
    items = parse(FIXTURE.read_text())
    fn = next(it for it in items if "complex-fn" in it.signature)
    assert fn.signature == "(defn complex-fn [arg1 arg2 arg3])"
    assert fn.start == 19
    assert fn.count == 6


def test_fixture_my_fn_multiarity():
    items = parse(FIXTURE.read_text())
    fn = next(it for it in items if "my-fn" in it.signature)
    assert fn.signature == "(defn my-fn)"
    assert fn.start == 26
    assert fn.count == 6


def test_fixture_private_fn_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(defn- private-fn [x])" for it in items)


def test_fixture_defmacro_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(defmacro when-positive [n & body])" for it in items)


def test_fixture_defmacro_start_and_count():
    items = parse(FIXTURE.read_text())
    m = next(it for it in items if "when-positive" in it.signature)
    assert m.start == 38
    assert m.count == 4


def test_fixture_defrecord_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(defrecord Person [name age])" for it in items)


def test_fixture_defrecord_start():
    items = parse(FIXTURE.read_text())
    r = next(it for it in items if "Person" in it.signature)
    assert r.start == 43
    assert r.count == 1


def test_fixture_deftype_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(deftype Point [x y])" for it in items)


def test_fixture_deftype_start_and_count():
    items = parse(FIXTURE.read_text())
    t = next(it for it in items if "Point" in it.signature)
    assert t.start == 45
    assert t.count == 4


def test_fixture_defprotocol_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(defprotocol Shape)" for it in items)


def test_fixture_defprotocol_start_and_count():
    items = parse(FIXTURE.read_text())
    p = next(it for it in items if "Shape" in it.signature)
    assert p.start == 50
    assert p.count == 4


def test_fixture_defmulti_signature():
    items = parse(FIXTURE.read_text())
    assert any(it.signature == "(defmulti describe :type)" for it in items)


def test_fixture_defmulti_start():
    items = parse(FIXTURE.read_text())
    m = next(it for it in items if "describe" in it.signature)
    assert m.start == 55
    assert m.count == 1


def test_fixture_no_import_like_entries():
    # No :require forms should appear as items
    items = parse(FIXTURE.read_text())
    assert all(":require" not in it.signature for it in items)


# ---------------------------------------------------------------------------
# Review-identified edge cases
# ---------------------------------------------------------------------------

def test_def_with_vector_value():
    # Vector literal as def value — param-vector stop must not fire for def
    items = parse("(def coords [10 20 30])\n")
    assert items[0].signature == "(def coords [10 20 30])"


def test_def_with_string_scalar():
    # String value is stripped but form is still found
    items = parse('(def greeting "hello")\n')
    assert len(items) == 1
    assert "greeting" in items[0].signature


def test_defn_type_hint_kept_in_sig():
    # ^Type hints (non-map) are informative and should stay in the signature
    items = parse("(defn ^String shout [s]\n  (.toUpperCase s))\n")
    assert "^String" in items[0].signature
    assert items[0].signature == "(defn ^String shout [s])"


def test_defn_caret_map_metadata_stripped():
    # ^{:added "1.0"} reader-macro metadata must be stripped from the sig
    src = '(defn my-fn\n  ^{:added "1.0"}\n  [x]\n  x)\n'
    items = parse(src)
    assert len(items) == 1
    assert ":added" not in items[0].signature
    assert "[x]" in items[0].signature


def test_character_literal_paren_in_body():
    # \( and \) are Clojure character literals, not real parens;
    # the form range must not bleed into the next top-level form.
    src = "(defn f [] \\()\n(def x 1)\n"
    items = parse(src)
    assert len(items) == 2
    f = next(it for it in items if "f" in it.signature)
    x = next(it for it in items if "x" in it.signature)
    assert f.count == 1
    assert x.start == 2


def test_defmethod_excluded():
    # defmethod is not in the listed forms and must not appear
    items = parse("(defmethod area :circle [r]\n  (* Math/PI r r))\n")
    assert items == []

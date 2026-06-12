"""Tests for the JSON / NDJSON outline parser."""

import io
import json
from pathlib import Path

from outliner.parsers.json import detect as detect_json, read as json_read
from outliner.cli import guess_syntax
from outliner.types import OutlineItem

FIXTURES = Path(__file__).parent / "fixtures" / "json"


def _read(text: str) -> list[OutlineItem]:
    return list(json_read(io.StringIO(text)))


# ---------------------------------------------------------------------------
# Extension detection
# ---------------------------------------------------------------------------

def test_detect_extension_json():
    assert guess_syntax("file.json") == "json"


def test_detect_extension_jsonl():
    assert guess_syntax("file.jsonl") == "json"


def test_detect_extension_ndjson():
    assert guess_syntax("file.ndjson") == "json"


# ---------------------------------------------------------------------------
# Content detection (NDJSON only)
# ---------------------------------------------------------------------------

def test_detect_ndjson():
    assert detect_json(['{"a": 1}', '{"b": 2}', '{"c": 3}'])


def test_detect_ndjson_mixed_with_empty():
    assert detect_json(["", '{"a": 1}', "  ", '{"b": 2}'])


def test_detect_ndjson_not_triggered_by_non_json():
    assert not detect_json(["hello", "world"])


def test_detect_ndjson_not_triggered_by_partial_json():
    assert not detect_json(['{"a": 1}', "garbage"])


def test_detect_ndjson_empty():
    assert not detect_json([])
    assert not detect_json(["", "  "])



# ---------------------------------------------------------------------------
# Single-doc object
# ---------------------------------------------------------------------------

def test_single_object_basic():
    items = _read('{"name": "Widget", "count": 42, "active": true}')
    sigs = {it.locator: it.signature for it in items}
    assert sigs["$"].startswith("47 B · json · object")
    assert sigs[".active"] == "bool -- true"
    assert sigs[".count"] == "int -- 42"
    assert sigs[".name"] == 'str -- "Widget"'


def test_single_object_float():
    items = _read('{"price": 12.5}')
    assert items[1].signature == "float -- 12.5"


def test_single_object_null_treated_as_absent():
    items = _read('{"a": 1, "b": null}')
    sigs = {it.locator: it.signature for it in items}
    assert ".b" not in sigs


def test_single_object_optional_field():
    items = _read(
        '{"name": "x", "age": 30}\n'
        '{"name": "y"}'
    )
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".name"] == 'str -- "x"'
    assert sigs[".age"] == "int? -- 30"


def test_single_object_empty():
    items = _read("{}")
    assert len(items) == 1
    assert items[0].locator == "$"
    assert "object" in items[0].signature


# ---------------------------------------------------------------------------
# Single-doc array
# ---------------------------------------------------------------------------

def test_single_array_of_objects():
    items = _read('[{"x": 1}, {"x": 2, "y": "hi"}]')
    sigs = {it.locator: it.signature for it in items}
    assert "array[2]" in sigs["$"]
    assert sigs[".x"] == "int -- 1"
    assert sigs[".y"] == "str? -- \"hi\""


def test_single_array_of_scalars():
    items = _read('[1, 2, 3]')
    assert len(items) == 1
    assert "array[3]" in items[0].signature


def test_single_array_empty():
    items = _read("[]")
    assert len(items) == 1
    assert "array[0]" in items[0].signature


def test_single_array_mixed_scalars():
    items = _read('[1, "two", 3, null]')
    assert "array[4]" in items[0].signature


# ---------------------------------------------------------------------------
# Single-doc scalar root
# ---------------------------------------------------------------------------

def test_single_scalar():
    items = _read("42")
    assert items[0].signature.endswith(" · int")


def test_single_scalar_string():
    items = _read('"hello"')
    assert items[0].signature.endswith(" · str")


def test_single_scalar_bool():
    items = _read("true")
    assert items[0].signature.endswith(" · bool")


def test_single_scalar_null():
    items = _read("null")
    assert items[0].signature.endswith(" · null")


# ---------------------------------------------------------------------------
# NDJSON
# ---------------------------------------------------------------------------

def test_ndjson_basic():
    items = _read('{"a": 1}\n{"a": 2, "b": "x"}\n')
    sigs = {it.locator: it.signature for it in items}
    assert sigs["$"] == "28 B · ndjson · sampled 2 of 2 records"
    assert sigs[".a"] == "int -- 1"
    assert sigs[".b"] == 'str? -- "x"'


def test_ndjson_header_estimates_when_sample_limit_hit(monkeypatch):
    import outliner.parsers.json as json_parser

    monkeypatch.setattr(json_parser, "NDJSON_SAMPLE", 2)
    items = _read('{"a": 1}\n{"a": 2}\n{"a": 3}\n')
    sigs = {it.locator: it.signature for it in items}
    assert sigs["$"] == "27 B · ndjson · sampled 2 of ~3 records"


def test_ndjson_single_line():
    # Single-line object: ambiguous between NDJSON and single-doc.
    # Detected as single-doc object (no second line to confirm NDJSON).
    items = _read('{"a": 1}\n')
    sigs = {it.locator: it.signature for it in items}
    assert "object" in sigs["$"]
    assert sigs[".a"] == "int -- 1"


# ---------------------------------------------------------------------------
# Nested objects
# ---------------------------------------------------------------------------

def test_nested_object():
    items = _read('{"user": {"name": "Alice", "age": 30}}')
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".user"] == "object"
    assert sigs[".user.age"] == "int -- 30"
    assert sigs[".user.name"] == 'str -- "Alice"'


def test_nested_object_optional():
    items = _read(
        '[{"meta": {"ver": 1}}, {"x": 1}]'
    )
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".meta"] == "object?"
    assert sigs[".meta.ver"] == "int? -- 1"


# ---------------------------------------------------------------------------
# Arrays of objects
# ---------------------------------------------------------------------------

def test_array_of_objects():
    items = _read('{"items": [{"id": 1, "label": "A"}, {"id": 2}]}')
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".items[]"] == "array"
    assert sigs[".items[].id"] == "int -- 1"
    assert sigs[".items[].label"] == 'str? -- "A"'


# ---------------------------------------------------------------------------
# Arrays of scalars
# ---------------------------------------------------------------------------

def test_array_of_strings():
    items = _read('{"tags": ["red", "green", "blue"]}')
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".tags[]"] == 'array[str] -- ["red", "green", "blue"]'


def test_array_of_ints():
    items = _read('{"scores": [10, 20, 30]}')
    # items[0] = $ summary, items[1] = .scores[]
    assert items[1].locator == ".scores[]"
    assert items[1].signature == "array[int] -- [10, 20, 30]"


def test_array_of_mixed_scalars():
    items = _read('{"vals": [1, "two", 3]}')
    assert items[1].locator == ".vals[]"
    assert items[1].signature == 'array[int|str] -- [1, "two", 3]'


def test_array_of_scalars_empty():
    items = _read('{"empty": []}')
    assert any(it.locator == ".empty[]" for it in items)
    assert any("array" in it.signature for it in items if it.locator == ".empty[]")


# ---------------------------------------------------------------------------
# Type handling
# ---------------------------------------------------------------------------

def test_bool_recognized():
    items = _read('{"flag": true}')
    assert items[1].signature == "bool -- true"


def test_null_type_not_shown():
    items = _read('{"a": null, "b": 1}')
    sigs = {it.locator: it.signature for it in items}
    assert ".a" not in sigs


def test_mixed_types():
    items = _read(
        '[{"val": 1}, {"val": "two"}, {"val": 3}]'
    )
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".val"] == "int|str -- 1"


# ---------------------------------------------------------------------------
# Sample truncation
# ---------------------------------------------------------------------------

def test_long_string_truncated():
    text = json.dumps({"desc": "x" * 50})
    items = _read(text)
    sig = items[1].signature
    assert sig.endswith('"')
    assert "…" in sig
    assert len(sig) <= 40 + len("str -- ")


def test_short_string_not_truncated():
    text = json.dumps({"name": "hi"})
    items = _read(text)
    assert "…" not in items[1].signature


# ---------------------------------------------------------------------------
# Scalars before containers
# ---------------------------------------------------------------------------

def test_scalars_before_containers():
    items = _read('{"z": 1, "a": {"x": 2}, "b": [3], "y": 4}')
    locs = [it.locator for it in items if it.locator != "$"]
    scalar_idx = {locs.index(l) for l in locs if l in (".y", ".z")}
    container_idx = {locs.index(l) for l in locs if l in (".a", ".b[]")}
    assert max(scalar_idx) < min(container_idx)


# ---------------------------------------------------------------------------
# Depth-first traversal
# ---------------------------------------------------------------------------

def test_depth_first():
    items = _read('{"a": {"x": 1, "y": 2}, "b": {"z": 3}}')
    locs = [it.locator for it in items if it.locator != "$"]
    # .a, its children .a.x .a.y, then .b and its child .b.z
    assert locs.index(".a.x") < locs.index(".b")
    assert locs.index(".a.y") < locs.index(".b")


# ---------------------------------------------------------------------------
# locator and fmt_width
# ---------------------------------------------------------------------------

def test_locator_set_on_items():
    items = _read('{"key": "val"}')
    assert items[0].locator == "$"
    assert items[1].locator == ".key"


def test_fmt_width_from_locator():
    items = _read('{"name": "x"}')
    assert items[0].fmt_width == 1  # "$"
    assert items[1].fmt_width == len(".name")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_input():
    assert _read("") == []
    assert _read("   \n  ") == []


def test_invalid_json():
    assert _read("not json") == []


def test_leading_blank_line():
    items = _read('\n{"a": 1}\n')
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".a"] == "int -- 1"


def test_utf8_bom():
    items = _read('\ufeff{"a": 1}')
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".a"] == "int -- 1"


def test_ndjson_blank_line_between_records():
    items = _read('{"a": 1}\n\n{"b": 2}\n')
    sigs = {it.locator: it.signature for it in items}
    assert "ndjson" in sigs["$"]
    assert sigs[".a"] == "int? -- 1"
    assert sigs[".b"] == "int? -- 2"


def test_ndjson_of_arrays():
    items = _read('[1, 2]\n[3, 4]\n')
    sigs = {it.locator: it.signature for it in items}
    assert "ndjson" in sigs["$"]
    assert sigs["[]"] == "array[int] -- [1, 2]"


def test_ndjson_malformed_line_skipped():
    items = _read('{"a": 1}\n{"a": 2}\nnot json\n{"a": 3}\n')
    sigs = {it.locator: it.signature for it in items}
    assert "sampled 3 of 3 records" in sigs["$"]
    assert sigs[".a"] == "int -- 1"


def test_deeply_nested_no_crash():
    # Schema recursion aborts gracefully; only the $ summary remains.
    items = _read("[" * 3000 + "]" * 3000)
    assert [it.locator for it in items] == ["$"]


def test_doc_larger_than_head_parsed(monkeypatch):
    import outliner.parsers.json as json_parser

    monkeypatch.setattr(json_parser, "HEAD_LIMIT", 64)
    items = _read(json.dumps({"alpha": 1, "beta": [1, 2], "gamma": {"x": "y"}}, indent=2))
    sigs = {it.locator: it.signature for it in items}
    assert "json · object" in sigs["$"]
    assert sigs[".alpha"] == "int -- 1"
    assert sigs[".gamma.x"] == 'str -- "y"'


def test_large_pretty_printed_object():
    data = {f"key{i:04d}": "x" * 10 for i in range(3000)}
    items = _read(json.dumps(data, indent=2))
    sigs = {it.locator: it.signature for it in items}
    assert "json · object" in sigs["$"]
    assert sigs[".key0000"] == 'str -- "xxxxxxxxxx"'


def test_oversize_doc_not_parsed(monkeypatch):
    import outliner.parsers.json as json_parser

    monkeypatch.setattr(json_parser, "HEAD_LIMIT", 64)
    monkeypatch.setattr(json_parser, "LOAD_LIMIT", 100)
    items = _read(json.dumps({f"k{i}": i for i in range(50)}, indent=2))
    assert len(items) == 1
    assert items[0].locator == "$"
    assert "json · object · not parsed" in items[0].signature


def test_deeply_nested():
    nested = {"l" + str(i): {"l" + str(i + 1): "v"} for i in range(5)}
    nested["l4"] = {"leaf": 1}
    text = json.dumps(nested)
    items = _read(text)
    assert any(it.locator == ".l4.leaf" for it in items)


# ---------------------------------------------------------------------------
# Fixture-based tests
# ---------------------------------------------------------------------------

def test_fixture_object():
    items = _read((FIXTURES / "object.json").read_text())
    sigs = {it.locator: it.signature for it in items}
    assert "json · object" in sigs["$"]
    assert sigs[".name"] == 'str -- "Widget"'
    assert sigs[".price"] == "float -- 12.5"
    assert sigs[".count"] == "int -- 42"
    assert sigs[".active"] == "bool -- true"
    assert ".desc" not in sigs
    assert sigs[".tags[]"] == 'array[str] -- ["red", "green"]'


def test_fixture_array():
    items = _read((FIXTURES / "array.json").read_text())
    sigs = {it.locator: it.signature for it in items}
    assert "array[2]" in sigs["$"]
    assert sigs[".id"] == "int -- 1"
    assert sigs[".label"] == 'str -- "A"'
    assert sigs[".color"] == "str? -- \"blue\""


def test_fixture_ndjson():
    items = _read((FIXTURES / "ndjson.json").read_text())
    sigs = {it.locator: it.signature for it in items}
    assert "ndjson" in sigs["$"]
    assert sigs[".city"] == 'str -- "Oslo"'
    assert sigs[".temp"] == "int -- 15"
    assert sigs[".rain"] == "bool? -- true"


def test_fixture_nested():
    items = _read((FIXTURES / "nested.json").read_text())
    sigs = {it.locator: it.signature for it in items}
    assert sigs[".user"] == "object"
    assert sigs[".user.name"] == 'str -- "Alice"'
    assert sigs[".user.age"] == "int -- 30"
    assert sigs[".order"] == "object"
    assert sigs[".order.items[]"] == "array"
    assert sigs[".order.items[].sku"] == 'str -- "X1"'
    assert sigs[".order.items[].qty"] == "int -- 2"
    assert sigs[".order.total"] == "float -- 99.5"
    assert ".order.meta" not in sigs


def test_fixture_ndjson_detect_from_content():
    text = (FIXTURES / "ndjson.json").read_text()
    assert detect_json(text.splitlines()) is True


def test_fixture_array_detect_from_content():
    text = (FIXTURES / "array.json").read_text()
    # Single-doc array is not detected by content (only NDJSON is)
    assert detect_json(text.splitlines()) is False

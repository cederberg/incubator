"""Tests for the XML outline parser."""

import io
from pathlib import Path

from outliner.cli import guess_syntax
from outliner.parsers import detect
from outliner.parsers.xml import detect as detect_xml, read as xml_read
from outliner.types import OutlineItem

FIXTURES = Path(__file__).parent / "fixtures" / "xml"


def _read(text: str) -> list[OutlineItem]:
    return list(xml_read(io.StringIO(text)))


# ---------------------------------------------------------------------------
# Extension and content detection
# ---------------------------------------------------------------------------

def test_detect_extension_xml():
    assert guess_syntax("file.xml") == "xml"


def test_detect_xml_declaration():
    assert detect_xml(['<?xml version="1.0"?>', "<root/>"])


def test_detect_xml_tag_is_conservative():
    assert not detect_xml(["<root><item /></root>"])


def test_detect_not_html():
    assert not detect_xml(["<!doctype html>", "<html></html>"])
    assert not detect_xml(["<html>", "<body></body>"])
    assert detect("<body><h1>x</h1></body>") != "xml"


def test_detect_content_registry():
    assert detect("<?xml version='1.0'?>\n<root/>\n") == "xml"


# ---------------------------------------------------------------------------
# Structural output
# ---------------------------------------------------------------------------

def test_basic_xml_schema():
    items = list(xml_read((FIXTURES / "basic.xml").open()))
    sigs = {it.locator: it.signature for it in items}
    assert sigs["/"].endswith(" · xml · sampled 8 elems")
    assert sigs["<library>"] == "elem"
    assert sigs["  <book>"] == "elem+"
    assert sigs["    @id"] == 'attr -- "1"'
    assert sigs["    @lang"] == 'attr? -- "en"'
    assert sigs["    <title>"] == 'text -- "One"'
    assert sigs["    <author>"] == 'text? -- "Alice"'
    assert sigs["    <summary>"] == 'mixed? -- "text"'
    assert sigs["      <b>"] == 'text -- "Bold"'


def test_attributes_before_children():
    items = list(xml_read((FIXTURES / "basic.xml").open()))
    locs = [it.locator for it in items]
    assert locs.index("    @id") < locs.index("    <title>")
    assert locs.index("    @lang") < locs.index("    <title>")


def test_namespaced_names_preserve_prefixes():
    items = list(xml_read((FIXTURES / "namespaced.xml").open()))
    sigs = {it.locator: it.signature for it in items}
    assert sigs["<feed>"] == "elem"
    assert sigs["  <atom:entry>"] == "elem"
    assert sigs["    @xml:lang"] == 'attr -- "en"'
    assert sigs["    <atom:title>"] == 'text -- "Hello"'
    assert all("xmlns" not in it.locator for it in items)


def test_deep_locators_keep_parent_context_with_indentation():
    items = list(xml_read((FIXTURES / "deep.xml").open()))
    rows = [(it.locator, it.signature) for it in items]
    assert ("        <name>", 'text -- "First"') in rows
    assert ("        <name>", 'text -- "Second"') in rows


def test_mixed_content():
    items = _read("<p>Hello <b>bold</b> tail</p>")
    sigs = {it.locator: it.signature for it in items}
    assert sigs["<p>"] == 'mixed -- "Hello tail"'
    assert sigs["  <b>"] == 'text -- "bold"'


def test_repeated_optional_element_uses_star():
    items = _read("<root><item><tag>a</tag><tag>b</tag></item><item /></root>")
    sigs = {it.locator: it.signature for it in items}
    assert sigs["  <item>"] == "elem+"
    assert sigs["    <tag>"] == 'text* -- "a"'


def test_stream_summary_omits_size():
    items = _read("<root><child /></root>")
    assert items[0].locator == "/"
    assert items[0].signature == "xml · sampled 2 elems"


def test_invalid_xml_emits_partial_outline():
    # Mismatched close tag: structure sampled up to the error is kept
    items = list(xml_read((FIXTURES / "invalid.xml").open()))
    sigs = {it.locator: it.signature for it in items}
    assert "sampled 2 of ~2 elems" in sigs["/"]
    assert sigs["<root>"] == "elem"
    assert sigs["  <item>"] == "elem"


def test_garbage_input_returns_empty():
    assert _read("not xml at all") == []
    assert _read("") == []


def test_truncated_doc_emits_partial_outline():
    text = "<root>" + "<item><name>x</name></item>" * 20 + "<item><na"
    items = _read(text)
    sigs = {it.locator: it.signature for it in items}
    assert "sampled" in sigs["/"] and "+" in sigs["/"]
    assert sigs["  <item>"] == "elem+"
    # the cut-off final <item> has no <name>, so it samples as optional
    assert sigs["    <name>"] == 'text? -- "x"'


def test_junk_after_root_keeps_first_doc():
    items = _read("<a><b>1</b></a>\n<a><b>2</b></a>\n")
    sigs = {it.locator: it.signature for it in items}
    assert sigs["<a>"] == "elem"
    assert sigs["  <b>"] == 'text -- "1"'


def test_deeply_nested_no_crash():
    text = "".join(f"<e{i}>" for i in range(5000)) + "".join(
        f"</e{i}>" for i in reversed(range(5000)))
    items = _read(text)
    locs = [it.locator for it in items]
    assert "<e0>" in locs
    # depth capped at MAX_DEPTH; deeper elements are skipped
    assert len(items) == 1 + 64


def test_huge_attr_sample_truncated():
    items = _read('<root><item name="' + "x" * 10_000 + '"/></root>')
    attr = next(it for it in items if it.locator.endswith("@name"))
    assert attr.signature.startswith("attr -- ")
    assert len(attr.signature) < 60


def test_estimate_when_element_cap_hit(monkeypatch, tmp_path):
    import outliner.parsers.xml as xml_parser

    monkeypatch.setattr(xml_parser, "MAX_START_ELEMENTS", 10)
    path = tmp_path / "many.xml"
    path.write_text("<root>" + "<item>v</item>" * 100 + "</root>")
    items = list(xml_read(path.open()))
    assert "sampled 10 of ~" in items[0].signature


def test_sampling_stops_at_start_element_cap(monkeypatch):
    import outliner.parsers.xml as xml

    monkeypatch.setattr(xml, "MAX_START_ELEMENTS", 2)
    monkeypatch.setattr(xml, "MAX_SECONDS", 100)
    items = _read("<root><a/><b/><c/></root>")
    locs = [it.locator for it in items]
    assert "<root>" in locs
    assert "  <a>" in locs
    assert "  <b>" not in locs


def test_fmt_width_from_locator():
    items = _read("<root><child>v</child></root>")
    assert items[0].fmt_width == 1
    assert items[1].fmt_width == len("<root>")

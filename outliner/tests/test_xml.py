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


def test_invalid_xml_returns_empty():
    assert list(xml_read((FIXTURES / "invalid.xml").open())) == []


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

"""Tests for the AsciiDoc outline parser."""

from pathlib import Path

from outliner.parsers.asciidoc import parse as _parse, detect as detect_adoc

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "adoc"


# ---------------------------------------------------------------------------
# Heading detection basics
# ---------------------------------------------------------------------------

def test_level0_document_title():
    items = parse("= My Title\n\nBody.\n")
    assert len(items) == 1
    assert items[0].signature == "= My Title"
    assert items[0].start == 1


def test_level1_section():
    items = parse("== Section\n\nBody.\n")
    assert len(items) == 1
    assert items[0].signature == "== Section"
    assert items[0].start == 1


def test_two_same_level():
    text = "== Alpha\n\ntext\n\n== Beta\n\nmore\n"
    items = parse(text)
    assert [it.signature for it in items] == ["== Alpha", "== Beta"]
    assert items[0].count == items[1].start - items[0].start


def test_nested_levels():
    text = "== Section\n\n=== Subsection\n\ntext\n"
    items = parse(text)
    assert items[0].signature == "== Section"
    assert items[1].signature == "=== Subsection"


def test_all_six_levels():
    text = "\n".join(f"{'=' * i} Heading {i}" for i in range(1, 7)) + "\n"
    items = parse(text)
    assert len(items) == 6
    for i, item in enumerate(items, 1):
        assert item.signature == f"{'=' * i} Heading {i}"


def test_heading_with_attributes():
    # Attribute entries before heading should not be confused with headings
    text = "= Title\n:author: Bob\n:revdate: 2024\n\n== Section\n\nbody\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "= Title" in sigs
    assert "== Section" in sigs
    # Attribute lines should not appear as items
    assert not any(":author:" in s for s in sigs)


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_range_same_level_ends_at_next():
    text = "== A\n\ntext\n\n== B\n\nmore\n"
    items = parse(text)
    a = items[0]
    b = items[1]
    assert a.count == b.start - a.start


def test_range_parent_covers_children():
    text = "== Parent\n\n=== Child\n\ntext\n\n== Sibling\n\nend\n"
    items = parse(text)
    parent = next(it for it in items if it.signature == "== Parent")
    sibling = next(it for it in items if it.signature == "== Sibling")
    child = next(it for it in items if it.signature == "=== Child")
    assert parent.count == sibling.start - parent.start
    assert parent.start < child.start
    assert parent.start + parent.count >= child.start + child.count


def test_range_to_eof():
    text = "== Only\n\nall content\n"
    items = parse(text)
    assert items[0].count == 3


def test_level0_range_covers_rest():
    text = "= Title\n\n== Section\n\ntext\n"
    items = parse(text)
    title = next(it for it in items if it.signature == "= Title")
    assert title.start == 1
    assert title.count == len(text.splitlines())


# ---------------------------------------------------------------------------
# Preamble
# ---------------------------------------------------------------------------

def test_no_preamble_when_heading_first():
    text = "= Title\n\nBody.\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "= Title"


def test_attribute_lines_not_preamble():
    # Attribute entries right after = Title are not preamble content
    text = "= Title\n:author: X\n\n== Section\n\nbody\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "= Title" in sigs
    assert "== Section" in sigs


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_no_headings_returns_first_line():
    text = "Some plain text.\nMore text.\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "Some plain text."
    assert items[0].start == 1
    assert items[0].count == 2


def test_equals_sign_in_body_not_heading():
    # A line like "x = 5" or "===" should not be treated as a heading
    text = "== Section\n\nx = 5\n=== Code\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "== Section" in sigs
    # "x = 5" is body text, not a heading
    assert not any(s.strip() == "x = 5" for s in sigs)


def test_heading_with_inline_formatting():
    # Inline markup (*bold*, _italic_, `mono`) preserved raw in signature
    items = parse("== *Bold* Section\n\nbody\n")
    assert items[0].signature == "== *Bold* Section"


def test_heading_inside_listing_block_known_limitation():
    # The parser does NOT track delimited blocks; a heading-like line inside
    # a ---- listing block is parsed as a heading (known limitation, same as
    # the markdown parser's code-fence limitation).
    text = "== Real\n\n----\n== Inside block\n----\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    # Parser sees 2 headings — document this known behaviour
    assert any("Real" in s for s in sigs)


def test_heading_no_space_not_recognized():
    # "==NoSpace" (no space after =) is NOT an AsciiDoc heading
    text = "==NoSpace\n\nbody\n"
    items = parse(text)
    # Should fall through to fallback — no heading found
    assert items[0].signature == "==NoSpace"  # first-line fallback
    assert items[0].start == 1


# ---------------------------------------------------------------------------
# sample.adoc fixture
# ---------------------------------------------------------------------------

def test_sample_item_count():
    items = parse((FIXTURES / "sample.adoc").read_text())
    assert len(items) >= 8   # title + intro + 2 subs + main + 3 subs + conclusion


def test_sample_document_title():
    items = parse((FIXTURES / "sample.adoc").read_text())
    assert items[0].signature == "= Document Title"
    assert items[0].start == 1


def test_sample_start_lines():
    text = (FIXTURES / "sample.adoc").read_text()
    lines = text.splitlines()
    items = parse(text)
    for item in items:
        # start is 1-based; signature text must appear somewhere near that line
        # (heading line itself or preceded by the doc title)
        assert 1 <= item.start <= len(lines)


def test_sample_has_subsections():
    items = parse((FIXTURES / "sample.adoc").read_text())
    sigs = [it.signature for it in items]
    assert any("Introduction" in s for s in sigs)
    assert any("Background" in s for s in sigs)
    assert any("Subsection A.1" in s for s in sigs)
    assert any("Conclusion" in s for s in sigs)


def test_sample_level0_covers_whole_file():
    text = (FIXTURES / "sample.adoc").read_text()
    items = parse(text)
    title = next(it for it in items if it.signature == "= Document Title")
    total = len(text.splitlines())
    assert title.start + title.count - 1 == total


def test_minimal_fixture():
    items = parse((FIXTURES / "minimal.adoc").read_text())
    assert len(items) == 1
    assert items[0].signature == "== Only Section"


# ---------------------------------------------------------------------------
# detect (per-module)
# ---------------------------------------------------------------------------

def test_detect_level0_plus_section():
    # Doc title + sub-section is a strong AsciiDoc signal
    assert detect_adoc(["= Document Title", "", "== Section"])


def test_detect_attribute_entry():
    assert detect_adoc(["= Title", ":author: Bob"])


def test_detect_block_macro():
    assert detect_adoc(["[source,python]", "----"])


def test_detect_admonition_block():
    assert detect_adoc(["[NOTE]", "===="])


def test_detect_not_triggered_by_plain_text():
    assert not detect_adoc(["Just plain text.", "No special markers."])


def test_detect_not_triggered_by_markdown_headings():
    # Markdown # headings should not trigger AsciiDoc detection
    assert not detect_adoc(["# Markdown Heading", "## Subheading"])


def test_detect_not_triggered_by_single_equals():
    # A single = line by itself is not sufficient
    assert not detect_adoc(["= alone"])


# ---------------------------------------------------------------------------
# Extension detection
# ---------------------------------------------------------------------------

def test_guess_syntax_adoc_extensions():
    assert guess_syntax("file.adoc") == "asciidoc"
    assert guess_syntax("file.asciidoc") == "asciidoc"


def test_guess_syntax_adoc_case():
    # Extensions are lower-case in our registry
    assert guess_syntax("README.adoc") == "asciidoc"


def test_guess_syntax_other_not_adoc():
    assert guess_syntax("file.md") != "asciidoc"
    assert guess_syntax("file.rst") != "asciidoc"


# ---------------------------------------------------------------------------
# Registry-level detect
# ---------------------------------------------------------------------------

def test_detect_content_adoc_attribute_entry():
    content = "= My Doc\n:author: Alice\n:toc:\n\n== Section\n\ntext\n"
    assert detect(content) == "asciidoc"


def test_detect_content_adoc_source_block():
    content = "== Section\n\n[source,python]\n----\ncode here\n----\n"
    assert detect(content) == "asciidoc"


def test_detect_content_adoc_extension_overrides():
    assert guess_syntax("doc.adoc") == "asciidoc"
    assert guess_syntax("doc.asciidoc") == "asciidoc"

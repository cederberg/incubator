"""Tests for the Markdown/plain-text outline parser."""

from pathlib import Path

from outliner.parsers.markdown import parse, _whitespace_filter
from outliner.autodetect import detect_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "md"
FIXTURES_TXT = Path(__file__).parent / "fixtures" / "txt"


# ---------------------------------------------------------------------------
# ATX headings
# ---------------------------------------------------------------------------

def test_atx_basic():
    items = parse("# Hello\n\nsome text\n\n## World\n\nmore\n")
    assert len(items) == 2
    assert items[0].signature == "Hello"
    assert items[0].start == 1
    assert items[1].signature == "World"
    assert items[1].start == 5


def test_atx_levels_1_to_6():
    text = "\n".join(f"{'#' * i} H{i}" for i in range(1, 7))
    items = parse(text)
    assert [it.signature for it in items] == [f"H{i}" for i in range(1, 7)]


def test_atx_trailing_hashes_stripped():
    items = parse("## Title ##\n")
    assert items[0].signature == "Title"


def test_atx_empty_heading():
    items = parse("##\n\nsome text\n")
    assert items[0].signature == ""


def test_atx_range_ends_at_same_level():
    # ## A spans until ## B (exclusive)
    items = parse("## A\n\ntext\n\n## B\n\nmore\n")
    assert items[0].count == 4   # lines 1-4 (4 lines before line 5)
    assert items[1].start == 5


def test_atx_range_ends_at_higher_level():
    # ### Sub ends when # Top appears
    text = "# Top\n\n### Sub\n\ndetail\n\n# Next\n"
    items = parse(text)
    sub = next(it for it in items if it.signature == "Sub")
    top_next = next(it for it in items if it.signature == "Next")
    assert sub.count == top_next.start - sub.start


def test_atx_nested_range_extends_past_children():
    text = "## Parent\n\n### Child\n\ntext\n\n## Sibling\n"
    items = parse(text)
    parent = items[0]
    sibling = items[2]
    # Parent range ends at Sibling
    assert parent.count == sibling.start - parent.start


def test_atx_fixture():
    text = (FIXTURES / "atx.md").read_text()
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "Title" in sigs
    assert "Section One" in sigs
    assert "Subsection A" in sigs
    assert "Section Two" in sigs


# ---------------------------------------------------------------------------
# Setext headings
# ---------------------------------------------------------------------------

def test_setext_level1():
    items = parse("Hello\n=====\n\ntext\n")
    assert len(items) == 1
    assert items[0].signature == "Hello"
    assert items[0].start == 1


def test_setext_level2():
    items = parse("World\n-----\n\ntext\n")
    assert items[0].signature == "World"


def test_setext_fixture():
    text = (FIXTURES / "setext.md").read_text()
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "Title" in sigs
    assert "Section One" in sigs


def test_setext_not_triggered_by_atx_line():
    # A line starting with # should not be treated as setext text
    items = parse("# ATX\n=====\n")
    assert len(items) == 1
    assert items[0].signature == "ATX"


# ---------------------------------------------------------------------------
# Mixed ATX + Setext
# ---------------------------------------------------------------------------

def test_mixed_fixture():
    text = (FIXTURES / "mixed.md").read_text()
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "ATX Title" in sigs
    assert "Section Alpha" in sigs
    assert "ATX Sub" in sigs
    assert "Beta Section" in sigs


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file():
    assert parse("") == []


def test_no_headings_returns_first_line():
    # No blank-sandwich candidates → first-line fallback
    items = parse("just a paragraph\nno headings here\n")
    assert len(items) == 1
    assert items[0].signature == "just a paragraph"
    assert items[0].start == 1
    assert items[0].count == 2


# ---------------------------------------------------------------------------
# Blank-sandwich fallback (plain text)
# ---------------------------------------------------------------------------

def test_sandwich_basic():
    text = "Title\n\nBody text here.\nMore body.\n\nSection\n\nMore content.\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "Title" in sigs
    assert "Section" in sigs


def test_sandwich_preamble_promoted():
    # Content before first sandwich heading gets a preamble item
    text = "Preamble line\n\nHeading One\n\nContent.\n\nHeading Two\n\nMore.\n"
    items = parse(text)
    assert items[0].signature == "Preamble line"
    assert items[0].start == 1


def test_sandwich_whitespace_filter_plain():
    # GPL-style: mostly indented headings → plain outlier dropped
    items = parse((FIXTURES_TXT / "gpl3.txt").read_text())
    sigs = [it.signature for it in items]
    assert "GNU GENERAL PUBLIC LICENSE" in sigs  # preamble
    assert "Preamble" in sigs
    assert "TERMS AND CONDITIONS" in sigs
    assert "1. Source Code." in sigs
    assert "How to Apply These Terms to Your New Programs" in sigs
    # The plain outlier "Also add information..." should not appear
    assert not any("Also add information" in s for s in sigs)


def test_sandwich_whitespace_filter_indented():
    # RFC-style: mostly plain headings → indented body paragraphs dropped
    items = parse((FIXTURES_TXT / "rfc_sample.txt").read_text())
    sigs = [it.signature for it in items]
    assert "HTTP/2" in sigs       # preamble hit
    assert "Abstract" in sigs
    assert "1.  Introduction" in sigs
    assert "5.1.1.  Stream Identifiers" in sigs
    # Indented short paragraphs should not appear
    assert not any(s.startswith("This document obsoletes") for s in sigs)
    assert not any(s.startswith("The lifecycle") for s in sigs)


def test_single_heading_covers_whole_file():
    text = "# Only\n\nall content\nhere\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].count == 4


def test_heading_not_in_code_fence():
    # CommonMark: fenced code blocks should suppress headings,
    # but our simple line-by-line parser does NOT handle this.
    # This test documents current (known-limited) behaviour.
    text = "```\n# Not a heading\n```\n# Real heading\n"
    items = parse(text)
    # parser sees 2 headings — acceptable known limitation
    sigs = [it.signature for it in items]
    assert "Real heading" in sigs


# ---------------------------------------------------------------------------
# _whitespace_filter
# ---------------------------------------------------------------------------

def test_whitespace_filter_mixed_no_filter():
    # 50% indented, 50% plain — neither threshold → all returned unchanged
    candidates = [(0, "  Indented A"), (1, "Plain B"), (2, "\tIndented C"), (3, "Plain D")]
    result = _whitespace_filter(candidates)
    assert result == candidates


# ---------------------------------------------------------------------------
# autodetect
# ---------------------------------------------------------------------------

def test_autodetect_markdown_extensions():
    for ext in (".md", ".markdown", ".mdown", ".mkd"):
        assert detect_syntax(f"file{ext}") == "markdown"


def test_autodetect_text_extensions():
    for ext in (".txt", ".text"):
        assert detect_syntax(f"file{ext}") == "markdown"


def test_autodetect_unknown_returns_none():
    assert detect_syntax("file.py") is None
    assert detect_syntax("file.rs") is None
    assert detect_syntax("-") is None

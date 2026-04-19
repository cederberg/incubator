"""Tests for the reStructuredText outline parser."""

from pathlib import Path

from outliner.parsers.rst import parse, detect as detect_rst
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "rst"


# ---------------------------------------------------------------------------
# Basic heading detection
# ---------------------------------------------------------------------------

def test_simple_heading():
    items = parse("Title\n=====\n\nBody text.\n")
    assert len(items) == 1
    assert items[0].signature == "Title"
    assert items[0].start == 1
    assert items[0].count == 4


def test_two_same_level_headings():
    text = "First\n=====\n\ntext\n\nSecond\n======\n\nmore\n"
    items = parse(text)
    assert [it.signature for it in items] == ["First", "Second"]
    assert items[0].count == items[1].start - items[0].start


def test_two_levels():
    text = "Section\n=======\n\nSubsection\n-----------\n\ntext\n"
    items = parse(text)
    assert items[0].signature == "Section"
    assert items[1].signature == "Subsection"


def test_level_order_by_appearance():
    # '-' seen first → level 1; '=' seen second → level 2
    text = "First\n-----\n\nSub\n===\n\ntext\n"
    items = parse(text)
    assert items[0].signature == "First"
    assert items[1].signature == "Sub"
    # "First" is level-1 with no subsequent level-1 heading → spans the whole file
    assert items[0].count == 7
    assert items[0].start == 1


def test_non_md_decoration_chars():
    # ~ ^ * + are valid RST but not Markdown
    for char in "~^*+":
        underline = char * 5
        items = parse(f"Title\n{underline}\n\nbody\n")
        assert len(items) == 1
        assert items[0].signature == "Title"


def test_underline_too_short_not_a_heading():
    # Underline shorter than title → not a heading → first-line fallback
    items = parse("Long Title Here\n====\n\ntext\n")
    assert len(items) == 1
    assert items[0].signature == "Long Title Here"
    assert items[0].start == 1
    assert items[0].count == 4


def test_empty_file():
    assert parse("") == []


def test_no_headings_returns_first_line():
    # RST with no heading syntax → first-line fallback spanning whole file
    text = "Some text here.\nMore text.\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "Some text here."
    assert items[0].start == 1
    assert items[0].count == 2


# ---------------------------------------------------------------------------
# Preamble
# ---------------------------------------------------------------------------

def test_preamble_before_first_heading():
    text = "Meta: data\nMore: info\n\nTitle\n=====\n\nBody.\n"
    items = parse(text)
    assert items[0].start == 1
    assert items[0].signature == "Meta: data"
    assert items[0].count == 3   # lines 1-3 before heading at line 4


def test_no_preamble_when_heading_is_first():
    text = "Title\n=====\n\nBody.\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "Title"


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_range_same_level_ends_at_next():
    text = "A\n=\n\ntext\n\nB\n=\n\nmore\n"
    items = parse(text)
    a = next(it for it in items if it.signature == "A")
    b = next(it for it in items if it.signature == "B")
    assert a.count == b.start - a.start


def test_range_parent_covers_children():
    text = "Top\n===\n\nSub\n---\n\ntext\n\nAnother Top\n===========\n\nend\n"
    items = parse(text)
    top = next(it for it in items if it.signature == "Top")
    another = next(it for it in items if it.signature == "Another Top")
    assert top.count == another.start - top.start


# ---------------------------------------------------------------------------
# pep8.rst fixture — two-level hierarchy
# ---------------------------------------------------------------------------

def test_pep8_has_two_levels():
    items = parse((FIXTURES / "pep8.rst").read_text())
    sigs = [it.signature for it in items]
    assert "Introduction" in sigs
    assert "Code Lay-out" in sigs
    assert "Indentation" in sigs      # level 2 under Code Lay-out
    assert "Tabs or Spaces?" in sigs  # level 2


def test_pep8_preamble():
    items = parse((FIXTURES / "pep8.rst").read_text())
    assert items[0].signature == "PEP: 8"
    assert items[0].start == 1


def test_pep8_level1_range_contains_level2():
    items = parse((FIXTURES / "pep8.rst").read_text())
    code_layout = next(it for it in items if it.signature == "Code Lay-out")
    indentation = next(it for it in items if it.signature == "Indentation")
    assert code_layout.start < indentation.start
    assert code_layout.start + code_layout.count > indentation.start + indentation.count


def test_pep8_covers_whole_file():
    text = (FIXTURES / "pep8.rst").read_text()
    items = parse(text)
    total_lines = len(text.splitlines())
    last = items[-1]
    assert last.start + last.count - 1 == total_lines


# ---------------------------------------------------------------------------
# rst.detect (per-module, operates on line list)
# ---------------------------------------------------------------------------

def test_detect_directive():
    assert detect_rst([".. code-block:: python"])
    assert detect_rst(["text", ".. note::"])


def test_detect_non_md_underline():
    assert detect_rst(["Title", "~~~~~"])
    assert detect_rst(["Title", "^^^^^"])
    assert detect_rst(["Title", "*****"])


def test_detect_not_triggered_by_md_underlines():
    assert not detect_rst(["Title", "====="])
    assert not detect_rst(["Title", "-----"])


def test_detect_not_triggered_by_plain_text():
    assert not detect_rst(["Just some plain text.", "No special markers."])


# ---------------------------------------------------------------------------
# detect_ext / detect (registry-level)
# ---------------------------------------------------------------------------

def test_guess_syntax_rst_extensions():
    for ext in (".rst", ".rest"):
        assert guess_syntax(f"file{ext}") == "rst"


def test_guess_syntax_no_extension():
    assert guess_syntax("README") is None
    assert guess_syntax("-") is None


def test_detect_content_rst_directive():
    content = "Abstract\n========\n.. code-block:: text\n"
    assert detect(content) == "rst"


def test_detect_content_rst_tilde_underline():
    content = "Section\n~~~~~~~\n\ntext\n"
    assert detect(content) == "rst"


def test_detect_content_ambiguous_defaults_to_markdown():
    # = and - underlines alone don't trigger RST; markdown is the catch-all
    content = "Title\n=====\n\nBody text.\n"
    assert detect(content) == "markdown"

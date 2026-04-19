"""Tests for the reStructuredText outline parser."""

from pathlib import Path

from outliner.parsers.rst import parse, detect_content
from outliner.autodetect import detect_syntax

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


def test_underline_must_be_long_enough():
    # Underline shorter than title text → not a heading
    items = parse("Long Title Here\n====\n\ntext\n")
    # Should fall back to sandwich heuristic (or first-line)
    assert len(items) >= 1
    # The word "Long Title Here" should appear as sig (from sandwich or first-line)
    sigs = [it.signature for it in items]
    assert any("Long Title Here" in s or "Long" in s for s in sigs)


def test_empty_file():
    assert parse("") == []


def test_no_headings_falls_back_to_sandwich():
    # No RST headings → blank-sandwich fallback (same as markdown plain text)
    text = "Title\n\nBody text.\nMore body.\n\nSection\n\nContent.\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "Title" in sigs
    assert "Section" in sigs


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
# pep20.rst fixture
# ---------------------------------------------------------------------------

def test_pep20_preamble():
    items = parse((FIXTURES / "pep20.rst").read_text())
    assert items[0].start == 1
    assert items[0].count == 9
    assert items[0].signature == "PEP: 20"


def test_pep20_headings():
    items = parse((FIXTURES / "pep20.rst").read_text())
    sigs = [it.signature for it in items]
    assert "Abstract" in sigs
    assert "The Zen of Python" in sigs
    assert "Easter Egg" in sigs
    assert "References" in sigs
    assert "Copyright" in sigs


def test_pep20_heading_ranges():
    items = parse((FIXTURES / "pep20.rst").read_text())
    abstract = next(it for it in items if it.signature == "Abstract")
    zen = next(it for it in items if it.signature == "The Zen of Python")
    assert abstract.start == 10
    assert abstract.count == 8   # ends at line 18 where "The Zen of Python" starts
    assert zen.start == 18
    assert zen.count == 26       # ends at line 44 where "Easter Egg" starts


def test_pep20_covers_whole_file():
    text = (FIXTURES / "pep20.rst").read_text()
    items = parse(text)
    total_lines = len(text.splitlines())
    last = items[-1]
    assert last.start + last.count - 1 == total_lines


# ---------------------------------------------------------------------------
# pep8.rst fixture — two-level hierarchy
# ---------------------------------------------------------------------------

def test_pep8_has_two_levels():
    items = parse((FIXTURES / "pep8.rst").read_text())
    # Level-1 headings (=) are wide-ranging; level-2 headings (-) are narrower
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
    # "Code Lay-out" must start before and end after "Indentation"
    assert code_layout.start < indentation.start
    assert code_layout.start + code_layout.count > indentation.start + indentation.count


# ---------------------------------------------------------------------------
# detect_content
# ---------------------------------------------------------------------------

def test_detect_content_directive():
    assert detect_content([".. code-block:: python"])
    assert detect_content(["text", ".. note::"])


def test_detect_content_non_md_underline():
    assert detect_content(["Title", "~~~~~"])
    assert detect_content(["Title", "^^^^^"])
    assert detect_content(["Title", "*****"])


def test_detect_content_not_triggered_by_md_underlines():
    # = and - are ambiguous; alone they do not trigger RST detection
    assert not detect_content(["Title", "====="])
    assert not detect_content(["Title", "-----"])


def test_detect_content_not_triggered_by_plain_text():
    assert not detect_content(["Just some plain text.", "No special markers."])


# ---------------------------------------------------------------------------
# autodetect integration
# ---------------------------------------------------------------------------

def test_autodetect_rst_extensions():
    for ext in (".rst", ".rest"):
        assert detect_syntax(f"file{ext}") == "rst"


def test_autodetect_content_rst_directive():
    content = "Abstract\n========\n.. code-block:: text\n"
    assert detect_syntax(None, content) == "rst"


def test_autodetect_content_rst_tilde_underline():
    content = "Section\n~~~~~~~\n\ntext\n"
    assert detect_syntax(None, content) == "rst"


def test_autodetect_content_markdown_wins_for_atx():
    content = "# Hello\n\nWorld\n"
    assert detect_syntax(None, content) == "markdown"


def test_autodetect_content_ambiguous_returns_none():
    # Only = underlines, no other markers
    content = "Title\n=====\n\nBody text.\n"
    assert detect_syntax(None, content) is None

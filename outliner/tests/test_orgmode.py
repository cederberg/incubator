"""Tests for the Org-mode outline parser."""

from pathlib import Path

from outliner.parsers.orgmode import parse as _parse, detect as detect_org

def parse(text):
    return list(_parse(text))
from outliner.parsers import detect
from outliner.cli import guess_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "org"


# ---------------------------------------------------------------------------
# Heading detection basics
# ---------------------------------------------------------------------------

def test_level1_heading():
    items = parse("* Heading\n\nBody.\n")
    assert len(items) == 1
    assert items[0].signature == "* Heading"
    assert items[0].start == 1


def test_level2_heading():
    items = parse("** Subheading\n\nbody\n")
    assert len(items) == 1
    assert items[0].signature == "** Subheading"


def test_two_same_level():
    text = "* Alpha\n\ntext\n\n* Beta\n\nmore\n"
    items = parse(text)
    assert [it.signature for it in items] == ["* Alpha", "* Beta"]
    assert items[0].count == items[1].start - items[0].start


def test_nested_levels():
    text = "* Section\n\n** Subsection\n\ntext\n"
    items = parse(text)
    assert items[0].signature == "* Section"
    assert items[1].signature == "** Subsection"


def test_all_levels_one_through_four():
    text = "* H1\n** H2\n*** H3\n**** H4\n"
    items = parse(text)
    assert len(items) == 4
    assert items[0].signature == "* H1"
    assert items[1].signature == "** H2"
    assert items[2].signature == "*** H3"
    assert items[3].signature == "**** H4"


def test_todo_keyword_stripped():
    # TODO/DONE keywords are stripped from the signature
    items = parse("* TODO Buy milk\n\nbody\n")
    assert items[0].signature == "* Buy milk"


def test_done_keyword_stripped():
    items = parse("* DONE Finish task\n\nbody\n")
    assert items[0].signature == "* Finish task"


def test_heading_with_tags():
    # Tags at end of heading (:tag1:tag2:) are stripped
    items = parse("* My Heading :work:urgent:\n\nbody\n")
    assert items[0].signature == "* My Heading"


def test_heading_with_todo_and_tags():
    items = parse("* TODO My Task :home:\n\nbody\n")
    assert items[0].signature == "* My Task"


def test_heading_with_priority():
    # Priority cookies [#A] are stripped
    items = parse("* [#A] Important thing\n\nbody\n")
    assert items[0].signature == "* Important thing"


def test_statistics_cookie_stripped():
    # Progress cookies [n/m] and [n%] are stripped
    items = parse("* Parent [2/3]\n\nbody\n")
    assert items[0].signature == "* Parent"


def test_statistics_cookie_percent_stripped():
    items = parse("* Task [33%]\n\nbody\n")
    assert items[0].signature == "* Task"


def test_todo_keyword_case_sensitive():
    # "next" lowercase is NOT a TODO keyword — only uppercase keywords stripped
    items = parse("* Next Steps\n\nbody\n")
    assert items[0].signature == "* Next Steps"


def test_directive_lines_not_headings():
    # #+TITLE and similar directives are not headings
    text = "#+TITLE: My Doc\n#+AUTHOR: Bob\n\n* Section\n\ntext\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "* Section" in sigs
    assert not any("#+TITLE" in s for s in sigs)
    assert not any("#+AUTHOR" in s for s in sigs)


# ---------------------------------------------------------------------------
# Range computation
# ---------------------------------------------------------------------------

def test_range_same_level_ends_at_next():
    text = "* A\n\ntext\n\n* B\n\nmore\n"
    items = parse(text)
    a = items[0]
    b = items[1]
    assert a.count == b.start - a.start


def test_range_parent_covers_children():
    text = "* Parent\n\n** Child\n\ntext\n\n* Sibling\n\nend\n"
    items = parse(text)
    parent = next(it for it in items if it.signature == "* Parent")
    sibling = next(it for it in items if it.signature == "* Sibling")
    child = next(it for it in items if it.signature == "** Child")
    assert parent.count == sibling.start - parent.start
    assert parent.start < child.start
    assert parent.start + parent.count >= child.start + child.count


def test_range_to_eof():
    text = "* Only\n\nall content\n"
    items = parse(text)
    assert items[0].count == 3


def test_level1_range_covers_deeper():
    text = "* Top\n\n** Sub\n\n*** Deep\n\ntext\n\n* Next\n\nend\n"
    items = parse(text)
    top = next(it for it in items if it.signature == "* Top")
    nxt = next(it for it in items if it.signature == "* Next")
    assert top.count == nxt.start - top.start


# ---------------------------------------------------------------------------
# Preamble (content before first heading)
# ---------------------------------------------------------------------------

def test_preamble_directives_not_shown():
    # #+TITLE etc. before first heading don't produce a separate item
    text = "#+TITLE: Doc\n#+AUTHOR: X\n\n* Section\n\nbody\n"
    items = parse(text)
    # Only the section heading should appear (no preamble item for directives)
    sigs = [it.signature for it in items]
    assert sigs == ["* Section"]


def test_preamble_regular_content_shown():
    # Non-directive preamble content before first heading gets an item
    text = "Some preamble text.\nMore preamble.\n\n* Section\n\nbody\n"
    items = parse(text)
    assert items[0].start == 1
    assert "preamble" in items[0].signature.lower()


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


def test_asterisk_in_body_not_heading():
    # Body text starting with * should not be confused with headings
    # (only lines where * is followed by space count)
    text = "* Real heading\n\n*bold* text here\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "* Real heading" in sigs
    assert len(items) == 1  # *bold* is not a heading


def test_heading_no_space_not_recognized():
    # "*NoSpace" (no space after *) is NOT an Org heading
    text = "*NoSpace\n\nbody\n"
    items = parse(text)
    assert items[0].signature == "*NoSpace"  # first-line fallback


def test_property_drawer_not_heading():
    # :PROPERTIES: drawer inside a heading is not a heading
    text = "* Heading\n:PROPERTIES:\n:key: val\n:END:\n\nbody\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "* Heading"


# ---------------------------------------------------------------------------
# sample.org fixture
# ---------------------------------------------------------------------------

def test_sample_item_count():
    items = parse((FIXTURES / "sample.org").read_text())
    assert len(items) >= 7  # intro + 2 subs + main + 3 subs + conclusion


def test_sample_first_heading():
    items = parse((FIXTURES / "sample.org").read_text())
    # First item should be the first heading (preamble absorbed or directive-only)
    first_heading = next(it for it in items if it.signature.startswith("*"))
    assert "Introduction" in first_heading.signature


def test_sample_start_lines():
    text = (FIXTURES / "sample.org").read_text()
    lines = text.splitlines()
    items = parse(text)
    for item in items:
        assert 1 <= item.start <= len(lines)


def test_sample_has_subsections():
    items = parse((FIXTURES / "sample.org").read_text())
    sigs = [it.signature for it in items]
    assert any("Introduction" in s for s in sigs)
    assert any("Background" in s for s in sigs)
    assert any("Subsection A.1" in s for s in sigs)
    assert any("Conclusion" in s for s in sigs)


def test_sample_todo_stripped():
    items = parse((FIXTURES / "sample.org").read_text())
    sigs = [it.signature for it in items]
    # "* TODO Conclusion" → "* Conclusion"
    assert any("Conclusion" in s for s in sigs)
    assert not any("TODO" in s for s in sigs)


def test_sample_level1_covers_children():
    text = (FIXTURES / "sample.org").read_text()
    items = parse(text)
    intro = next(it for it in items if "Introduction" in it.signature)
    background = next(it for it in items if "Background" in it.signature)
    assert intro.start < background.start
    assert intro.start + intro.count > background.start


def test_minimal_fixture():
    items = parse((FIXTURES / "minimal.org").read_text())
    assert len(items) == 1
    assert items[0].signature == "* Only Heading"


# ---------------------------------------------------------------------------
# detect (per-module)
# ---------------------------------------------------------------------------

def test_detect_org_directive_plus_heading():
    assert detect_org(["#+TITLE: My Doc", "", "* Section"])


def test_detect_begin_src_block():
    assert detect_org(["#+BEGIN_SRC python", "print('hi')", "#+END_SRC"])


def test_detect_multiple_star_headings():
    assert detect_org(["* First", "** Second", "*** Third"])


def test_detect_not_triggered_by_plain_text():
    assert not detect_org(["Just plain text.", "No special markers."])


def test_detect_not_triggered_by_single_heading():
    # A single * heading without any other Org signal is not enough
    assert not detect_org(["* Lone heading"])


def test_detect_not_triggered_by_markdown():
    assert not detect_org(["# Markdown", "## Subheading", "Some text."])


def test_detect_title_directive_alone():
    # #+TITLE alone is a strong Org signal
    assert detect_org(["#+TITLE: Something"])


# ---------------------------------------------------------------------------
# Extension detection
# ---------------------------------------------------------------------------

def test_guess_syntax_org_extension():
    assert guess_syntax("file.org") == "orgmode"


def test_guess_syntax_org_case():
    assert guess_syntax("README.org") == "orgmode"


def test_guess_syntax_other_not_org():
    assert guess_syntax("file.md") != "orgmode"
    assert guess_syntax("file.adoc") != "orgmode"


# ---------------------------------------------------------------------------
# Registry-level detect
# ---------------------------------------------------------------------------

def test_detect_content_org_title_directive():
    content = "#+TITLE: My Org\n#+AUTHOR: Alice\n\n* Section\n\ntext\n"
    assert detect(content) == "orgmode"


def test_detect_content_org_begin_src():
    content = "* Section\n\n#+BEGIN_SRC python\ncode here\n#+END_SRC\n"
    assert detect(content) == "orgmode"


def test_detect_content_org_extension_overrides():
    assert guess_syntax("notes.org") == "orgmode"

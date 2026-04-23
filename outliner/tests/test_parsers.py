"""Tests for parsers/__init__.py — front-matter stripping and dispatch."""

import outliner.parsers as parsers


# ---------------------------------------------------------------------------
# Front-matter stripping via outline() — correctness and line numbers
# ---------------------------------------------------------------------------

def test_frontmatter_line_numbers_offset():
    # Front-matter is 3 lines; heading must appear at line 4, not line 1.
    text = "---\nname: test\n---\n# Heading\n\nBody.\n"
    items = parsers.outline("markdown", text)
    assert len(items) == 1
    assert items[0].signature == "# Heading"
    assert items[0].start == 4


def test_frontmatter_headings_found():
    text = "---\nname: test\ndescription: foo\n---\n# Heading\n\nBody.\n"
    items = parsers.outline("markdown", text)
    assert len(items) == 1
    assert items[0].signature == "# Heading"


def test_frontmatter_false_setext_not_triggered():
    # Without stripping the closing --- would be a false Setext underline for
    # the last front-matter line, hiding the real heading below.
    text = "---\nname: test\nsome line\n---\n# Real Heading\n\nBody.\n"
    items = parsers.outline("markdown", text)
    sigs = [it.signature for it in items]
    assert any("Real Heading" in s for s in sigs)
    assert not any("some line" in s for s in sigs)


def test_frontmatter_no_closer_not_stripped():
    # No closing --- → treat as regular Markdown, don't drop content.
    text = "---\nname: test\n\n# Heading\n\nBody.\n"
    items = parsers.outline("markdown", text)
    sigs = [it.signature for it in items]
    assert any("Heading" in s for s in sigs)


def test_frontmatter_closer_beyond_100_lines_not_stripped():
    # Closing --- beyond line 100 is not treated as front-matter.
    # When not stripped, the heading appears deep in the file, not at line 1.
    inner = "".join(f"field{i}: value\n" for i in range(100))
    text = f"---\n{inner}---\n# Heading\n"
    items = parsers.outline("markdown", text)
    sigs = [it.signature for it in items]
    assert any("Heading" in s for s in sigs)
    heading = next(it for it in items if it.signature == "# Heading")
    assert heading.start > 100


# ---------------------------------------------------------------------------
# Front-matter stripping via detect()
# ---------------------------------------------------------------------------

def test_frontmatter_rst_directive_not_false_positive():
    # A .. directive inside front-matter must not trigger RST detection.
    text = "---\nnote: .. looks like a directive\n---\n# Heading\n\nBody.\n"
    assert parsers.detect(text) == "markdown"

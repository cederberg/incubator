"""Tests for the HTML outline parser."""

from pathlib import Path

from outliner.parsers.html import parse as _parse, detect as detect_html
from outliner.parsers import detect
from outliner.cli import guess_syntax

def parse(text):
    return list(_parse(text))

FIXTURES = Path(__file__).parent / "fixtures" / "html"


# ---------------------------------------------------------------------------
# Extension / syntax detection
# ---------------------------------------------------------------------------

def test_guess_syntax_html_extensions():
    for ext in (".html", ".htm", ".xhtml"):
        assert guess_syntax(f"file{ext}") == "html"


def test_detect_doctype():
    assert detect_html(["<!DOCTYPE html>"])
    assert detect_html(["<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\">"])


def test_detect_html_tag():
    assert detect_html(["<html lang='en'>"])
    assert detect_html(["<html>"])


def test_detect_not_plain_text():
    assert not detect_html(["Just plain text.", "No HTML here."])


def test_detect_not_python():
    assert not detect_html(["# parse <html> tag", "def foo():"])


def test_detect_content_registry():
    content = "<!DOCTYPE html>\n<html>\n<body><h1>Hi</h1></body></html>\n"
    assert detect(content) == "html"


# ---------------------------------------------------------------------------
# Structural elements: <head> and <body>
# ---------------------------------------------------------------------------

def test_head_signature():
    items = parse("<html><head><title>T</title></head><body></body></html>")
    sigs = [it.signature for it in items]
    assert "<head>" in sigs


def test_body_signature():
    items = parse("<html>\n<head></head>\n<body><p>hi</p></body>\n</html>")
    sigs = [it.signature for it in items]
    assert "<body>" in sigs


def test_head_body_no_indent():
    items = parse("<head>\n<title>T</title>\n</head>\n<body>\n<p>hi</p>\n</body>\n")
    head = next(it for it in items if it.signature == "<head>")
    body = next(it for it in items if it.signature == "<body>")
    assert not head.signature.startswith(" ")
    assert not body.signature.startswith(" ")


def test_head_range():
    text = "<head>\n<title>T</title>\n</head>\n<body>\n<p>hi</p>\n</body>\n"
    items = parse(text)
    head = next(it for it in items if it.signature == "<head>")
    assert head.start == 1
    assert head.count == 3


def test_body_range():
    text = "<head>\n<title>T</title>\n</head>\n<body>\n<p>hi</p>\n</body>\n"
    items = parse(text)
    body = next(it for it in items if it.signature == "<body>")
    assert body.start == 4
    assert body.count == 3


def test_title_signature():
    items = parse("<head>\n<title>Example &amp; Test</title>\n</head>\n")
    title = next(it for it in items if it.signature.startswith("  <title>"))
    assert title.start == 2
    assert title.count == 1
    assert title.signature == "  <title>Example & Test</title>"


def test_embedded_body_title_is_ignored():
    items = parse("<head><title>Real</title></head><body><title>Embed</title></body>\n")
    sigs = [it.signature for it in items]
    assert "  <title>Real</title>" in sigs
    assert "  <title>Embed</title>" not in sigs


# ---------------------------------------------------------------------------
# Heading signatures (native <hN>text</hN> with 2-space depth indent)
# ---------------------------------------------------------------------------

def test_h1_signature():
    items = parse("<html><body><h1>Main Title</h1></body></html>")
    sigs = [it.signature for it in items]
    assert "  <h1>Main Title</h1>" in sigs


def test_h2_signature():
    items = parse("<h2>Sub Heading</h2>")
    assert items[0].signature == "  <h2>Sub Heading</h2>"


def test_all_heading_levels():
    text = "".join(f"<h{i}>Level {i}</h{i}>\n" for i in range(1, 7))
    items = parse(text)
    for i in range(1, 7):
        expected = "  " * i + f"<h{i}>Level {i}</h{i}>"
        assert any(it.signature == expected for it in items)


def test_heading_inner_tags_stripped():
    items = parse("<h2><em>Styled</em> Heading</h2>")
    assert items[0].signature == "  <h2>Styled Heading</h2>"


def test_html_entity_amp():
    items = parse("<h3>AT&amp;T</h3>")
    assert items[0].signature == "  <h3>AT&T</h3>"


def test_html_entity_lt_gt():
    # entities decoded; the resulting < and > are literal in the signature text
    items = parse("<h2>Type &lt;X&gt;</h2>")
    assert items[0].signature == "  <h2>Type <X></h2>"


def test_html_entity_numeric_decimal():
    items = parse("<h2>&#65;BC</h2>")
    assert items[0].signature == "  <h2>ABC</h2>"


def test_html_entity_numeric_hex():
    items = parse("<h2>&#x41;BC</h2>")
    assert items[0].signature == "  <h2>ABC</h2>"


def test_multiline_heading():
    text = "<h2>\n  Multi-line\n  Heading\n</h2>\n"
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "  <h2>Multi-line Heading</h2>"
    assert items[0].start == 1


def test_multiline_opening_tag():
    # '>' on a different line from the tag name
    text = '<h1 class="big"\n    style="color:red">\n  My Heading\n</h1>\n'
    items = parse(text)
    assert len(items) == 1
    assert items[0].signature == "  <h1>My Heading</h1>"
    assert items[0].start == 1
    assert items[0].count == 4


def test_multiline_opening_tag_section():
    text = '<section\n  id="details">\n<p>text</p>\n</section>\n'
    items = parse(text)
    sec = next(it for it in items if "section" in it.signature)
    assert sec.signature == "  <section#details>text"
    assert sec.start == 1
    assert sec.count == 4


# ---------------------------------------------------------------------------
# Heading ranges
# ---------------------------------------------------------------------------

def test_h2_range_ends_at_next_h2():
    text = "<h2>A</h2>\n<p>text</p>\n<h2>B</h2>\n<p>more</p>\n"
    items = parse(text)
    a = next(it for it in items if it.signature == "  <h2>A</h2>")
    b = next(it for it in items if it.signature == "  <h2>B</h2>")
    assert a.count == b.start - a.start


def test_h3_range_ends_at_h2():
    text = "<h2>Parent</h2>\n<h3>Child</h3>\n<p>x</p>\n<h2>Next</h2>\n"
    items = parse(text)
    child = next(it for it in items if it.signature == "    <h3>Child</h3>")
    nxt   = next(it for it in items if it.signature == "  <h2>Next</h2>")
    assert child.count == nxt.start - child.start


def test_h1_covers_rest_of_file():
    text = "<h1>Title</h1>\n<h2>Sub</h2>\n<p>text</p>\n"
    items = parse(text)
    h1 = next(it for it in items if it.signature == "  <h1>Title</h1>")
    total = len(text.splitlines())
    assert h1.start + h1.count - 1 == total


# ---------------------------------------------------------------------------
# Landmark elements (2-space indent, inside body)
# ---------------------------------------------------------------------------

def test_nav_signature():
    items = parse("<nav>\n<a>link</a>\n</nav>\n")
    sigs = [it.signature for it in items]
    assert "  <nav>link" in sigs


def test_main_signature():
    items = parse("<main>\n<p>body</p>\n</main>\n")
    sigs = [it.signature for it in items]
    assert "  <main>body" in sigs


def test_article_signature():
    items = parse("<article>\n<p>text</p>\n</article>\n")
    sigs = [it.signature for it in items]
    assert "  <article>text" in sigs


def test_section_plain_signature():
    assert parse("<section></section>\n") == []


def test_empty_landmarks_are_omitted():
    assert parse("<header></header><article></article><nav></nav>\n") == []


def test_section_with_id():
    items = parse("<section id=\"details\">\n<p>text</p>\n</section>\n")
    sigs = [it.signature for it in items]
    assert "  <section#details>text" in sigs


def test_nav_with_aria_label():
    items = parse("<nav aria-label=\"Main navigation\">\n<a>link</a>\n</nav>\n")
    sigs = [it.signature for it in items]
    assert '  <nav aria-label="Main navigation">' in sigs


def test_nav_with_id_and_aria_label():
    items = parse("<nav id=\"site\" aria-label=\"Site\">\n<a>link</a>\n</nav>\n")
    sigs = [it.signature for it in items]
    assert '  <nav#site aria-label="Site">' in sigs


def test_main_with_id_and_aria_label():
    items = parse("<main id=\"content\" aria-label=\"Article\"><p>Body</p></main>\n")
    sigs = [it.signature for it in items]
    assert '  <main#content aria-label="Article">' in sigs


def test_header_signature():
    items = parse("<header id=\"top\"></header>\n")
    sigs = [it.signature for it in items]
    assert "  <header#top>" in sigs


def test_footer_is_omitted():
    assert parse("<footer aria-label=\"Site footer\">Legal links</footer>\n") == []


def test_section_excerpt_from_heading():
    items = parse("<section><h2>Useful heading</h2><p>Body text.</p></section>\n")
    sigs = [it.signature for it in items]
    assert "  <section>Useful heading" in sigs


def test_article_excerpt_from_text():
    items = parse("<article><p>First useful sentence. Second sentence.</p></article>\n")
    sigs = [it.signature for it in items]
    assert "  <article>First useful sentence." in sigs


def test_labeled_nav_omits_excerpt():
    items = parse("<nav aria-label=\"Main\"><a>Home</a></nav>\n")
    sigs = [it.signature for it in items]
    assert '  <nav aria-label="Main">' in sigs


def test_boring_excerpt_is_omitted():
    assert parse("<section>Skip to content</section>\n") == []


def test_same_line_nav_range():
    items = parse("<div><nav aria-label=\"Pages\"><a>One</a></nav><p>after</p></div>\n")
    nav = next(it for it in items if it.signature == '  <nav aria-label="Pages">')
    assert nav.start == 1
    assert nav.count == 1


def test_same_line_article_range():
    items = parse("<article><h2>One</h2><p>Body</p></article><p>after</p>\n")
    article = next(it for it in items if it.signature.startswith("  <article>"))
    assert article.count == 1


def test_multiple_same_line_headings():
    items = parse("<main><h1>One</h1><section><h2>Two</h2></section><h2>Three</h2></main>\n")
    sigs = [it.signature for it in items]
    assert "    <h1>One</h1>" in sigs
    assert "      <h2>Two</h2>" in sigs
    assert "      <h2>Three</h2>" in sigs


def test_same_line_style_does_not_suppress_later_heading():
    items = parse("<style>.x{color:red}</style><h2>Still here</h2>\n")
    sigs = [it.signature for it in items]
    assert "  <h2>Still here</h2>" in sigs


def test_script_html_does_not_create_structural_items():
    items = parse('<script>const x = "<head><body><h1>Fake</h1>";</script><h1>Real</h1>\n')
    sigs = [it.signature for it in items]
    assert "<head>" not in sigs
    assert "<body>" not in sigs
    assert "  <h1>Real</h1>" in sigs
    assert not any("Fake" in sig for sig in sigs)


def test_embedded_head_inside_body_is_ignored():
    items = parse("<head></head><body><main><head><title>Embed</title></head></main></body>\n")
    assert [it.signature for it in items].count("<head>") == 1


def test_section_with_class():
    items = parse("<section class=\"hero main-section\">\n<p>text</p>\n</section>\n")
    sigs = [it.signature for it in items]
    assert "  <section>text" in sigs


def test_landmark_range_covers_closing_tag():
    text = "<nav>\n<a>Home</a>\n<a>About</a>\n</nav>\n<p>after</p>\n"
    items = parse(text)
    nav = next(it for it in items if it.signature.startswith("  <nav>"))
    assert nav.start == 1
    assert nav.count == 4


def test_nested_landmarks_both_appear():
    text = "<main>\n<section>\n<p>x</p>\n</section>\n</main>\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "  <main>" in sigs
    assert "    <section>x" in sigs


def test_nested_landmarks_indent_by_outline_depth():
    items = parse(
        "<body><main><section id='s'><article id='a'>"
        "<h2>Deep</h2></article></section></main></body>\n"
    )
    assert any(it.signature.startswith("  <main>") for it in items)
    assert any(it.signature.startswith("    <section#s>") for it in items)
    assert any(it.signature.startswith("      <article#a>") for it in items)
    assert any(it.signature.startswith("        <h2>Deep</h2>") for it in items)


def test_skipped_heading_level_stays_near_container():
    items = parse("<section><h3>Card title</h3></section>\n")
    sigs = [it.signature for it in items]
    assert "  <section>Card title" in sigs
    assert "    <h3>Card title</h3>" in sigs


def test_heading_levels_are_relative_within_container():
    items = parse("<section><h2>News</h2><h3>Story</h3></section>\n")
    sigs = [it.signature for it in items]
    assert "    <h2>News</h2>" in sigs
    assert "      <h3>Story</h3>" in sigs


def test_script_block_headings_suppressed():
    text = "<body>\n<script>\nvar t = \"<h2>Fake</h2>\";\n</script>\n<h2>Real</h2>\n</body>\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert not any("Fake" in s for s in sigs)
    assert "  <h2>Real</h2>" in sigs


def test_style_block_headings_suppressed():
    text = "<head>\n<style>\n/* h1 { color: red; } */\n</style>\n</head>\n<body>\n<h1>Real</h1>\n</body>\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "  <h1>Real</h1>" in sigs
    assert sum(1 for s in sigs if "<h1>" in s) == 1  # only one h1


def test_inline_script_does_not_suppress_adjacent_heading():
    # <script> and </script> on the same line — the line is skipped,
    # but headings on other lines are unaffected
    text = "<script src='a.js'></script>\n<h2>Still here</h2>\n"
    items = parse(text)
    sigs = [it.signature for it in items]
    assert "  <h2>Still here</h2>" in sigs


def test_landmark_unclosed_extends_to_eof():
    text = "<section>\n<p>text</p>\n<p>more</p>\n"
    items = parse(text)
    sec = next(it for it in items if it.signature.startswith("  <section>"))
    assert sec.start == 1
    assert sec.count == 3


# ---------------------------------------------------------------------------
# Fixture: basic.html
# ---------------------------------------------------------------------------

def test_fixture_item_count():
    items = parse((FIXTURES / "basic.html").read_text())
    # 7 headings + title + 4 landmarks + 2 structural (head, body) = 14
    assert len(items) == 14


def test_fixture_sorted_by_start():
    items = parse((FIXTURES / "basic.html").read_text())
    starts = [it.start for it in items]
    assert starts == sorted(starts)


def test_fixture_head():
    items = parse((FIXTURES / "basic.html").read_text())
    head = next(it for it in items if it.signature == "<head>")
    assert head.start == 3
    assert head.count == 4


def test_fixture_body():
    items = parse((FIXTURES / "basic.html").read_text())
    body = next(it for it in items if it.signature == "<body>")
    assert body.start == 7
    assert body.count == 34


def test_fixture_nav():
    items = parse((FIXTURES / "basic.html").read_text())
    nav = next(it for it in items if it.signature.startswith("  <nav>"))
    assert nav.start == 8
    assert nav.count == 4


def test_fixture_main():
    items = parse((FIXTURES / "basic.html").read_text())
    main = next(it for it in items if it.signature.startswith("  <main>"))
    assert main.start == 12
    assert main.count == 28


def test_fixture_h1():
    items = parse((FIXTURES / "basic.html").read_text())
    h1 = next(it for it in items if it.signature.strip() == "<h1>Main Title</h1>")
    assert h1.start == 13
    assert h1.count == 29


def test_fixture_h2_section_one():
    items = parse((FIXTURES / "basic.html").read_text())
    h2 = next(it for it in items if it.signature.strip() == "<h2>Section One</h2>")
    assert h2.start == 16
    assert h2.count == 8


def test_fixture_article():
    items = parse((FIXTURES / "basic.html").read_text())
    art = next(it for it in items if it.signature.lstrip().startswith("<article>"))
    assert art.start == 19
    assert art.count == 4


def test_fixture_h3_article_heading():
    items = parse((FIXTURES / "basic.html").read_text())
    h3 = next(it for it in items if it.signature.strip() == "<h3>Article Heading</h3>")
    assert h3.start == 20
    assert h3.count == 4


def test_fixture_h2_section_two():
    items = parse((FIXTURES / "basic.html").read_text())
    h2 = next(it for it in items if it.signature.strip() == "<h2>Section Two</h2>")
    assert h2.start == 24
    assert h2.count == 10


def test_fixture_section_with_id():
    items = parse((FIXTURES / "basic.html").read_text())
    sec = next(it for it in items if it.signature.lstrip().startswith("<section#details>"))
    assert sec.start == 26
    assert sec.count == 7


def test_fixture_h3_entity_decoded():
    items = parse((FIXTURES / "basic.html").read_text())
    h3 = next(it for it in items if it.signature.strip() == "<h3>Details & More</h3>")
    assert h3.start == 27
    assert h3.count == 7


def test_fixture_h4():
    items = parse((FIXTURES / "basic.html").read_text())
    h4 = next(it for it in items if it.signature.strip() == "<h4>Sub-details</h4>")
    assert h4.start == 30
    assert h4.count == 4


def test_fixture_multiline_h2():
    items = parse((FIXTURES / "basic.html").read_text())
    h2 = next(it for it in items if it.signature.strip() == "<h2>Multi-line Heading</h2>")
    assert h2.start == 34
    assert h2.count == 8


def test_empty_html():
    assert parse("") == []


def test_no_headings_no_landmarks():
    items = parse("<html><body><p>Just a paragraph.</p></body></html>")
    # only body detected (head absent in this snippet)
    sigs = [it.signature for it in items]
    assert all(s in ("<body>",) for s in sigs)

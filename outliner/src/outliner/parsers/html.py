"""HTML outline parser using Python's tokenizing HTMLParser."""

import html
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser

from outliner.types import OutlineItem

SYNTAX = "html"
EXTENSIONS = (".html", ".htm", ".xhtml")

_DOCTYPE_RE = re.compile(r'^\s*<!DOCTYPE\s+html', re.IGNORECASE)
_HTML_TAG_RE = re.compile(r'^\s*<html[\s>]', re.IGNORECASE)
_WS_RE = re.compile(r'\s+')
_SENTENCE_RE = re.compile(r'(?<=[.!?])\s+')
_STRUCTURAL = {"head", "body"}
_LANDMARKS = {"nav", "main", "article", "section", "header"}
_OUTLINE_TAGS = _STRUCTURAL | _LANDMARKS
_CONTENT_TAGS = {"body"} | _LANDMARKS
_TEXT_SKIP_TAGS = {"script", "style", "svg", "noscript", "template"}
_EXCERPT_LIMIT = 80
_BORING_EXCERPTS = {
    "advertisement", "close", "menu", "navigation", "open menu",
    "search", "skip advertisement", "skip to content",
}
_VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


@dataclass
class _Node:
    tag: str
    start: int
    start_col: int
    attrs: dict[str, str]
    depth: int
    text_parts: list[str] = field(default_factory=list)
    heading_text: str = ""
    end: int | None = None

    @property
    def signature(self) -> str:
        return _block_sig(
            self.tag,
            self.attrs,
            self.heading_text or "".join(self.text_parts),
            self.depth,
        )

    @property
    def has_identity(self) -> bool:
        return (
            self.tag in _STRUCTURAL
            or self.tag == "main"
            or bool(self.attrs.get("id"))
            or bool(_clean(self.attrs.get("aria-label", "")))
            or bool(_excerpt(self.heading_text or "".join(self.text_parts)))
        )


@dataclass
class _Heading:
    tag: str
    level: int
    start: int
    start_col: int
    base_depth: int
    context_key: int
    text_parts: list[str] = field(default_factory=list)


class _Parser(HTMLParser):
    def __init__(self, line_count: int):
        super().__init__(convert_charrefs=False)
        self.line_count = line_count
        self.nodes: list[_Node] = []
        self.headings: list[tuple[int, int, int, str]] = []
        self.titles: list[tuple[int, int, OutlineItem]] = []
        self._stack: list[_Node] = []
        self._heading: _Heading | None = None
        self._title: _Heading | None = None
        self._text_skip: list[str] = []
        self._heading_stacks: dict[int, list[tuple[int, int]]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self._text_skip:
            if tag in _TEXT_SKIP_TAGS:
                self._text_skip.append(tag)
            return
        if tag in _TEXT_SKIP_TAGS:
            self._text_skip.append(tag)
            return

        line, column = self.getpos()
        attrs_by_name = {name.lower(): value or "" for name, value in attrs}
        if tag in _OUTLINE_TAGS:
            if tag in _STRUCTURAL and self._inside_content():
                return
            node = _Node(
                tag=tag,
                start=line,
                start_col=column,
                attrs=attrs_by_name,
                depth=self._tag_depth(tag),
            )
            self.nodes.append(node)
            if tag not in _VOID_TAGS:
                self._stack.append(node)
        elif tag in _VOID_TAGS:
            return

        if _is_heading(tag):
            self._heading = _Heading(
                tag=tag,
                level=int(tag[1]),
                start=line,
                start_col=column,
                base_depth=self._heading_base_depth(),
                context_key=self._heading_context_key(),
            )
        elif tag == "title" and self._inside_document_head():
            self._title = _Heading(
                tag=tag,
                level=0,
                start=line,
                start_col=column,
                base_depth=self._tag_depth(tag),
                context_key=0,
            )

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self._text_skip:
            return
        if tag in _OUTLINE_TAGS:
            if tag in _STRUCTURAL and self._inside_content():
                return
            attrs_by_name = {name.lower(): value or "" for name, value in attrs}
            line, column = self.getpos()
            self.nodes.append(_Node(
                tag=tag,
                start=line,
                start_col=column,
                end=line,
                attrs=attrs_by_name,
                depth=self._tag_depth(tag),
            ))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._text_skip:
            if tag == self._text_skip[-1]:
                self._text_skip.pop()
            return

        line = self.getpos()[0]
        if self._heading and tag == self._heading.tag:
            heading = self._heading
            text = _clean("".join(heading.text_parts))
            depth = self._heading_depth(heading)
            self.headings.append((
                heading.start,
                heading.start_col,
                heading.level,
                f"{'  ' * depth}<{heading.tag}>{text}</{heading.tag}>",
            ))
            for node in reversed(self._stack):
                if node.tag in _LANDMARKS and not node.heading_text:
                    node.heading_text = text
                    break
            self._heading = None
        elif self._title and tag == "title":
            title = self._title
            text = _clean("".join(title.text_parts))
            if text:
                self.titles.append((title.start, title.start_col, OutlineItem(
                    start=title.start,
                    count=max(1, line - title.start + 1),
                    signature=f"{'  ' * title.base_depth}<title>{text}</title>",
                )))
            self._title = None

        if tag in _OUTLINE_TAGS:
            for idx in range(len(self._stack) - 1, -1, -1):
                node = self._stack[idx]
                if node.tag == tag:
                    node.end = line
                    del self._stack[idx:]
                    break

    def handle_data(self, data: str) -> None:
        if self._heading:
            self._heading.text_parts.append(data)
        elif self._title:
            self._title.text_parts.append(data)
        elif not self._text_skip:
            self._add_text(data)

    def handle_entityref(self, name: str) -> None:
        if self._heading:
            self._heading.text_parts.append(f"&{name};")
        elif self._title:
            self._title.text_parts.append(f"&{name};")
        elif not self._text_skip:
            self._add_text(f"&{name};", glue=True)

    def handle_charref(self, name: str) -> None:
        if self._heading:
            self._heading.text_parts.append(f"&#{name};")
        elif self._title:
            self._title.text_parts.append(f"&#{name};")
        elif not self._text_skip:
            self._add_text(f"&#{name};", glue=True)

    def close(self) -> None:
        super().close()
        if self._heading:
            heading = self._heading
            text = _clean("".join(heading.text_parts))
            depth = self._heading_depth(heading)
            self.headings.append((
                heading.start,
                heading.start_col,
                heading.level,
                f"{'  ' * depth}<{heading.tag}>{text}</{heading.tag}>",
            ))
            self._heading = None
        if self._title:
            title = self._title
            text = _clean("".join(title.text_parts))
            if text:
                self.titles.append((title.start, title.start_col, OutlineItem(
                    start=title.start,
                    count=max(1, self.line_count - title.start + 1),
                    signature=f"{'  ' * title.base_depth}<title>{text}</title>",
                )))
            self._title = None
        for node in self._stack:
            node.end = self.line_count

    def _inside_content(self) -> bool:
        return any(node.tag in _CONTENT_TAGS for node in self._stack)

    def _inside_document_head(self) -> bool:
        return any(node.tag == "head" for node in self._stack) and not self._inside_content()

    def _outline_depth(self) -> int:
        return len([
            node for node in self._stack
            if node.has_identity and node.tag not in _STRUCTURAL
        ])

    def _tag_depth(self, tag: str) -> int:
        return 0 if tag in _STRUCTURAL else self._outline_depth() + 1

    def _heading_context_node(self) -> _Node | None:
        for node in reversed(self._stack):
            if node.tag not in _STRUCTURAL and node.tag in _OUTLINE_TAGS:
                return node
        return None

    def _heading_base_depth(self) -> int:
        node = self._heading_context_node()
        return node.depth + 1 if node else 1

    def _heading_context_key(self) -> int:
        node = self._heading_context_node()
        return id(node) if node else 0

    def _heading_depth(self, heading: _Heading) -> int:
        stack = self._heading_stacks.setdefault(heading.context_key, [])
        while stack and stack[-1][0] >= heading.level:
            stack.pop()
        depth = stack[-1][1] + 1 if stack else heading.base_depth
        stack.append((heading.level, depth))
        return depth

    def _add_text(self, text: str, glue: bool = False) -> None:
        if not text.strip():
            return
        for node in reversed(self._stack):
            if node.tag in _LANDMARKS:
                if node.text_parts and not (glue or node.text_parts[-1].endswith(";")):
                    node.text_parts.append(" ")
                node.text_parts.append(text)
                break


def _is_heading(tag: str) -> bool:
    return len(tag) == 2 and tag[0] == "h" and tag[1] in "123456"


def _clean(text: str) -> str:
    return _WS_RE.sub(" ", html.unescape(text)).strip()


def _block_sig(tag: str, attrs: dict[str, str], fallback_text: str = "", depth: int = 0) -> str:
    ident = f"#{attrs['id']}" if attrs.get("id") else ""
    label = _clean(attrs.get("aria-label", ""))
    label_attr = f' aria-label="{label}"' if label else ""
    excerpt = _excerpt(fallback_text) if tag in _LANDMARKS else ""
    text = excerpt if excerpt and not label else ""
    return f"{'  ' * depth}<{tag}{ident}{label_attr}>{text}"


def _excerpt(text: str) -> str:
    text = _clean(text)
    if not text:
        return ""
    first = _SENTENCE_RE.split(text, maxsplit=1)[0]
    if first.lower() in _BORING_EXCERPTS:
        return ""
    return first if len(first) <= _EXCERPT_LIMIT else first[:_EXCERPT_LIMIT - 3].rstrip() + "..."


def _items_from_headings(
    headings: list[tuple[int, int, int, str]],
    line_count: int,
) -> Iterator[tuple[int, int, OutlineItem]]:
    for idx, (line, column, level, signature) in enumerate(headings):
        end = line_count + 1
        for future_line, _, future_level, _ in headings[idx + 1:]:
            if future_level <= level:
                end = future_line
                break
        yield (line, column, OutlineItem(start=line, count=max(1, end - line), signature=signature))


def detect(lines: list[str]) -> bool:
    for line in lines[:30]:
        if _DOCTYPE_RE.match(line) or _HTML_TAG_RE.match(line):
            return True
    return False


def parse(text: str) -> Iterator[OutlineItem]:
    line_count = len(text.splitlines())
    parser = _Parser(line_count)
    parser.feed(text)
    parser.close()

    block_items = (
        (node.start, node.start_col, OutlineItem(
            start=node.start,
            count=max(1, (node.end or line_count) - node.start + 1),
            signature=node.signature,
        ))
        for node in parser.nodes if node.has_identity
    )
    events = [*parser.titles, *_items_from_headings(parser.headings, line_count), *block_items]
    for _, _, item in sorted(events, key=lambda event: (event[0], event[1])):
        yield item

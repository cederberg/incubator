"""XML outline parser.

Produces XPath-like locators with XML-native node kinds in the signature
column: elem, attr, text, and mixed.
"""

import io
import os
import stat
import time
import xml.parsers.expat
from collections import Counter, defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field

from outliner.parsers.util import format_count, format_size
from outliner.types import OutlineItem

SYNTAX = "xml"
EXTENSIONS = (".xml",)

MAX_START_ELEMENTS = 1_000_000
MAX_SECONDS = 0.5
TIME_CHECK_INTERVAL = 8192


@dataclass
class PathStats:
    count: int = 0
    attrs: dict[str, int] = field(default_factory=dict)
    attr_samples: dict[str, str] = field(default_factory=dict)
    child_counts: Counter[str] = field(default_factory=Counter)
    text_count: int = 0
    child_count: int = 0
    sample: str = ""


@dataclass
class OpenElem:
    path: tuple[str, ...]
    children: set[str] = field(default_factory=set)
    has_child: bool = False
    has_text: bool = False
    text: list[str] = field(default_factory=list)


class StopParsing(Exception):
    pass


class Collector:
    def __init__(self):
        self.stats: dict[tuple[str, ...], PathStats] = {}
        self.children: dict[tuple[str, ...], list[tuple[str, ...]]] = defaultdict(list)
        self.seen_children: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
        self.stack: list[OpenElem] = []
        self.started = 0
        self.start_time = time.perf_counter()

    def start(self, name: str, attrs: dict[str, str]) -> None:
        self.started += 1
        if self.started > MAX_START_ELEMENTS or self._timed_out():
            raise StopParsing

        path = (*self.stack[-1].path, name) if self.stack else (name,)
        stats = self.stats.setdefault(path, PathStats())
        stats.count += 1

        if self.stack:
            parent = self.stack[-1]
            parent.has_child = True
            parent.children.add(name)
            key = (parent.path, path)
            if key not in self.seen_children:
                self.children[parent.path].append(path)
                self.seen_children.add(key)

        for attr_name, value in attrs.items():
            if attr_name == "xmlns" or attr_name.startswith("xmlns:"):
                continue
            stats.attrs[attr_name] = stats.attrs.get(attr_name, 0) + 1
            if attr_name not in stats.attr_samples:
                stats.attr_samples[attr_name] = _clean_text(value)

        self.stack.append(OpenElem(path=path))

    def text(self, data: str) -> None:
        text = _clean_text(data)
        if not text or not self.stack:
            return
        elem = self.stack[-1]
        elem.has_text = True
        if sum(len(part) for part in elem.text) < 120:
            elem.text.append(text)

    def end(self, _name: str) -> None:
        if self.stack:
            self._finish(self.stack.pop())

    def finish_open(self) -> None:
        while self.stack:
            self._finish(self.stack.pop())

    def _finish(self, elem: OpenElem) -> None:
        stats = self.stats[elem.path]
        if elem.has_text:
            stats.text_count += 1
            if not stats.sample:
                stats.sample = _clean_text(" ".join(elem.text))
        if elem.has_child:
            stats.child_count += 1
        for child in elem.children:
            stats.child_counts[child] += 1

    def _timed_out(self) -> bool:
        return (
            self.started % TIME_CHECK_INTERVAL == 0
            and time.perf_counter() - self.start_time >= MAX_SECONDS
        )


# -- detection -----------------------------------------------------------

def detect(lines: list[str]) -> bool:
    first = next((line.strip() for line in lines if line.strip()), "")
    if not first:
        return False
    return first.lower().startswith("<?xml")


# -- entry point ---------------------------------------------------------

def read(fh) -> Iterator[OutlineItem]:
    collector = Collector()
    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = collector.start
    parser.EndElementHandler = collector.end
    parser.CharacterDataHandler = collector.text

    try:
        while chunk := fh.read(1024 * 1024):
            parser.Parse(chunk, False)
        parser.Parse("", True)
    except StopParsing:
        collector.finish_open()
    except xml.parsers.expat.ExpatError:
        return

    if not collector.stats:
        return

    sampled = sum(stats.count for stats in collector.stats.values())
    size = _file_size(fh)
    prefix = f"{format_size(size)} · " if size is not None else ""
    signature = f"{prefix}xml · sampled {format_count(sampled)} elems"
    yield OutlineItem(locator="/", signature=signature)
    yield from _emit_schema(collector)


# -- schema emission -----------------------------------------------------

def _emit_schema(collector: Collector) -> Iterator[OutlineItem]:
    paths = list(collector.stats)
    root = paths[0]
    yield from _emit_path(collector, root)


def _emit_path(
    collector: Collector,
    path: tuple[str, ...],
) -> Iterator[OutlineItem]:
    stats = collector.stats[path]
    sig = _element_sig(collector, path)
    sample = _sample(stats.sample)
    if sample and _kind(stats) in ("text", "mixed"):
        sig = f"{sig} -- {sample}"
    yield OutlineItem(locator=_element_locator(path), signature=sig)

    for attr in sorted(stats.attrs):
        attr_sig = _sig("attr", stats.attrs[attr] < stats.count)
        sample = _sample(stats.attr_samples.get(attr, ""))
        if sample:
            attr_sig = f"{attr_sig} -- {sample}"
        yield OutlineItem(locator=_attr_locator(path, attr), signature=attr_sig)

    for child in collector.children.get(path, []):
        yield from _emit_path(collector, child)


def _kind(stats: PathStats) -> str:
    if stats.text_count and stats.child_count:
        return "mixed"
    if stats.text_count:
        return "text"
    return "elem"


def _sig(kind: str, optional: bool) -> str:
    return f"{kind}{'?' if optional else ''}"


def _element_sig(collector: Collector, path: tuple[str, ...]) -> str:
    return f"{_kind(collector.stats[path])}{_cardinality(collector, path)}"


def _cardinality(collector: Collector, path: tuple[str, ...]) -> str:
    if len(path) == 1:
        return ""
    parent = path[:-1]
    parent_stats = collector.stats[parent]
    child_seen = parent_stats.child_counts[path[-1]]
    child_count = collector.stats[path].count
    if child_seen == parent_stats.count and child_count == parent_stats.count:
        return ""
    if child_seen < parent_stats.count and child_count == child_seen:
        return "?"
    if child_seen == parent_stats.count:
        return "+"
    return "*"


# -- locators ------------------------------------------------------------

def _element_locator(path: tuple[str, ...]) -> str:
    return f"{_indent(len(path) - 1)}<{path[-1]}>"


def _attr_locator(path: tuple[str, ...], attr: str) -> str:
    return f"{_indent(len(path))}@{attr}"


def _indent(depth: int) -> str:
    return "  " * depth


# -- helpers -------------------------------------------------------------

def _clean_text(text: str) -> str:
    return " ".join(text.split())


def _sample(text: str) -> str:
    if not text:
        return ""
    sample = '"' + text.replace('"', '\\"') + '"'
    return sample[:38] + '…"' if len(sample) > 40 else sample


def _file_size(fh) -> int | None:
    try:
        file_stat = os.fstat(fh.fileno())
        return file_stat.st_size if stat.S_ISREG(file_stat.st_mode) else None
    except (io.UnsupportedOperation, OSError):
        return None



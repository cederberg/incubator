---
drafted: 2026-06-08
updated: 2026-06-09
status: archived
---

# XML Support - Notes

## About this file

- Captures the agreed XML outliner design before implementation.
- Records benchmark findings from real-world XML datasets.
- Records decisions about sampling, indentation, and cardinality.

## Design goal

- XML output should mirror the JSON structural-outline approach.
- XML locators should be structural XML-ish names instead of line ranges.
- XML signatures should use XML-native node kinds, not inferred scalar types.
- The parser should prioritize zero dependencies.
- The default parser path should sample, not stream the full document.

## Output model

- The `/` locator is the document summary line.
- The summary line should report size and syntax only, not the root element.
- The summary line should include sampled element occurrences as
  `sampled N elems`.
- Element rows use `elem`.
- Attribute rows use `attr`.
- Text-only element rows use `text`.
- Mixed-content element rows use `mixed`.
- Element rows use regex-style cardinality suffixes.
- No suffix means exactly one sampled occurrence per sampled parent occurrence.
- `?` means zero or one sampled occurrence per sampled parent occurrence.
- `+` means one or more sampled occurrences per sampled parent occurrence.
- `*` means zero or more sampled occurrences per sampled parent occurrence.
- XML should not emit `int`, `str`, `bool`, `float`, or union types.
- Samples use `--` with truncated text or attribute values.
- Attribute rows use `?` when absent from some sampled element occurrences.
- Attributes are listed before child elements.

Example:

```text
/                                195.5 MB · xml · sampled 204K elems
<PubmedArticleSet>               elem
  <PubmedArticle>                elem+
    <MedlineCitation>            elem
      @Status                    attr -- "MEDLINE"
      <Article>                  elem
        <ArticleTitle>           text -- "Clinical..."
        <Abstract>               mixed
```

## Locator style

- Use indentation to preserve parent context.
- Use `<tag>` for element rows.
- Use `@attr` for attribute rows.
- Do not repeat full parent paths in each locator.
- Do not use `..//Node` shortening in normal output.
- Root element appears as a normal locator row after the `/` summary.

Example:

```text
<health-topics>               elem
  @date-generated             attr -- "06/06/2026 02:30:41"
  @total                      attr -- "2033"
  <health-topic>              elem+
    @id                       attr -- "6308"
    @language                 attr -- "English"
    @meta-desc                attr -- "If you are being tested for Type 2 di…"
```

## Sampling strategy

- Do not define or infer a generic "record" concept before implementation.
- Stop sampling after `1_000_000` start elements or `0.5s`, whichever comes
  first.
- Check elapsed time periodically, not on every parser event.
- Full-document parsing should not be the default outline path.
- A future `--full` mode can be considered later if real use requires it.

## Parser choice

- Use `xml.parsers.expat` from the Python standard library.
- Avoid `lxml` unless a later requirement justifies adding a dependency.
- Avoid SAX unless its API becomes useful for a specific implementation detail.
- Avoid ElementTree for the core path because real-world XML can expose entity
  handling problems.

Observed parser behavior:

- `expat` was the fastest overall in benchmark runs.
- `ElementTree` failed on DBLP because of DTD-defined entities like `&uuml;`.
- `lxml.iterparse` was competitive but adds a dependency.
- SAX was slower than the alternatives.

## Benchmark findings

- DBLP gzip decompression alone took about `3.6-3.8s`.
- DBLP full expat parse through gzip took `39.422s`.
- Therefore roughly `35-36s` of the DBLP run was XML parsing and event handling.
- Full parsing is too expensive for very large dumps.
- Early sampling is cheap enough for interactive use.

Full streaming parse timings:

```text
MedlinePlus topics XML   28 MB   expat 0.172s   ElementTree 0.213s   lxml 0.168s
MeSH descriptors XML    298 MB   expat 2.479s   ElementTree 3.602s   lxml 2.623s
PubMed XML              186 MB   expat 1.450s   ElementTree 2.140s   lxml 1.523s
SimpleWiki bz2          362 MB   expat 28.424s  ElementTree 24.725s  lxml 24.460s
DBLP gzip               1.0 GB   expat 39.422s  ElementTree failed   lxml 48.344s
```

Sampling timings:

```text
DBLP gzip      100K start elements  0.035s
DBLP gzip        1M start elements  0.363s
DBLP gzip        5M start elements  1.709s
SimpleWiki bz2 100K start elements  0.785s
SimpleWiki bz2   1M start elements  3.689s
PubMed XML       1M start elements  0.459s
MeSH XML         1M start elements  0.396s
```

## Namespaces

- Use local prefixes declared in the file when available.
- Do not print namespace URLs in outline output.
- Prefixes such as `id:elem` should remain compact enough for the indented
  locator format.
- Namespace URLs are already available in the XML header for users who need
  them.
- If a namespace has no prefix, use local-name output.

Example:

```text
<feed>
  <atom:entry>
    @xml:lang
```

## Compressed input

- Do not add compressed-file support to the CLI.
- The CLI supports files and stdin.
- Users can pipe decompressed XML into stdin.

Examples:

```bash
gzip -dc dblp.xml.gz | outliner-cli -s xml -
bzip2 -dc simplewiki.xml.bz2 | outliner-cli -s xml -
```

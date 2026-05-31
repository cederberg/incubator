---
drafted: 2026-05-08
status: active
---

# JSON / Data Format Support — Notes

## Structural (path-based) output instead of line ranges

Code files use `start,count` as the "where" because the natural precision tool
is `read(file, start, count)`. For JSON the "where" is a jq path —
`jq '.<path>' file.json` fetches the exact data. The outliner's two-column
output (location, description) should encode whatever precision tool is native
to the format. For XML this means XPath, for HTML CSS selectors.

The `signature` field in `OutlineItem` is poorly named — it's a code-centric
term. Something like `label` or `desc` would be more general.

## JSON format types

JSON data comes in two forms with different characteristics:

**Single-doc JSON** — the whole file is one JSON value (object or array). Often
minified to a single line. Line numbers are meaningless. `json.load()` works up
to roughly 100 MB (a few hundred ms, proportional memory). At ~500 MB it takes
14 seconds and 1.8 GB RAM, which is impractical.

**NDJSON / JSONL** — one JSON object per line, no outer wrapper. Not technically
valid JSON as a whole, but trivial to process line-by-line. Line numbers are
meaningful as record indices (`sed -n '42p'` fetches a record). Used by
real-world datasets (Yelp, GitHub Archive, etc.). The 5 GB review file in the
fixtures is NDJSON with 7 million records.

## Sampling is sufficient for schema inference

For NDJSON, schema from the first 100 lines already captures all distinct keys.
The full 150K-line parse of the business file added nothing. For nested
sub-objects with sparse fields, 5000 lines gives a clear picture of which fields
are common vs rare.

We never need to parse the whole file. Sample 100–1000 lines for structure,
estimate total records from file size divided by average line length (instant,
~1% error) rather than counting lines via streaming (2.4s for 5 GB) or
`read().count('\n')` (OOM for 5 GB).

## Optional vs always-present fields

For schema output, the mandatory/optional split is informative enough. Reporting
exact percentages ("3.8%") is overkill — just mark which fields are sometimes
omitted. The sparsity pattern is visible within the first few thousand lines.

## First-line summary

A JSON file should show a one-line summary at the top: character count, format
type (single-doc vs NDJSON/JSONL), top-level type (object/array), array length
if applicable. This tells the reader what kind of JSON they're dealing with and
which tools to use.

## Current architecture doesn't support large files

CLI reads the entire file into memory before any parsing (`fh.read()` at line 82
of `cli.py`). If `.json` were registered in `EXTENSIONS`, a directory walk
hitting a 5 GB NDJSON file would allocate 5 GB and likely OOM. The parser
interface `parse(text: str)` couples file I/O to parsing.

### No custom wrapper needed — TextIOWrapper.seek(0) is fine

The simplest fix requires no custom IO wrapper. Python's `TextIOWrapper`
supports `seek(0)` — it resets to the start of the file, regardless of encoding
and file size. So the CLI just does:

```python
with open(src, encoding="utf-8", errors="replace") as fh:
    head = fh.read(4096)          # 4K chars for detection (~16 KB worst case)
    syntax = args.syntax or detect(head)
    fh.seek(0)                    # back to start, O(1)
    items = outline(syntax, fh)   # pass handle — parser decides how to read
```

Code parsers get a handle and call `fh.read()` immediately (same as before).
JSON parser reads incrementally. Stdin can't seek, but we keep the existing
`sys.stdin.read()` for stdin — stdin being multi-GB is not a practical concern.

A `_PrependReader` wrapper that splices the head and tail into a seamless stream
was considered but is unnecessary: it would need binary wrapping and encoding
juggling, and `seek(0)` already solves it.

Extension registration for `.json`/`.xml` must wait until the streaming read
path is in place.

## Scalar type consistency

JSON values within arrays of objects often have consistent types per field, but
not always. The Titanic fixture has `Age` as int and `Cabin` as null, while
fields like `attributes` in the Yelp business data are sometimes `null` and
sometimes `object`. The outliner should report the type(s) observed per field.

## YAML

Simpler subset of the JSON approach. Parse whole file (large YAML files are
rare), show key paths with types. Low priority — the value is marginal and
--grep use cases are unlikely.

## XML

Very similar to JSON in structure. XPath-based location keys. Element paths with
attributes, text content types, nesting depth.

## Benchmarks

Parsing 1000 NDJSON lines, including schema extraction: ~3 ms. Parsing 100K
NDJSON lines: ~430 ms. json.loads on a 65 MB single-doc string: ~370 ms.
json.loads on a 522 MB single-doc string: 14.3 s, 1.8 GB peak memory. Line
counting via `sum(1 for _ in f)` on 5 GB: 2.4 s.

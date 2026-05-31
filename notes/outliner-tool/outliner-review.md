---
drafted: 2026-04-29
status: archived
---

# Outliner — Code Review Notes

From code review session, April 2026. Source is 2213 lines across 14 files;
tests are 5352 lines across 16 files.

## Source Code Duplication

### `_collect_sig` — defined 10 times (one per language parser)

The core loop is structurally identical across java, rust, c, csharp, swift,
php, javascript, go, python, ruby: count `(` / `)`, collect stripped parts,
break on condition, call `extract_signature`. Candidates for consolidation:

- **java + rust**: nearly identical — only differ in end-condition check and a
  Rust-specific where-clause cleanup. Could share a `collect_paren_sig` utility
  in `util.py`, with rust adding the comma-cleanup on top. Saves ~20 lines.
- **csharp + swift**: both have the "look-ahead for `{` on next non-blank line"
  pattern with a `paren_opened` flag. Only real difference: C# strips `=>.*$`,
  Swift strips `{.*$`. A shared base with a strip-regex parameter would collapse
  two 41-line functions into one.
- go, javascript, php, c, python, ruby have justified differences and should
  stay separate.

### 4-line item-append pattern — repeated ~25 times

This sequence appears nearly verbatim throughout every brace-language parser:

```python
sig, sig_end, has_body = _collect_sig(lines, i)
start = seek_comment_start(lines, i, pred)
end = seek_brace_end(lines, sig_end) if has_body else sig_end + 1
items.append(OutlineItem(start=start + 1, count=end - start, signature=sig))
```

Appears in c.py (3×), csharp.py (4×), java.py, javascript.py (7×), rust.py,
swift.py, php.py, go.py (2×). A `make_item` utility in `util.py` would be the
highest-leverage consolidation in the project.

### `_is_comment_line` / `_is_walkback_line` — defined 5 times

c.py, csharp.py, javascript.py, php.py, and swift.py each define a near-
identical 2–6 line predicate checking for `//`, `/*`, `*`. Differences:

- csharp adds `///` and `[` (attributes)
- javascript/swift add `@` (decorators)
- php adds `#`

A shared `is_clike_comment(line, s, *, attrs=False, hash=False, at=False)` in
`util.py` would replace all five, and the inline lambdas in go/java/rust could
migrate to it too.

### `_STMT_START_RE` and `_CONTROL_FLOW` — defined independently in 4 parsers

c.py, csharp.py, java.py, javascript.py each define `_STMT_START_RE` with
overlapping keywords (`return`, `throw`, `break`, `continue` in all four).
`_CONTROL_FLOW` frozensets in java and csharp share most content. Could share a
base set with per-language additions, but low priority.

### `javascript.py`: `_collect_const_sig` duplicates `_collect_sig`

`_collect_const_sig` (lines 171–200) is `_collect_sig` with an extra `found_eq`
gate. ~20 identical lines. Could be unified with a `require_eq` parameter,
saving ~30 lines in the largest and most complex parser.

## Parser Complexity Assessment

| File          | Lines | Notes                                                   |
| ------------- | ----- | ------------------------------------------------------- |
| javascript.py | 358   | Justified: 7 declaration forms + TS negation logic      |
| c.py          | 304   | Justified: `_is_func_line` heuristics unavoidable       |
| csharp.py     | 287   | Property detection (`_is_property_line`) adds real bulk |
| swift.py      | 150   | Reasonable; similar structure to C# at half lines       |
| rust.py       | 89    | Very clean; `_ALL_DECLS` list pattern is good           |
| go.py         | 83    | Exemplary — minimal and clear                           |

C#'s `_is_property_line` (lines 148–171) is 24 lines for a feature that exists
to handle a handful of false-positive cases. Worth revisiting if it causes
ongoing maintenance.

## Test Duplication

### Fixture re-reads — 13–22 disk reads per test run per file

Every fixture test calls `parse(FIXTURE.read_text())` independently:

- test_rust.py: 22 calls
- test_java.py: 22 calls
- test_csharp.py: 13 calls

A module-scoped pytest fixture would read the file once:

```python
@pytest.fixture(scope="module")
def items():
    return parse(FIXTURE.read_text())
```

### `sigs = [it.signature for it in items]` — repeated throughout fixture tests

Appears ~40+ times across files. If `items` is a fixture, `sigs` could be a
derived fixture or the pattern could be a small helper.

### Boilerplate edge cases

Every test file has `test_empty_file` (`assert parse("") == []`) and
`test_only_comments`. Could be parameterized via `conftest.py` but the current
approach is also fine — they're short and confirm the contract locally.

## Actionable Items (roughly by impact)

1. Extract `make_item` utility — collapse 25 call sites of the 4-line append
   pattern. Highest leverage, lowest risk.
2. Merge `_collect_const_sig` into `_collect_sig` in javascript.py — saves ~30
   lines in the largest file.
3. Merge java + rust `_collect_sig` into a shared utility in `util.py`.
4. Merge csharp + swift `_collect_sig` — nearly identical except body-strip
   regex.
5. Shared `is_clike_comment` predicate in `util.py` — replaces 5 near-identical
   per-file definitions.
6. Module-scoped fixture in tests — eliminates 50+ redundant disk reads.

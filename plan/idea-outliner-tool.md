# Outliner Tool

A fast CLI tool that prints the structural outline of a source file —
declarations with line ranges — so an agent (or human) can navigate a file
without reading it whole.

## Command-line

```
outline <file>
```

## Output

```
#3:1   package driver
#5:8   import (...)
#14:4  type Driver struct {
#19:6  func New() *Driver {
#26:12 func (d *Driver) StartLogging(...) error {
```

Format: `#<start-line>:<line-count>  <signature-line>`

The range covers the full declaration including preceding doc comments, so
`Read(file, offset=26, limit=12)` fetches the complete item.

## Notes

**Problem it solves:** In long agent sessions, files get re-read repeatedly and
looking up a single API signature requires ingesting hundreds of lines.
Outline-first navigation would replace most full reads with one cheap outline +
one targeted read.

**Why not the existing Read tool:** Read has `offset`/`limit` but you need to
know the range first. Grep finds text but not structure.

**Human analogy is imperfect:** Agents don't have attention fatigue; more
context is generally better. The real cost is context-window efficiency, not
distraction.

**Format rationale:** `#line:count` gives the exact slice to pass to Read. No
doc comments in output — those are fetched on demand.

**Scope:** ~20–30 common text-based formats. Go, Python, Markdown, YAML/JSON,
shell scripts. Format dispatch on file extension.

**Implementation ideas:**

- Go files: use `go/ast` for exact ranges including doc comments (~40–50 lines)
- Everything else: regex heuristics per format; brace-counting not needed for
  most
- Single Go binary; fast, no runtime deps

**Potential issues:**

- Multi-line function signatures (Go, Rust): print just the opening line or
  merge?
- Interface method bodies: indent under type or omit?
- `var`/`const` blocks: opener only, or each identifier?
- Deeply nested formats (e.g. JSON) may produce noisy output

**Recursive outlining:** Out of scope for this tool. `find` or `fd` already
provides filesystem outlines; an agent can call `outline` on any interesting
files found. Relevant mainly when comparing against Aider's repo map, which does
whole-repo ranking in one shot.

## Related Tools

Evaluated on Ubuntu 22.04 against `driver/driver.go` (275 lines, Go) and
`README.md` from `baraverkstad/docker-journald-plus`, plus a GitHub Actions YAML
file. The key criterion is whether a tool produces full-body line ranges
suitable for `Read(file, offset=X, limit=Y)` with acceptable signal-to-noise.

### universal-ctags

**Install:** `apt install universal-ctags` / `brew install universal-ctags`

```
ctags --output-format=json --fields=+ne -o - <file>
```

JSON per symbol with `line`, `end` (closing-brace line), kind, and source
pattern. Line count = `end - line + 1`. Closest existing tool to this proposal.

**Pros:**

- Easy install, no runtime deps, very fast
- Accurate full-body ranges for Go — all top-level types and functions present:
  `consumeLog` → `#173:91`, `Driver` struct → `#16:5`
- Markdown headings output as `chapter`/`section`/`subsection` kinds with ranges
- `kind` field allows straightforward filtering

**Cons:**

- Noisy: struct fields (`mu`, `consumers`, `sendFn`, …) appear as
  `kind:"member"` alongside top-level declarations; must filter by kind
- Doc comments excluded from ranges — `New()` at line 36 has its comment at line
  35; ctags reports `line:36`, so `Read(offset=36, limit=3)` misses it
- Import blocks never tagged
- No YAML support — `.yml` files produce no output at all

**Verdict:** Needs a ~20-line wrapper to filter kinds, compute counts, and walk
back one line for doc comments. YAML needs a separate approach. The closest
starting point for building this tool.

---

### tree-sitter

**Install:** `npm install -g tree-sitter-cli`; grammars must be cloned
separately

```
tree-sitter tags <file>
```

Grammar-based symbol extractor. Each language requires its grammar repo cloned
into a directory listed in `~/.config/tree-sitter/config.json`.

**Pros:**

- Broad grammar ecosystem (Go, Rust, Python, TypeScript, etc.)
- Includes doc-comment snippets in output for `def` entries

**Cons:**

- Extremely noisy: a 275-line Go file produces ~150 tag lines, mixing
  declarations, type references, and call sites — most lines are noise:
  ```
  Mutex      | type ref (16,16)-(16,21) `mu        sync.Mutex`
  consumeLog | call ref (118,6)-(118,16) `go d.consumeLog(ctx, f, lc)`
  ```
- Range is the **identifier's column span only**, not the full declaration body
  — `Driver` reports `(15,5)-(15,11)` (the name characters), making `Read`
  ranges impossible to derive without custom Scheme queries (`tags.scm`) per
  language
- Markdown and YAML grammars exist but ship no `tags.scm`; `tree-sitter tags`
  produces nothing for them
- More setup friction than ctags with less usable output

**Verdict:** Unusable without custom per-language query work. The range
fundamental is wrong for this use case.

---

### ast-grep

**Install:** `cargo install ast-grep` (requires Rust toolchain)

```
ast-grep run -p '<pattern>' --json <file>
```

Tree-sitter-based pattern matcher. No built-in "outline" mode — requires
separate invocations per construct type.

**Pros:**

- Full-body JSON ranges (0-indexed), accurate with no noise: `consumeLog` →
  start=172, end=262 → `#173:91 ✓`
- Patterns are language-aware; no false positives

**Cons:**

- No single outline command — a complete Go outline needs at least three
  patterns:
  ```bash
  ast-grep run -p 'func $NAME($$$) $$${ $$$}' --json file.go   # functions
  ast-grep run -p 'func ($R $T) $NAME($$$) $$${ $$$}' --json   # methods
  ast-grep run -p 'type $NAME struct { $$$}' --json             # structs
  ```
  Results from separate runs must be merged and sorted by line number
- Doc comments still excluded (pattern anchors to `func`/`type` keyword)
- YAML and Markdown need patterns written from scratch
- `/usr/bin/sg` on Ubuntu 22.04 is `newgrp` (unrelated system tool); must use
  full path `~/.cargo/bin/ast-grep`

**Verdict:** More wrapper work than ctags but avoids kind-filtering noise. A
viable base if you're willing to maintain per-language pattern sets.

---

### lsp-cli

**Install:** `npm install -g @mariozechner/lsp-cli`

```
lsp-cli <directory> <language> output.json
```

Wraps LSP `textDocument/documentSymbol` to index a directory. Auto-downloads the
required language server on first run. Explicitly targets LLM/agent use cases
("must be preferred to grep").

**Pros:**

- Accurate full-body ranges via LSP `range` field
- Doc comments captured in a separate `documentation` field (JSDoc/JavaDoc/etc.)
- Hierarchical output (methods nested under classes)
- Covers Java, C, C++, C#, Haxe, TypeScript, Dart

**Cons:**

- Noisy: class members (constructors, methods, properties) all appear as
  children — a 3-method class produces 7 child entries including constructor
  params and fields
- Doc comment text is in `documentation`, not reflected in the `range`; the
  range itself still starts at the declaration keyword
- Output is a JSON file, not stdout — requires a separate read step
- No Go, Python, Markdown, or YAML support
- Slower startup: downloads and spawns an LSP server per analysis run
- Requires `tsconfig.json` for TypeScript (warns without it and may miss
  symbols)

**Verdict:** Purpose-built for LLM navigation but limited to 7 languages (no
Go). The per-file outline use case is a poor fit: it indexes whole directories,
outputs to a file, and is noticeably slower than ctags.

---

### Aider repo map

Whole-repo structural outline ranked by cross-reference importance. Not a
standalone CLI — baked into Aider's LLM infrastructure, which uses ctags
internally.

**Pros:**

- Repo-level overview in one shot
- Symbols ranked by how often they are referenced

**Cons:**

- **No line numbers or ranges** — output uses `⋮...` ellipsis notation; cannot
  derive `Read(offset=X, limit=Y)` calls
- Not extractable as a standalone tool
- Could not be installed in the test environment (`pip install aider-chat`
  produced no working binary)

**Verdict:** Not applicable as a line-range outliner. Relevant only when
comparing whole-repo symbol ranking against per-file outline.

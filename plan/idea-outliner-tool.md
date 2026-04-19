# Outliner Tool

A fast CLI tool that prints the structural outline of a source file — declarations
with line ranges — so an agent (or human) can navigate a file without reading it
whole.

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
looking up a single API signature requires ingesting hundreds of lines. Outline-first
navigation would replace most full reads with one cheap outline + one targeted read.

**Why not the existing Read tool:** Read has `offset`/`limit` but you need to
know the range first. Grep finds text but not structure.

**Human analogy is imperfect:** Agents don't have attention fatigue; more context
is generally better. The real cost is context-window efficiency, not distraction.

**Format rationale:** `#line:count` gives the exact slice to pass to Read. No doc
comments in output — those are fetched on demand.

**Scope:** ~20–30 common text-based formats. Go, Python, Markdown, YAML/JSON,
shell scripts. Format dispatch on file extension.

**Implementation ideas:**
- Go files: use `go/ast` for exact ranges including doc comments (~40–50 lines)
- Everything else: regex heuristics per format; brace-counting not needed for most
- Single Go binary; fast, no runtime deps

**Potential issues:**
- Multi-line function signatures (Go, Rust): print just the opening line or merge?
- Interface method bodies: indent under type or omit?
- `var`/`const` blocks: opener only, or each identifier?
- Deeply nested formats (e.g. JSON) may produce noisy output

**Recursive outlining:** Out of scope for this tool. `find` or `fd` already
provides filesystem outlines; an agent can call `outline` on any interesting
files found. Relevant mainly when comparing against Aider's repo map, which
does whole-repo ranking in one shot.

## Investigate

Compare each tool's output against the proposed format — specifically whether
line numbers and line counts (ranges) are present. Several likely omit one or both.

Agents evaluating these tools run on Ubuntu 22.04 LTS (Claude Code web).

**universal-ctags**
— `brew install universal-ctags` / `apt install universal-ctags`

```
ctags --output-format=json --fields=+ne -o - <file>
```

JSON per symbol with `line`, `end`, kind, and source pattern. Line count =
`end - line`. Closest existing tool; needs a small formatter script.

**tree-sitter** — `brew install tree-sitter` / build from source on Ubuntu

```
tree-sitter tags <file>
```

Outputs name, kind, row:col range, source snippet. Requires per-language grammar
setup. Cleaner output but less turnkey.

**ast-grep** — `brew install ast-grep` / `cargo install ast-grep`

```
sg run -p '$FUNC' --json <file>
```

Tree-sitter-based; outputs JSON with start/end line and matched text. Needs a
pattern per symbol type — not push-button, but scriptable and precise. Has
dedicated AI tooling docs.

**Aider repo map** — `pip install aider-chat` (macOS and Ubuntu)

Whole-repo structural outline ranked by symbol importance. Uses `⋮...` ellipsis
for omitted bodies; no line numbers. Not a standalone tool; baked into Aider.
Most relevant for evaluating recursive/repo-wide outlining.

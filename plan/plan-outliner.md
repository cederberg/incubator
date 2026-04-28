# Outliner Tool — Implementation Plan

A fast CLI tool (`outline <file>`) that prints the structural outline of a
source file — declarations with line ranges — so an LLM agent (or human) can
navigate a file without reading it whole.

## Output Format

```
 3,4   type Driver struct
19,6   func New() *Driver
26,12  func (d *Driver) StartLogging(ctx context.Context, f *os.File) error
```

Each line: `<start>,<count>  <signature>`

- `start` is 1-based, right-aligned across all items in the file
- `count` is the number of lines; the whole `start,count` field is padded with
  trailing spaces so signatures align in a single column
- `signature` is the declaration's first non-comment line with leading/trailing
  whitespace stripped; trailing `{` removed; no truncation
- Multi-line signatures (e.g. a function with arguments spanning several lines)
  are merged into a single line for better searchability

### Long-range items

Some items naturally span large ranges that contain other items:

- **Markdown headings** — an `##` section runs until the next `##`, covering
  every sub-heading and paragraph inside it
- **Java / C# classes** — the class declaration spans the entire body including
  all methods
- **Go / Rust `impl` blocks** — span all methods within

These overlapping ranges are intentional and useful: the agent can read the
whole section/class in one call, or navigate to a specific method within it. The
output is sorted by start line. Nesting is expressed in two complementary ways:
overlapping ranges (a class range contains its methods' ranges) and native-format
indentation in the signature — indentation for code files, ATX heading levels
(`#`, `##`, …) for Markdown.

### Multi-file output

When more than one file is given, a header line precedes each file's outline,
with one blank line before it:

```
==> driver.go <==
 3,4   type Driver struct
19,6   func New() *Driver

==> util.go <==
1,12  func ParseFlags() *Config
```

## Command-Line Interface

```
outline [OPTIONS] [FILE...]
```

| Option              | Description                                         |
| ------------------- | --------------------------------------------------- |
| `-g, --grep EXPR`   | Only show items whose signature matches EXPR        |
| `-s, --syntax LANG` | Override syntax auto-detection when it is ambiguous |

With no `FILE` arguments, reads from stdin. Explicitly passing `-` also reads
stdin. `--syntax` is required for stdin since there is no filename to detect
from, and may be needed for any file where auto-detection is unreliable (e.g.
extensionless scripts, or `.h` files that could be C or C++).

## Design Decisions

- **TDD**: implement each parser red-green with pytest — write a failing test
  against a fixture file first, then make it pass.
- **Doc-comment inclusion**: The start line walks back past blank lines and
  `//`, `#`, `--`, `/**` etc. comment blocks so
  `Read(offset=start, limit=count)` fetches the whole item including docs.
- **Signatures**: Leading/trailing whitespace stripped; trailing `{` stripped.
  Multi-line signatures are joined into one line (whitespace-normalised).
- **Import statements**: Always excluded from output.
- **Module globals / constants**: Excluded — module-level variable assignments
  are more noise than signal when outlining a codebase. This may be revisited.
- **Blocks** (`var (...)`): Print the opener as one item.
- **Class members**: Always included — the tool outlines the whole file.
- **Plain text**: Treat as Markdown (heading lines only).
- **Content auto-detection**: Each parser implements `detect(lines)` that
  returns True/False based on file content. Detection must be
  **conservative**: use language-specific co-occurring markers, never a single
  generic keyword. `class`, `def`, `function`, `module`, etc. appear in many
  languages and must never be used as sole detection signals. Good markers:
  Go requires both `package` and `func`/`type`; Python checks that
  `def`/`class` lines end with `:` (not `{`). When uncertain, prefer false
  negative (fall through to next detector) over false positive (misidentify
  the file). Markdown's `detect()` always returns True and is registered last
  as a catch-all fallback.

## Project Layout

```
outliner/
  pyproject.toml          # uvx-compatible packaging
  src/
    outliner/
      parsers/            # one module per language
  tests/
    fixtures/             # sample source files per language
```

## Implementation Tasks

### Infrastructure

- [x] Initialise `outliner/` Python project (`pyproject.toml`, `uvx` entry
      point)
- [x] `types.py` — `OutlineItem` dataclass
- [x] `cli.py` — `--grep`, `--syntax`, multi-file + stdin support
- [x] `tests/test_cli.py` — smoke tests for CLI entry point

### Language Parsers (each with fixture + TDD red-green tests)

Order reflects: user priority first, then complex/weird syntaxes early (to
surface output format edge cases), then remaining popular languages. JSON and
YAML are deferred to last as their output format needs separate design thought.

- [x] **Markdown** (`parsers/markdown.py`) — ATX/Setext headings with nesting;
      simplest parser, good baseline for understanding the output format
- [x] **reStructuredText** (`parsers/rst.py`) — underline/overline headings with
      any decoration character (`= - ~ ^ * + # < >`); level determined by
      order of first appearance; `.rst`/`.rest` extensions + content detection
- [x] **Python** (`parsers/python.py`) — regex-based; functions, classes,
      methods
- [x] **Go** (`parsers/go.py`) — func, method, type, const/var blocks;
      multi-line signature merging
- [x] **Java** — class/interface/enum/record, constructor, method; annotation
      type declaration (`@interface`); annotations as modifiers
- [x] **Rust** — fn, impl, struct, enum, trait, mod, type alias;
      lifetime/generic handling
- [x] **JavaScript/TypeScript** — function declaration, class; top-level
      function-valued `const`/`let` (arrow functions, class expressions) but
      not plain value assignments; TypeScript: interface, type alias, enum,
      namespace, decorators; `.js`/`.jsx`/`.ts`/`.tsx` extensions
- [x] **C/C++** — function definitions, struct/class/enum, namespace (C++),
      `#define` macros, template declarations
- [x] **C#** — namespace, class/interface/struct/enum/record, method, property,
      attributes
- [x] **Swift** — func, class/struct/enum/protocol/actor, extension
- [x] **Ruby** — module, class, def, attr\_\*
- [x] **PHP** — namespace, function, class/interface/trait/enum, method
- [x] **Shell/Bash** — function definitions (both syntaxes: `name()` and
      `function name`)
- [ ] **Perl** — package, sub
- [ ] **Zig** — fn, struct/enum/union; top-level `const` only where value is a
      type or function (not plain numeric/string constants)
- [ ] **Scala** — def, class/case class/object/trait, given/extension (Scala 3)
- [ ] **Clojure** — ns, defn, defmacro, deftype, defrecord, defprotocol,
      defmulti, def; S-expression structure
- [ ] **Elixir** — defmodule, def/defp, defmacro, defprotocol, defimpl,
      `@spec`-aware; multiple-clause functions
- [ ] **Erlang** — `-module`, function clauses (name/arity), `-spec`, `-type`,
      `-record`
- [ ] **Haskell** — module, top-level type sigs (`name ::`) + definitions,
      data/newtype/type, class/instance
- [ ] **Kotlin** — fun, class/data class/sealed class/object/interface,
      typealias
- [ ] **Lua** — local/global function definitions
- [ ] **R** — function assignments (`name <- function`)
- [ ] **OCaml** — let/let rec, type, module, module type
- [ ] **F#** — let/let rec, type, module
- [ ] **Dart** — class/mixin/extension, function
- [ ] **YAML** — TBD
- [ ] **JSON** — TBD
- [ ] **XML** — TBD
- [ ] **HTML** — TBD
- [ ] **AsciiDoc** — `=`-prefixed headings (like ATX but with `=` and `==`),
      section titles; `.adoc`/`.asciidoc` extensions
- [ ] **Org-mode** — `*`-prefixed headings (`*`, `**`, …); widely used in
      Emacs / literate-programming workflows; `.org` extension
- [ ] **LaTeX** — `\chapter`, `\section`, `\subsection`, `\subsubsection`;
      `.tex` extension

### Polish

- [x] `README.md` for the `outliner/` package

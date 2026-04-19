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
output is sorted by start line; nesting is visible from the ranges alone.

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
- **Blocks** (`var (...)`): Print the opener as one item.
- **Class members**: Always included — the tool outlines the whole file.
- **Plain text**: Treat as Markdown (heading lines only).

## Project Layout

```
outliner/
  pyproject.toml          # uvx-compatible packaging
  src/
    outliner/
      __init__.py
      cli.py              # entry point
      types.py            # OutlineItem dataclass, Kind enum
      autodetect.py       # extension/shebang → syntax name
      parsers/
        __init__.py
        python.py
        markdown.py
        go.py
        rust.py
        javascript.py
        typescript.py
        java.py
        haskell.py
        clojure.py
        elixir.py
        erlang.py
        c_cpp.py
        csharp.py
        swift.py
        kotlin.py
        scala.py
        ruby.py
        php.py
        shell.py
        lua.py
        perl.py
        r_lang.py
        ocaml.py
        fsharp.py
        dart.py
        zig.py
        yaml_parser.py
        json_parser.py
  tests/
    fixtures/             # sample source files per language
    test_cli.py
    test_markdown.py
    test_python.py
    test_go.py
    test_rust.py
    test_haskell.py
    test_clojure.py
    test_javascript.py
    test_typescript.py
    test_java.py
    test_c_cpp.py
    test_csharp.py
    test_elixir.py
    test_erlang.py
    test_swift.py
    test_kotlin.py
    test_scala.py
    test_ruby.py
    test_php.py
    test_shell.py
    test_lua.py
    test_perl.py
    test_r_lang.py
    test_ocaml.py
    test_fsharp.py
    test_dart.py
    test_zig.py
    test_yaml.py
    test_json.py
```

## Implementation Tasks

### Infrastructure

- [x] Initialise `outliner/` Python project (`pyproject.toml`, `uvx` entry
      point)
- [x] `types.py` — `OutlineItem` dataclass
- [x] `autodetect.py` — extension/shebang → syntax name
- [ ] `autodetect.py` — content-based fallback (detect RST by underline
      pattern, etc.) when extension is absent or ambiguous
- [x] `cli.py` — `--grep`, `--syntax`, multi-file + stdin support
- [x] `tests/test_cli.py` — smoke tests for CLI entry point

### Language Parsers (each with fixture + TDD red-green tests)

Order reflects: user priority first, then complex/weird syntaxes early (to
surface output format edge cases), then remaining popular languages. JSON and
YAML are deferred to last as their output format needs separate design thought.

- [x] **Markdown** (`parsers/markdown.py`) — ATX/Setext headings with nesting;
      simplest parser, good baseline for understanding the output format
- [ ] **reStructuredText** (`parsers/rst.py`) — underline/overline headings with
      any decoration character (`= - ~ ^ * + # < >`); level determined by
      order of first appearance; add `.rst` to autodetect
- [ ] **Python** (`parsers/python.py`) — use `ast` module; functions, classes,
      methods, module-level assignments
- [ ] **Go** (`parsers/go.py`) — func, method, type, const/var blocks;
      multi-line signature merging
- [ ] **Rust** (`parsers/rust.py`) — fn, impl, struct, enum, trait, mod;
      lifetime/generic handling
- [ ] **Haskell** (`parsers/haskell.py`) — module, top-level type sigs
      (`name ::`) + definitions, data/newtype/type, class/instance
- [ ] **Clojure** (`parsers/clojure.py`) — ns, defn, defmacro, deftype,
      defrecord, def; S-expression structure
- [ ] **JavaScript** (`parsers/javascript.py`) — function, arrow function,
      class, const/let/var at top level
- [ ] **TypeScript** (`parsers/typescript.py`) — extends JS; interface, type
      alias, enum, decorators
- [ ] **Java** (`parsers/java.py`) — class/interface/enum, method signatures,
      annotations
- [ ] **C/C++** (`parsers/c_cpp.py`) — function definitions, struct/class/enum,
      `#define` macros, template lines
- [ ] **C#** (`parsers/csharp.py`) — namespace, class/interface/enum, method,
      property, attributes
- [ ] **Elixir** (`parsers/elixir.py`) — defmodule, def/defp, defmacro,
      `@spec`-aware; multiple-clause functions
- [ ] **Erlang** (`parsers/erlang.py`) — `-module`, function clauses
      (name/arity), `-spec`
- [ ] **Swift** (`parsers/swift.py`) — func, class/struct/enum/protocol,
      extension, top-level var/let
- [ ] **Kotlin** (`parsers/kotlin.py`) — fun, class/object/interface, top-level
      val/var
- [ ] **Scala** (`parsers/scala.py`) — def, class/object/trait, case class,
      top-level val/var
- [ ] **Ruby** (`parsers/ruby.py`) — module, class, def, attr\_\*
- [ ] **PHP** (`parsers/php.py`) — namespace, function, class/interface/trait,
      method
- [ ] **Shell/Bash** (`parsers/shell.py`) — function definitions (both syntaxes)
- [ ] **Lua** (`parsers/lua.py`) — local/global function definitions
- [ ] **Perl** (`parsers/perl.py`) — package, sub
- [ ] **R** (`parsers/r_lang.py`) — function assignments (`name <- function`)
- [ ] **OCaml** (`parsers/ocaml.py`) — let/let rec, type, module
- [ ] **F#** (`parsers/fsharp.py`) — let/let rec, type, module
- [ ] **Dart** (`parsers/dart.py`) — class/mixin/extension, function, top-level
      variables
- [ ] **Zig** (`parsers/zig.py`) — fn, struct/enum/union, top-level const/var
- [ ] **YAML** (`parsers/yaml_parser.py`) — TBD
- [ ] **JSON** (`parsers/json_parser.py`) — TBD

### Polish

- [ ] `README.md` for the `outliner/` package

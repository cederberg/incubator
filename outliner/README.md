# outliner

Print the structural outline of source files — declarations with line ranges —
so an LLM agent (or human) can navigate a file without reading it whole.

## Usage

```
outliner [OPTIONS] [FILE...]
```

| Option              | Description                                                     |
| ------------------- | --------------------------------------------------------------- |
| `-g, --grep EXPR`   | Only show items whose signature matches EXPR (case-insensitive) |
| `-s, --syntax LANG` | Override syntax auto-detection when it is ambiguous             |

Pass a file, a directory (walked recursively), or omit arguments to read stdin.
Use `-` to read stdin explicitly. `--syntax` is only needed when content
auto-detection cannot identify the language (e.g. an ambiguous extensionless
script piped on stdin).

## Output

```
 3,4   type Driver struct
19,6   func New() *Driver
26,12  func (d *Driver) StartLogging(ctx context.Context, f *os.File) error
```

Each line: `<start>,<count>  <signature>`

- `start` — 1-based line number, right-aligned
- `count` — number of lines covered by the item (including doc-comments above)
- `signature` — first non-comment line of the declaration; multi-line signatures
  are merged into one line

Nesting is visible in two ways: overlapping ranges (a class range contains its
methods) and native-format indentation in the signature (indented for code,
`#`/`##` heading levels for Markdown).

## Running

The tool is not yet published to PyPI. Run it directly from this repository
using [uv](https://docs.astral.sh/uv/):

```sh
# From within the outliner/ directory
uv run outliner path/to/file.py

# From the repository root
uv run --project outliner outliner path/to/file.py

# Outline an entire directory
uv run --project outliner outliner src/
```

## Running Tests

```sh
# From within the outliner/ directory
uv run pytest
```

## Supported Languages

Python, Go, Markdown, reStructuredText — with Java, Rust, JavaScript/TypeScript,
C/C++, C#, and many more in progress.

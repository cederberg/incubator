# outliner

Print the structural outline of source files — declarations with line ranges —
so an LLM agent (or human) can navigate a file without reading it whole.

## Usage

```
outliner-cli [OPTIONS] [FILE...]
```

| Option              | Description                                                                   |
| ------------------- | ----------------------------------------------------------------------------- |
| `-g, --grep EXPR`   | Only show items whose signature matches EXPR (case-insensitive)               |
| `-s, --syntax LANG` | Override syntax auto-detection when it is ambiguous                           |
| `-w, --width COLS`  | Truncate output lines to COLS (`0`=unlimited, `auto`=terminal, default=`120`) |

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
  are merged into one line; lines longer than the output width are truncated
  with `...`

Nesting is visible in two ways: overlapping ranges (a class range contains its
methods) and native-format indentation in the signature (indented for code,
`#`/`##` heading levels for Markdown).

## Installation

```sh
pip install outliner
```

## Running

```sh
# With the package installed (pip or uvx):
uvx outliner-cli path/to/file.py

# From within the outliner/ directory
uv run outliner-cli path/to/file.py
```

## Running Tests

```sh
# From within the outliner/ directory
uv run pytest
```

## Supported Languages

AsciiDoc, C/C++, C#, Clojure, Go, HTML, Java, JavaScript/TypeScript, Markdown,
Org-mode, Perl, PHP, Python, reStructuredText, Ruby, Rust, Scala, Shell, Swift,
and Zig.

## Example Use Cases

**Structural overview** — Run on a directory to see all declarations across many
files before reading anything:

```
$ uvx outliner-cli src/
==> src/billing.py <==
 12,8   class Invoice
 22,4   def create(customer_id: str, items: list[Item]) -> Invoice
 38,6   def send(invoice: Invoice, method: str) -> bool

==> src/payments.py <==
  8,3   class PaymentMethod
 14,12  def charge(method: PaymentMethod, amount: Decimal) -> Receipt
```

**Find all copies of a pattern** — `--grep serialize` across a source tree
locates every implementation of a repeated function in one command:

```
$ uvx outliner-cli --grep serialize src/
==> src/invoice.py <==
 44,5   def serialize(self) -> dict

==> src/receipt.py <==
 31,3   def serialize(self) -> dict
```

**Find functions whose interface mentions a term** — `--grep` searches
signatures, not bodies. It finds functions whose interface involves a concept,
skipping internal uses, comments, and call sites:

```
$ uvx outliner-cli --grep payment src/
 14,12  def charge(method: PaymentMethod, amount: Decimal) -> Receipt
 61,4   def refund(payment: Payment) -> bool
```

**Find functions accepting a specific type** — `--grep PaymentMethod` locates
every function where the type appears in parameters, return types, or generic
bounds. Multi-line signatures are merged into a single line before matching, so
nothing is missed:

```
$ uvx outliner-cli --grep PaymentMethod src/
 14,12  def charge(method: PaymentMethod, amount: Decimal) -> Receipt
 88,4   def validate(m: PaymentMethod) -> bool
```

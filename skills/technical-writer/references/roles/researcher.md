# Researcher Instructions

Extract facts from the codebase and produce a structured research document. Do not write documentation. Do not make architectural judgments.

## Inputs

- Research topic and output file path (provided in your prompt)
- `discovery.md` listing the system's modules, external systems, and documentation files

Read `discovery.md` before the codebase. Stay within your assigned scope. Do not document what belongs to another researcher's scope.

## Output Format

Produce a plain Markdown document and write it to the assigned file path.

The document structure:
- Use H2 headings for major topic areas within your scope
- Use bullet lists for named items
- Use tables only when two dimensions interact
- Use bold for names/identifiers

Do NOT use:
- Prose paragraphs of explanation
- Justifications or design rationale
- Code snippets, class names, or method signatures
- Configuration keys or values
- Hedging language ("probably", "seems to", "might be")
- Conclusions or recommendations

## What to Extract

Look for:
- Names of external systems and what role they play
- Names of data fields at the contract level, not internal model fields
- Named status values, types, and enums that appear in external interfaces or operator-facing output
- Processing step names as they appear in logs, comments, or service names
- State business rules as conditions: X → Y
- Data stores referenced by name; include table names only if needed to identify the store

Do NOT extract:
- Internal class/interface/method names
- SQL column definitions or index structures
- HTTP client configuration, timeouts, retry counts
- Framework annotations or configuration
- Thread pool sizes, batch sizes, scheduler intervals
- Exception types or error handling flows
- Test code

## Handling Uncertainty

Write `[MISSING: <description of what was looked for or what is ambiguous>]` for any fact not found or not confidently interpretable. Do not guess.

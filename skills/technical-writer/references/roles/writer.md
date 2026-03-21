# Writer Instructions

Write a document from a provided template and research documents. Do not research. Take all facts from the research documents.

## Inputs

- `template.md` — document structure and per-section content guidance for this document type
- One or more research documents (facts, names, data contracts, processing steps)
- `style-guide.md` — sentence rules, formatting, anti-patterns
- `abstraction-rules.md` — what to include and exclude; the five heuristics; verbosity failure modes (optional)
- `examples.md` — curated examples of the target voice and abstraction level (optional)

Read all the files provided before writing. Use no other files. If a file is absent, ignore it.

## Output Format

Produce a Markdown document and write it to the assigned file path.

## Writing Process

1. Read `template.md`. This defines the sections and subsections to write, in order.
2. Read the research documents. For each section in the template, identify the relevant research findings.
3. Read the examples, if provided. Note the sentence length and level of detail.
4. Write the document section by section, following the template order. Omit sections for which the research contains nothing to say.
5. After finishing each section, re-read it against the style guide.

## Handling Missing Facts

If a research document is missing a fact you need to write a section:
- Write the section as far as you can
- Insert a `[MISSING: <description of what is needed>]` placeholder where the gap is
- Do NOT go looking for the fact yourself
- Do NOT guess or infer

## Calibrating Abstraction Level

Before including any fact from a research document, apply the core test:

> Would a technically literate person who has not read the source code need this to understand what the document is describing?

If no, exclude it. If borderline, exclude it — when in doubt, less is more.

Select and elevate from the research documents. Do not reproduce them.

## What NOT to Do

- Do not add any fact not present in the research documents
- Do not consult the codebase
- Do not explain design rationale ("This is done because…")
- Do not add a note just to cover yourself — use it only for a genuine caveat
- Do not summarize or introduce sections ("This section describes…")
- Do not use hedging language

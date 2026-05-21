# Writer Instructions

Write a document from research documents. Use the provided template when one
exists. Do not research. Take all facts from the research documents.

## Inputs

- `template.md` (optional) — document structure and per-section content guidance
  for this document type
- One or more research documents (facts, names, data contracts, processing
  steps)
- `style-guide.md` — sentence rules, formatting, anti-patterns
- `abstraction-rules.md` (optional) — what to include and exclude; the five
  heuristics; verbosity failure modes
- `examples.md` (optional) — curated examples of the target voice and
  abstraction level

Read all the files provided before writing. Use no other files. If a file is
absent, ignore it.

If the instruction explicitly asks for a rewrite, replace the affected text
rather than patching around it. Preserve facts, constraints, and explicit user
intent; do not preserve wording or structure that weakens the result.

## Output Format

Produce a Markdown document and write it to the assigned file path.

## Writing Process

1. Read `template.md`, if provided. This defines the sections and subsections to
   write, in order.
2. Read the research documents.
3. Read the examples, if provided. Note the sentence length and level of detail.
4. Write the document section by section. Omit sections for which the research
   contains nothing to say.
5. After finishing each section, re-read it against the style guide.

If no template is provided, infer the shortest useful structure from the
requested document type and the research documents.

## Handling Missing Facts

If a research document is missing a fact you need to write a section:

- Write the section as far as you can
- Insert a `**MISSING:** {{description of what is needed}}` placeholder where
  the gap is
- Do NOT go looking for the fact yourself
- Do NOT guess or infer

## What NOT to Do

- Do not add any fact not present in the research documents
- Do not copy research prose, headings, or organization into the draft
- Do not consult the codebase
- Do not explain design rationale ("This is done because…")
- Do not add a note just to cover yourself — use it only for a genuine caveat
- Do not summarize or introduce sections ("This section describes…")
- Do not use hedging language

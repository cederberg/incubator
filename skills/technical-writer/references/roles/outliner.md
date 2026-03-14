# Outliner Instructions

Produce a document skeleton with sections and subsections a writer can fill in. Derive all structure from `template.md` and all facts from the research documents. Do not write content. Make structural and ordering decisions only.

## Inputs

- `template.md` — the canonical document structure for this document type
- One or more research documents (facts, names, data contracts, processing steps)

Read the files provided before producing the skeleton.

## Output Format

Produce a Markdown skeleton and write it to the assigned file path.

Include only headings — no prose, no bullet lists, no field names. Use H2 names exactly as defined in `template.md`. Replace placeholder names (e.g. "[Process Name]") with names an operator would recognise. Derive replacements from the research.

```markdown
## Introduction

## Inbound Data
### Source A
### Source B

## Concepts & Definitions
### Concept Group A

## Order Processing
### Step One
### Step Two
```

## Section Selection

Include a section only if the research contains content for it. Omit sections with nothing to say. When in doubt, include the section. Use noun phrases for all headings.

## Subsection Ordering

Order subsections so that no subsection references a concept introduced later in the same section. For processing sections, use execution order. For all other sections, place foundational sub-topics before those that reference them. Place primary sub-topics before secondary ones.

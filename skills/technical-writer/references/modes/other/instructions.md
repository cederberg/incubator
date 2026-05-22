# Mode Instructions: Other

This mode has no `template.md` or `examples.md`. The writer infers structure
from the requested document type, research output, and its knowledge of common
technical-document forms.

## Pre-flight

Before starting Phase 1, interview the user to establish scope. Ask questions
one at a time, waiting for each answer before asking the next. Skip any question
the user already answered.

1. **Document type** — "What kind of document do you need?" Accept a specific
   type or infer one from the request.
2. **Subject** — "What is the document about?" Accept a name and a short
   description. Ask a clarifying follow-up if the answer is vague.
3. **Audience and purpose** — "Who will read it, and what should they be able to
   do after reading?"
4. **Inclusions** — "What should the document cover?" Look for behaviour,
   decisions, constraints, risks, edge cases, source evidence, and open
   questions.
5. **Exclusions** — "Is there anything that should be explicitly left out?"
6. **Structure** — "Do you already have required sections or a preferred
   structure?" If not, note that the writer will infer one.
7. **Starting points** — "Which files, modules, docs, tickets, or source
   materials should research start from?" If the user does not know, note that
   discovery will scan broadly.

Write the answers to `$WORK_DIR/brief.md` with these sections:

```
## Document Type
{{document type}}

## Subject
{{name and description}}

## Audience and Purpose
{{audience and desired outcome}}

## Scope
- Include: {{what the document should cover}}
- Exclude: {{what to leave out}}

## Structure
{{required or preferred sections, or "Infer from research"}}

## Starting Points
- {{files, modules, docs, tickets, or source materials to consult}}
```

## Discovery Strategy

After pre-flight, decide whether the document is source-led or intent-led.

- **Source-led** — use normal scoped discovery when code, docs, tickets, or
  other source material can answer the document's main questions.
- **Intent-led** — use interview-as-discovery when the document depends on user
  intent, desired behaviour, requirements, decisions, or unresolved questions.

For source-led documents, pass `$WORK_DIR/brief.md` to the discovery sub-agent
alongside the standard discovery instructions. Instruct it to focus on the
starting points listed in the brief. If no starting points were provided, scan
the full project. Prioritise sources related to the subject and document type.

For intent-led documents, keep interviewing until the brief states the relevant
goals, constraints, required behaviour, acceptance criteria, risks, and open
questions. Write `$WORK_DIR/discovery.md` from the interview answers using the
standard discovery sections. Do not force codebase discovery unless source
materials were named.

The discovery output still follows the standard format defined in the workflow
and narrows its attention to what is relevant to the brief.

## Research Topic Generation

This mode overrides the default Phase 2 topic selection. After discovery,
generate research topics based on `$WORK_DIR/brief.md` and
`$WORK_DIR/discovery.md`.

Materialise the topics in `$WORK_DIR/topics.md`:

| Topic          | Description          | Output file       |
| -------------- | -------------------- | ----------------- |
| {{topic name}} | {{what to research}} | {{topic-name}}.md |

Each description must be specific enough for a researcher to act on without
further context. Use inclusions to set topic boundaries. Use exclusions to set
explicit scope limits. Do not create topics outside the brief.

Choose topic boundaries that fit the document. Common boundaries include
context, source evidence, behaviour, requirements, decisions, constraints,
risks, outcomes, and open questions.

Adapt the number and scope of topics to the document. A narrow document may need
one researcher. A cross-system document may need several.

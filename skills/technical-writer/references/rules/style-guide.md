# Style Guide

## Voice and Tense

- Present tense, third person: "The system receives…", "Each event contains…"
- Active voice. Not "Events are checked by the system" but "The system checks events."
- No first person. Never "we", "our", or "I".

## Sentence Rules

- Every sentence must be load-bearing. If removing it changes nothing, remove it.
- Sentences should not exceed ~20 words. Split long sentences at natural boundaries.
- No hedging words: "typically", "usually", "generally", "in most cases", "often". Either the rule applies or the exception is worth its own sentence.
- No filler openers: "It is worth noting that…", "It should be mentioned that…", "As you can see…" — cut entirely.
- No justification prose. State what the system does or what the rule requires. Exception: include rationale when it determines how to apply the rule to cases not listed. Never "This was designed for…" or "The reason we do X is…"

## Paragraph Rules

- Two to four sentences per paragraph. More is a sign the paragraph covers two things.
- One idea per paragraph. If a paragraph ends with something unrelated to its first sentence, split it.
- No transition sentences between paragraphs ("Now that we've covered X, let's look at Y…").

## Formatting

### Bold
- Bold marks a name or label: a defined term, a named mode, a named category. The bolded item must be a noun or noun phrase — something that could appear in an index.
- Bold is not for emphasis. If a sentence needs emphasis, rewrite it.
- Legitimate uses: term in a definition list (`- **COMPLETED** — Processing succeeded`), named option introduced inline (`**Structural** — run the reviewer…`), category label in a rule list (`**Permanence:** Only extract…`).

### Note:
- Use "Note:" for a caveat or exception that cannot be folded into the main text without disrupting flow.
- One "Note:" per section is typical. Two is the maximum.
- Format: `Note that <fact>.` — a complete sentence, not a fragment.
- Do not use "Note:" to explain the implementation behind a rule.

### Tables
- Use tables for matrix relationships only: when two named dimensions interact (e.g. event type × message type).
- Not for simple lists that happen to have two columns.

### ASCII Diagrams
- Use ASCII diagrams for system topology and state machines.
- Do not use them for data structures, call sequences, or class hierarchies.

### Lists
- Bullet lists for finite sets of named things: statuses, message types, fields.
- Numbered lists for ordered sequences: processing steps, priority tiers, resolution cases.
- No nested bullets beyond one level deep.
- Each bullet item: bold name, dash, short description. No trailing period.

## Terminology

- Name each concept once; use that name without variation thereafter.
- Introduce each name once (in its definition or on first use) and reference it by name thereafter.
- Named things are never paraphrased after introduction. Not "the research step" after Phase 2: Research has been named. Not "the delivery service" after Delivery Gateway has been named.

## Section Headings

- H2 (`##`) for major document sections. H3 (`###`) for subsections. No H4.
- Section headings are noun phrases, not questions or verbs: "Event Processing", not "How Events Are Processed" or "Processing Events".

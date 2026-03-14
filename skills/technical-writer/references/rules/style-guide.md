# Style Guide

## Voice and Tense

- **Documentation voice** — for documents that describe a system, process, or artifact
  - **Subject** — the thing being documented
  - **Form** — present tense, third person, active voice
  - **Example** — "The system receives…", "The gateway forwards the message."
  - **Avoid** — "Events are checked by the system."

- **Instructional voice** — for documents that prescribe behaviour for a practitioner
  - **Subject** — the action or rule
  - **Form** — imperative mood
  - **Example** — "Split the paragraph." "Remove it."
  - **Avoid** — "The draft should be overwritten with the revised version."

Choose one voice for each document. No first person in either voice (i.e. never "we", "our", or "I").

## Sentence Rules

- Every sentence must be load-bearing. If removing it changes nothing, remove it.
- Do not exceed ~20 words per sentence.
- No hedging words: "typically", "usually", "generally", "in most cases", "often".
- No filler openers: "It is worth noting that…", "It should be mentioned that…", "As you can see…"
- No justification prose. State what something does or what it requires. Never "This was designed for…" or "The reason we do X is…"
- Instructional documents may include illustrative examples or clarification sentences.

## Paragraph Rules

- Use two to four sentences per paragraph.
- Write one idea per paragraph; split any paragraph that contains two.
- No transition sentences between paragraphs ("Now that we've covered X, let's look at Y…").

## Formatting

### Bold Usage
- Use bold to mark a name or label: a defined term, a named mode, a named category.
- Bold only nouns or noun phrases — items that could appear in an index.
- Do not use bold for emphasis. If a sentence needs emphasis, rewrite it.
- Legitimate uses:
  - `- **COMPLETED** — Processing succeeded` (definition list term)
  - `**Structural** — run the reviewer…` (named option inline)
  - `**Permanence:** Only extract…` (category label)

### Note Usage
- Use notes for caveats or exceptions that break prose flow. Do not use notes to explain why a rule exists.
- Max two notes per section.
- Format as a complete sentence, i.e. `Note that <fact>.`

### Tables
- Use tables for matrix relationships only (e.g. event type × message type).
- Do not use tables for lists with two columns.

### ASCII Diagrams
- Use ASCII diagrams for system topology and state machines.
- Do not use ASCII diagrams for data structures, call sequences, or class hierarchies.

### Lists
- Use bullet lists for sets of named things: statuses, message types, fields.
- Use numbered lists for ordered sequences: processing steps, priority tiers, resolution cases.
- Use at most two levels of bullets.
- Each bullet in a named-item list follows this format: `**Name** — short description` (no trailing period)

## Terminology

- Introduce each concept with one name in a definitions list or when first used. Reference it by that name thereafter.
- Never paraphrase a named thing after its introduction (e.g. "Delivery Gateway" not "the delivery service").

## Section Headings

- Use H2 (`##`) for major sections.
- Use H3 (`###`) for subsections.
- Do not use H4.
- Write section headings as noun phrases. Not questions ("How Events Are Processed") or verb phrases ("Processing Events").

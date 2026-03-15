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

Choose one voice for each document. Avoid first person (never "we", "our", or "I").

## Sentence Rules

- Make every sentence load-bearing. If removing it changes nothing, remove it.
- Do not exceed ~20 words per sentence.
- Avoid hedging words: "typically", "usually", "generally", "in most cases", "often".
- Avoid filler openers: "It is worth noting that…", "It should be mentioned that…", "As you can see…"
- Avoid justification prose. State what something does or what it requires. Avoid phrases like "This was designed for…" or "The reason X exists is…"
- Allow illustrative examples and clarification sentences in instructional documents.

## Paragraph Rules

- Use two to four sentences per paragraph.
- Write one idea per paragraph; split any paragraph that contains two.
- Avoid transition sentences between paragraphs (e.g. "Now that we've covered X, let's look at Y…").

## Formatting

### Bold Usage
- Use bold to mark names or labels: defined terms, named modes, named categories.
- Bold only nouns or noun phrases — items that could appear in an index.
- Do not use bold for emphasis. If a sentence needs emphasis, rewrite it.
- Legitimate uses:
  - `- **COMPLETED** — Processing succeeded` (definition list term)
  - `**Structural** — run the reviewer…` (named option inline)
  - `**Permanence:** Only extract…` (category label)

### Note Usage
- Use notes for caveats or exceptions that break prose flow. Do not use notes to explain why a rule exists.
- Use at most two notes per section.
- Format as a complete sentence: `Note that <fact>.`

### Tables
- Use tables for matrix relationships. In prescriptive documents, use tables when each column carries independent meaning.
- Do not use tables for lists with two columns.

### ASCII Diagrams
- Use ASCII diagrams for system topology and state machines.
- Do not use ASCII diagrams for data structures, call sequences, or class hierarchies.

### Lists
- Use bullet lists for sets of named things: statuses, message types, fields.
- Use numbered lists for ordered sequences: processing steps, priority tiers, resolution cases.
- Use at most two levels of bullets.
- Format named-item list items as `**Name** — short description` (no trailing period).
- Write rule lists as plain imperative sentences.

## Terminology

- Introduce each concept with one name at first use, either inline or in a definitions list. Reference it by that name thereafter.
- Never paraphrase a named thing after its introduction (e.g. "Delivery Gateway" not "the delivery service").

## Section Headings

- Use H2 (`##`) for major sections.
- Use H3 (`###`) for subsections.
- Avoid H4 headings.
- Write section headings as noun phrases. Avoid questions ("How Events Are Processed") and verb phrases ("Processing Events").

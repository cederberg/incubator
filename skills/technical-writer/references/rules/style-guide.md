# Style Guide

## Voice and Tense

Choose a voice based on document type. Do not mix within a document.

- **Documentation voice** — for documents that describe a system, process, or artifact
  - Subject: the thing being documented
  - Form: present tense, third person, active voice
  - Example: "The system receives…", "The gateway forwards the message."
  - Not: "Events are checked by the system."

- **Instructional voice** — for documents that prescribe behaviour for a practitioner
  - Subject: the action or rule
  - Form: imperative mood
  - Example: "Split the paragraph." "Remove it."
  - Not: "The draft should be overwritten with the revised version."

No first person in either voice. Never "we", "our", or "I".

## Sentence Rules

- Every sentence must be load-bearing. If removing it changes nothing, remove it.
- Do not exceed ~20 words per sentence. Split long sentences at natural boundaries.
- No hedging words: "typically", "usually", "generally", "in most cases", "often". Either the rule applies or the exception is worth its own sentence.
- No filler openers: "It is worth noting that…", "It should be mentioned that…", "As you can see…" — cut entirely.
- No justification prose. State what the system does or what the rule requires. Never "This was designed for…" or "The reason we do X is…"

## Paragraph Rules

- Use two to four sentences per paragraph. Split any paragraph that exceeds four sentences.
- Write one idea per paragraph. Split paragraphs that contain unrelated ideas.
- No transition sentences between paragraphs ("Now that we've covered X, let's look at Y…").

## Formatting

### Bold Marks
- Use bold to mark a name or label: a defined term, a named mode, a named category. Bold only nouns or noun phrases — items that could appear in an index.
- Do not use bold for emphasis. If a sentence needs emphasis, rewrite it.
- Legitimate uses:
  - **Definition list term** — `- **COMPLETED** — Processing succeeded`
  - **Named option inline** — `**Structural** — run the reviewer…`
  - **Category label** — `**Permanence:** Only extract…`

### Note Usage
- Use "Note:" for a caveat or exception that would require a parenthetical or subordinate clause mid-sentence to include inline.
- Two "Note:" entries max per section.
- Format: `Note that <fact>.` — a complete sentence, not a fragment.
- Do not use "Note:" to explain why a rule exists.

### Tables
- Use tables for matrix relationships only: when two named dimensions interact (e.g. event type × message type).
- Do not use tables for simple lists that happen to have two columns.

### ASCII Diagrams
- Use ASCII diagrams for system topology and state machines.
- Do not use ASCII diagrams for data structures, call sequences, or class hierarchies.

### Lists
- Use bullet lists for finite sets of named things: statuses, message types, fields.
- Use numbered lists for ordered sequences: processing steps, priority tiers, resolution cases.
- No nested bullets beyond one level deep.
- Each bullet in a named-item list follows this format: **Name** — short description. No trailing period.

## Terminology

- Introduce each concept with one name at its definition or first use. Reference it by that name thereafter.
- Never paraphrase a named thing after its introduction. Not "the research step" after Phase 2: Research has been named. Not "the delivery service" after Delivery Gateway has been named.

## Section Headings

- Use H2 (`##`) for major sections. Use H3 (`###`) for subsections. Do not use H4.
- Write section headings as noun phrases, not questions or verbs: "Event Processing", not "How Events Are Processed" or "Processing Events".

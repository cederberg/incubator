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
- No justification prose. The doc states what the system does, not why it was designed that way. Not "This is done because…" — that belongs in an ADR, not a system overview.

## Paragraph Rules

- Two to four sentences per paragraph. More is a sign the paragraph covers two things.
- One idea per paragraph. If a paragraph ends with something unrelated to its first sentence, split it.
- No transition sentences between paragraphs ("Now that we've covered X, let's look at Y…").

## Formatting

### Bold
- Bold is for defined terms appearing in a definition list: `- **COMPLETED** - Processing succeeded`
- Bold is not for general emphasis. If a sentence needs emphasis, rewrite it.

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

- Use the system's own names consistently. A thing has one name throughout the document.
- Introduce a named concept once (in its definition section or on first use) and then reference it by name.
- External systems are proper nouns: use their real names consistently. Never "the delivery service" after Delivery Gateway has been introduced.

## Section Headings

- H2 (`##`) for major document sections. H3 (`###`) for subsections. No H4.
- Section headings are noun phrases, not questions or verbs: "Event Processing", not "How Events Are Processed" or "Processing Events".

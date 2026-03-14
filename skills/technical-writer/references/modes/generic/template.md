# Document Structure Template

Use this structure as the starting point. Replace `[Topic]` section headings with the actual topic names. Add or remove `[Topic]` sections to match the content — do not create sections that have nothing to say.

---

## Summary

**Purpose:** Orient the reader: what this document describes, and why it matters.

**Content:**
- One to three sentences stating what the subject is and its role or context.
- One paragraph describing the scope of this document — what it covers and what it does not.

**Exclude:** Implementation history, rationale for why the subject was designed a certain way, team or organisational context.

---

## Concepts & Definitions

**Purpose:** Establish the vocabulary used throughout the rest of the document. Define every named concept that appears in more than one section.

**Structure:** One H3 subsection per concept group. Order by: foundational concepts first, then concepts that depend on them.

**Content per subsection:**
- One sentence introducing the concept and its role.
- Bullet list of named values with descriptions, OR a numbered list for priority/resolution cases, OR a table for matrix relationships.
- Note: for mutual exclusivity rules, ordering effects, or special cases that cannot be inferred from the list alone.

**Omit this section entirely** if the document has no shared vocabulary to establish.

---

## [Topic]

**Purpose:** Cover one distinct topic or area in full.

**Repeat** this section for each topic the document needs to address. Replace `[Topic]` with a noun phrase an operator or reader would recognise. Use one section per topic.

**Structure:** One H3 subsection per named sub-topic or step within the topic, in logical or execution order.

**Content per subsection:**
- One paragraph: what this sub-topic covers, in terms of inputs, behaviour, and outcomes.
- Bullet or numbered list if the sub-topic has a defined sequence, set of named items, or branching logic worth documenting.
- Note: for important exceptions or edge cases.

**Exclude:** Implementation details that a reader does not need to understand the behaviour. Internal names, configuration keys, and mechanism descriptions belong in source code or ADRs, not here.

---

## Notes on Section Ordering

- Summary → Concepts & Definitions → [Topic sections] is the default order.
- Concepts & Definitions may be omitted if there is no shared vocabulary.
- Order topic sections so that each is understandable from what precedes it — foundational topics first.
- Do not create a section just to have it. Omit sections with nothing to say.

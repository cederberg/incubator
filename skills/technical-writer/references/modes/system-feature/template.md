# Document Structure Template

Use this structure as the starting point. Adapt sections to match the actual subject — do not add sections that have no content, and do not force content into a section where it does not fit.

---

## Introduction

**Purpose:** Orient the reader: what this feature or process is, why it exists, and where it sits in the broader system.

**Content:**
- Paragraph 1: What the feature does, for whom, and its business or operational purpose. One to three sentences.
- Paragraph 2: How this feature relates to the rest of the system — what triggers it, what it produces, and which parts of the system it interacts with.
- Bullet list of external systems or internal components this feature depends on or communicates with. One line per system: name and one-sentence role. Omit if the feature is self-contained.

**Exclude:** Implementation technologies, reasons for architectural choices, team or organisational context.

---

## Concepts & Definitions

**Purpose:** Establish the vocabulary used throughout the rest of the document. Every named concept that appears in multiple later sections belongs here.

**Structure:** One H3 subsection per concept group. Order by: foundational concepts first, then concepts that depend on them.

**Content per subsection:**
- One sentence introducing the concept and its role.
- Bullet list of named values with descriptions (for enums/types), OR a numbered list for priority/resolution cases, OR a table for matrix relationships.
- Notes for mutual exclusivity rules, ordering effects, or special cases that cannot be inferred from the list alone.

**Omit this section entirely** if the document has no shared vocabulary to establish. If a concept is only used in one section, define it inline there instead.

---

## [Process or Feature Area]

**Purpose:** Describe one distinct process, workflow, or functional area in full.

**Repeat** this section for each major process or area the document needs to cover. Use one section per process. Replace `[Process or Feature Area]` with a name an operator or domain expert would recognise.

**Structure:** One H3 subsection per named step or phase, in execution order.

**Content per subsection:**
- One paragraph: what happens in this step — its trigger or input, the action performed, and the outcome or state change it produces.
- Bullet or numbered list if the step has a defined sequence, decision points, or branching logic worth documenting.
- For decision points: state the condition and each possible path. Use the form "If X, then Y. Otherwise, Z."
- Notes for important exceptions, edge cases, or failure behaviour within the step.

**Exclude:** Class names, method names, SQL queries, retry counts, thread pool sizes, exception types, framework interactions. Describe what the step does to the data, not how the code implements it.

---

## Failure Modes

**Purpose:** Describe what happens when the feature or process cannot complete normally.

**Structure:** One H3 subsection per distinct failure scenario, or a single section with a bullet list if failures are simple.

**Content per subsection:**
- What condition triggers the failure.
- What the system does in response: state changes, notifications, fallback behaviour.
- Whether and how recovery occurs.

**Omit this section** if failure behaviour is simple enough to cover inline within the process sections. Do not repeat what is already stated there.

---

## Notes on Section Ordering

- Introduction → Concepts & Definitions → [Process/Feature sections] → Failure Modes is the default order.
- Order process sections by significance or execution order — the primary flow first, then variations or secondary flows.
- Concepts & Definitions may be omitted if there is no shared vocabulary.
- Failure Modes may be omitted if failures are covered inline or are trivial.
- Do not create a section just to have it. Omit sections with nothing to say.

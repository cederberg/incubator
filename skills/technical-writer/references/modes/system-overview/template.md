# Document Structure Template

Use this structure as the canonical starting point. Add or remove sections to match the actual system — do not add sections that have no content, and do not split a single concept across multiple sections.

---

## Introduction

**Purpose:** Orient the reader: what the system does in business terms, and where it sits in the broader landscape.

**Content:**
- Paragraph 1: What the system does, for whom, and why (regulatory/business purpose). One to three sentences.
- Paragraph 2: High-level data flow — what comes in, what happens, what goes out.
- ASCII topology diagram showing internal components, infrastructure, and generic actor groupings (e.g. "Clients", "Worker", "Downstream Services") with directional arrows. The diagram should convey structure and flow — not enumerate every external system by name. Keep it readable: if more than ~5–6 external nodes would appear, group them.
- Bullet list of external systems, directly after the diagram. One line per system: name and one-sentence role. This is where individual systems are named and introduced.

**Exclude:** Implementation technologies (Spring Boot, Oracle, Kafka version), reasons for architectural choices, team or organizational context.

---

## Concepts & Definitions

**Purpose:** Establish the vocabulary used throughout the rest of the document. Every named concept that appears in multiple later sections belongs here.

**Structure:** One H3 subsection per concept group. Order by: domain-level concepts first, then system-specific concepts.

**Content per subsection:**
- One sentence introducing the concept and its role.
- Bullet list of named values with descriptions (for enums/types), OR a numbered list for resolution/priority cases, OR a table for matrix relationships.
- Note: for mutual exclusivity rules, ordering effects, or special cases that cannot be inferred from the list alone.

**Exclude:** How the values are stored, how resolution is implemented in code, configuration keys. A concept section defines what a thing *is*, not how it works.

---

## Status Lifecycles

**Purpose:** Describe the named states a key entity can occupy and what observable conditions trigger each transition.

**Structure:** One H3 subsection per stateful entity type (e.g., "Order Status", "Account Status").

**Content per subsection:**
- One sentence: what the entity is and why its state matters.
- A table or diagram: named states and the observable conditions that trigger each transition.
- Note: for terminal states, mutually exclusive states, or states with special operational significance.

**Exclude:** Internal triggers (method calls, scheduler invocations, database writes). Document the observable business event that causes each transition, not the mechanism that executes it.

---

## Inbound Data

**Purpose:** Define the data contracts at the system boundary — what data enters the system and from where.

**Structure:** One H3 subsection per distinct inbound source or event category.

**Content per subsection:**
- One paragraph: what triggers this data, which external system sends it.
- Bullet list of fields: `**Field Name** — one-line description`. Include only fields the system uses or that affect behavior.
- Note: for reliability, timing, or validity caveats that affect how the system interprets the data.

**Exclude:** HTTP methods, endpoint paths, authentication, field data types, JSON structure, error handling, retry behavior.

---

## Outbound Data

**Purpose:** Define the data contracts at the outbound system boundary.

**Structure:** One H3 subsection per distinct outbound destination.

**Content per subsection:**
- One paragraph: what the system sends and to which external system.
- Bullet list of fields if the contract is non-obvious.
- Note: for any behavioral constraints at the destination (e.g., the destination handles scheduling/retries itself).

**Exclude:** Same exclusions as Inbound Data.

---

## [Process Name]

**Purpose:** Describe one of the system's named processes — what happens to data as it moves through it.

**Repeat** this section for each distinct named process the system performs. Use one section per process, not one section for all. Minor, background, and administrative processes belong in Other Processes, not here.

**Structure:** One H3 subsection per named processing step, in execution order.

**Naming:** Name the section after the process as an operator would recognise it (e.g., "Number Portability Processing", "Subscription Provisioning"). Name each H3 after its step (e.g., "Validation", "Number Assignment", "Confirmation").

**Content per subsection:**
- One paragraph: what happens in this step, in terms of inputs, action, and outcome.
- Bullet list or numbered steps if the step has a defined sequence or branching logic worth documenting.
- Note: for important exceptions or edge cases within the step.

**Exclude:** Class names, method names, SQL queries, retry counts, thread pool sizes, exception types, how the step interacts with the framework. The step is described in terms of what it does to the data, not how the code implements it.

---

## Other Processes

**Purpose:** Describe minor background, maintenance, or administrative processes. A process belongs here if it does not constitute a primary user- or system-facing operation.

**Structure:** H3 (`###`) subsections, one per process.

**Content:** Same rules as process sections, but typically shorter — one paragraph and any needed list.

**Examples:** GDPR data purge, deduplication cleanup, operator data maintenance, template refresh.

---

## Notes on Section Ordering

- Introduction → Concepts & Definitions → Status Lifecycles → Inbound Data → Outbound Data → [Process sections] → Other Processes is the default order.
- Include as many process sections as the system warrants. Order them by significance — the primary process first.
- If a concept is only used in one section, it may be defined inline there rather than in Concepts & Definitions.
- If Outbound Data is trivial (one destination, obvious contract), it may be folded into the Introduction.
- Do not create a section just to have it. Omit sections with nothing to say.

# Overview Template

Use this as a guide, not a fixed outline.

- Start with Introduction. Add Concepts & Definitions when later sections depend
  on shared terms.
- Define a concept inline when it is used in only one section.
- Order remaining sections so readers do not need to skip forward to understand.
- Put topology, data contract, and behavior sections before sections that depend
  on them.
- For a system overview, a common order is Introduction → Concepts & Definitions
  → Topology & Actors → Data Contracts → States & Lifecycles → Behavior &
  Workflows → Support Processes.
- For subsystem overviews, a common order is Introduction → Concepts &
  Definitions → Topology & Actors → subject-specific sections.
- For topic, concept, or domain overviews, order sections around the reader's
  questions and omit system-shaped sections that do not apply.
- Do not create a section just to have it. Omit sections with no distinct facts.
- Do not split one concept across multiple sections.

---

## Introduction

Orient the reader. State what the subject is or does, who it serves, where it
sits, and what is inside or outside scope.

Include high-level flow when it helps: what comes in, what happens, and what
goes out. Add the requested overview diagram here unless a later section gives
it clearer context. Introduce every actor, system, or component that appears in
the diagram. Group repeated or low-level actors when naming each one would make
the diagram harder to read.

Exclude implementation technologies, architecture rationale, team context, and
setup details unless they define the subject.

## Concepts & Definitions

Define named concepts before later sections rely on them.

Include statuses, message types, variants, domain terms, priority rules, and
relationship matrices that affect reader understanding. Use lists for named
values, numbered lists for priority or resolution order, and tables for matrix
relationships.

Exclude storage details, configuration keys, class names, and implementation
mechanisms.

## {{Section}}

Repeat this H2 template for each additional section the overview needs. Replace
`{{Section}}` with a concrete section name, e.g:

- **Topology & Actors** — external systems, infrastructure components, internal
  components, actors, boundaries, roles, relationships, and flow direction
  between them.
- **Data Contracts** — fields each external or boundary actor sends or receives.
  Include only fields the subject uses or exposes in behavior. Add timing,
  reliability, or validity caveats that affect interpretation.
- **States & Lifecycles** — named states, lifecycle phases, observable
  transition conditions, terminal states, mutually exclusive states, and
  operationally significant states. Document observable transitions, not
  internal triggers.
- **Behavior & Workflows** — named workflows, triggers, ordered steps, decision
  points, business rules, terminal outcomes, edge cases, and failure behavior.
  Use one section per primary workflow.
- **Rules & Decisions** — priority rules, eligibility rules, matching rules,
  branching conditions, policy decisions, and fallback rules.
- **Support Processes** — background, maintenance, administrative, or secondary
  processes that matter but are not primary.

Use H3 subsections for details inside broad sections: actors, contracts,
lifecycles, process steps, or topic slices.

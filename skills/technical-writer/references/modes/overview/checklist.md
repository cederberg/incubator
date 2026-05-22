# Review Checklist: Overview

Apply Baseline, Diagrams, and Concepts to every overview. Apply remaining
sections only when they match the requested overview or the draft's evident
purpose.

## Baseline

- [ ] Opening identifies the subject, purpose, and scope
- [ ] Section order helps the reader build the right mental model
- [ ] Section headings are concrete and contain no unreplaced placeholders
- [ ] Named concepts are introduced before later sections depend on them
- [ ] Implementation detail appears only when it supports the overview's purpose
- [ ] No undefined acronyms or abbreviated system names

## Diagrams

- [ ] Diagram choice follows the user's stated preference or the mode default
- [ ] Each diagram clarifies topology, state, flow, or relationships already
      present in prose
- [ ] Diagram labels match terms used in the prose
- [ ] Every actor, component, or state in a diagram is named in prose
- [ ] Additional diagrams make dense prose easier to understand
- [ ] No diagram is decorative or a visual version of a simple list

## Concepts

- [ ] Concepts & Definitions introduces terms needed by later sections
- [ ] Concept groups appear before sections that rely on them
- [ ] Named values have short, behavioral descriptions
- [ ] Priority, ordering, and exclusivity rules are explicit
- [ ] Storage details, configuration keys, and implementation names are excluded

## Topology and Actors (if applicable)

- [ ] Important actors, components, dependencies, and boundaries are named
- [ ] Each actor or component has a clear role
- [ ] Direction of flow is clear
- [ ] External systems are named when they affect behavior

## Data Contracts (if applicable)

- [ ] Relevant inputs and outputs are covered
- [ ] Field lists include only fields that affect behavior or reader
      understanding
- [ ] Timing, reliability, and validity caveats are stated when they affect
      behavior
- [ ] Protocol, endpoint, authentication, raw payload, and retry details appear
      only when the overview is about that interface

## States and Behavior (if applicable)

- [ ] Triggers or transition conditions are stated
- [ ] Ordered steps appear only when sequence matters
- [ ] Decision points state each possible path
- [ ] State transitions name observable conditions
- [ ] Terminal outcomes and important failure behavior are covered

# Structural Checklist: System Feature

## Structure

- [ ] Introduction is present and states what the feature does, why it exists, and where it fits
- [ ] Section order: Introduction → Concepts & Definitions (if present) → process/feature sections → Failure Modes (if present)
- [ ] Introduction opens with a factual statement; no taglines or marketing phrases
- [ ] Scope is clear from the introduction — a reader can tell what this document covers and what it does not
- [ ] Concepts & Definitions is present if and only if a term is used in more than one section
- [ ] No section heading contains a placeholder such as `[Process or Feature Area]` or `[Topic]`

## Process Coverage

- [ ] Every process or feature area identified in the brief is documented
- [ ] Each process section states what triggers it
- [ ] Each process section describes its steps in execution order
- [ ] Decision points state the condition and each possible path
- [ ] Terminal outcomes are stated: what the process produces on success
- [ ] State changes are documented: what entities change status and to what
- [ ] Failure behaviour is documented, either inline or in a dedicated Failure Modes section

## Abstraction Level

- [ ] No internal class, method, or variable names appear
- [ ] No SQL, endpoint paths, or configuration keys appear
- [ ] Steps describe what happens to the data, not how the code implements it
- [ ] Edge cases are handled with a sentence or clause, not a sub-section (unless genuinely complex)

## Terminology

- [ ] No term is used before it is defined in Concepts & Definitions or introduced in its own section
- [ ] Domain terms are consistent throughout — the same concept is not referred to by different names

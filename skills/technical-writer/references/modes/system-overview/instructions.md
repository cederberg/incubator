# Mode Instructions: System Overview

## Research Topics

Research each topic and write its findings to the named output file:

- **Topology & actors** → `topology.md` \
  External systems and infrastructure components, their roles, data flow
  direction between them.
- **Data contracts** → `contracts.md` \
  Data fields each external actor sends and receives; field names and one-line
  descriptions; reliability or timing notes visible in the code or config.
- **Processing logic** → `processing.md` \
  Named processes and their triggers. For each process: the steps in execution
  order, what each step does to the data, decision points and branching
  conditions, intermediate state changes, and terminal outcomes (success and
  failure). Include business rules that govern filtering, prioritisation, and
  validation.
- **Vocabulary** → `vocabulary.md` \
  Named concepts: enum values, status values, message types, event types,
  variant names, and their descriptions.

Adapt scopes to the actual project using `$WORK_DIR/discovery.md`. For a small
project, use two or three researchers.

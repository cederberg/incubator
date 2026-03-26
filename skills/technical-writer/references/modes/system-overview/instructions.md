# Mode Instructions: System Overview

## Research Topics

| Topic | Description | Output file |
|---|---|---|
| Topology & actors | External systems and infrastructure components, their roles, data flow direction between them | topology.md |
| Data contracts | Data fields each external actor sends and receives; field names and one-line descriptions; reliability or timing notes visible in the code or config | contracts.md |
| Processing logic | Named processes and their triggers. For each process: the steps in execution order, what each step does to the data, decision points and branching conditions, intermediate state changes, and terminal outcomes (success and failure). Include business rules that govern filtering, prioritisation, and validation. | processing.md |
| Vocabulary | Named concepts: enum values, status values, message types, event types, variant names, and their descriptions | vocabulary.md |

Adapt scopes to the actual project using `$WORK_DIR/discovery.md`. For a small project, use two or three researchers.

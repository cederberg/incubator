# Discovery and Research: System Overview

## Phase 1: Discovery

Use the default discovery instructions.

## Phase 2: Research Topics

| Topic | Description | Output file |
|---|---|---|
| Topology & actors | External systems and infrastructure components, their roles, data flow direction between them | topology.md |
| Data contracts | Data fields each external actor sends and receives; field names and one-line descriptions; reliability or timing notes visible in the code or config | contracts.md |
| Processing logic | Named processing steps, the sequence they occur in, the business rules that govern each, filter conditions, outcome states | processing.md |
| Vocabulary | Named concepts: enum values, status values, message types, event types, variant names, and their descriptions | vocabulary.md |

Adapt scopes to the actual project using `$WORK_DIR/discovery.md`. For a small project, use two or three researchers.

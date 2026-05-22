# Mode Instructions: Overview

## Pre-flight

Before Phase 1, ask the user which diagrams the overview should include unless
the answer is already clear from context.

Ask as a free-text question. State the available options:

- one Mermaid overview chart (default)
- ASCII instead of Mermaid
- additional diagrams for state, flow, or relationships
- no diagrams

If the user has no preference, use one Mermaid overview chart. Write the answer
to `$WORK_DIR/brief.md`:

```
## Diagram Preference
{{diagram preference}}
```

Pass `$WORK_DIR/brief.md` to discovery, research, writer, and reviewer
sub-agents.

## Research Topics

Use these as default research topics. Adapt or omit topics that do not fit the
requested overview.

- **Topology & actors** → `topology.md` \
  External systems, infrastructure components, internal components, boundaries,
  roles, relationships, and data-flow direction between them.
- **Data contracts** → `contracts.md` \
  Data fields each external or boundary actor sends and receives; field names
  and one-line descriptions; reliability or timing notes visible in the code or
  config.
- **Behavior & lifecycles** → `processing.md` \
  Named workflows, state changes, processing steps, business rules, decisions,
  and terminal outcomes.
- **Vocabulary** → `vocabulary.md` \
  Named concepts, domain terms, entities, relationships, status values, message
  types, event types, variants, and their descriptions.

Adapt scopes to the requested overview and `$WORK_DIR/discovery.md`. A narrow
topic may need one or two researchers. A cross-system overview may need all
topics.

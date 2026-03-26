# Mode Instructions: System Feature

## Pre-flight

Before starting Phase 1, interview the user to establish scope. Ask the following questions **one at a time**, waiting for each answer before asking the next.

1. **Subject** — "What do you want documented?" Accept a name and a short description. If the user's answer is vague (e.g., "the matching stuff"), ask a clarifying follow-up before proceeding.
2. **Inclusions** — "What should the document cover?" Look for: processes, decision logic, data flows, integrations, edge cases, failure handling. If the user gives a broad answer, reflect back what you understood and ask if anything is missing.
3. **Exclusions** — "Is there anything that should be explicitly left out?" Examples: upstream systems already documented elsewhere, configuration details, deployment concerns.
4. **Starting points** — "Which parts of the codebase implement this?" Accept module names, directories, service names, or class names. If the user doesn't know, note that discovery will scan broadly.

Write the answers to `$WORK_DIR/brief.md` with these sections:

```
## Subject
<name and description>

## Scope
- Include: <what the document should cover>
- Exclude: <what to leave out>

## Codebase Starting Points
- <modules, directories, or services to focus on>
```

### Scoped Discovery

Pass `$WORK_DIR/brief.md` to the discovery sub-agent alongside the standard discovery instructions. Instruct it to focus on the codebase starting points listed in the brief. If no starting points were provided, scan the full project but prioritise modules and services that relate to the subject described in the brief.

The discovery output still follows the standard format defined in the workflow, but the agent should narrow its attention to what is relevant to the brief.

### Research Topic Generation

After discovery, generate research topics based on the brief and `$WORK_DIR/discovery.md`. Do not use the user's words verbatim as topic descriptions — translate them into specific, researcher-actionable extraction instructions.

Materialise the topics as a table in `$WORK_DIR/topics.md`:

| Topic | Description | Output file |
|---|---|---|
| <topic name> | <what to research — specific enough for a researcher to act on without further context> | <topic-name>.md |

Use the brief's inclusions to determine topic boundaries. Use the exclusions to set explicit scope limits in each topic description. Typical topics for a feature or process document:

- **Context & triggers** — what initiates the feature or process, which systems or actors are involved, preconditions
- **Processing steps** — the steps in execution order, what each step does to the data, decision points and branching conditions, intermediate state changes
- **Outcomes & failure modes** — terminal states, success and failure paths, error handling behaviour, downstream effects
- **Related concepts** — named statuses, types, or domain terms specific to this feature that the reader needs to understand

Adapt the number and scope of topics to the subject. A simple feature may need two researchers; a complex process may need four. Do not create topics that fall outside the brief's scope.

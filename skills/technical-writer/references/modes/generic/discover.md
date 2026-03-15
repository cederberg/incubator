# Discovery and Research: Generic

## Phase 1: Discovery

Before running the default discovery agent:

1. Extract research topics from the user's description. If the user has not provided topics, ask: "What areas should the researchers investigate?"
2. Materialise the topics into `$WORK_DIR/topics.md` following the table format in Phase 2 below.

Then run the default discovery agent to produce `$WORK_DIR/discovery.md`.

## Phase 2: Research Topics

Materialise the topics as a table in `$WORK_DIR/topics.md`:

| Topic | Description | Output file |
|---|---|---|
| <topic name> | <what to research> | <topic-name>.md |

Adapt scopes to the actual project using `$WORK_DIR/discovery.md`. For a small project, two or three researchers suffice.

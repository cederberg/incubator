---
name: update-knowledge-base
description: Extracts knowledge from a series of summarized conversations.
synonyms: [summarize knowledge, save knowledge, sync knowledge, update brain]
version: 1.0.0
---

# update-knowledge-base

## Preconditions
- Existing conversation summaries exist in one or more
  `.agent/memory/conversation-YYYY-MM-DD-HHMM.md` (or json) files.

## Activation
Trigger this skill when the user requests to "update knowledge",
"save knowledge", or at the conclusion of a significant milestone.

## Processing Logic

Read input conversation summaries from `.agent/memory/conversation-*` in
batches of maximum 10 files. Don't process files older (see file name)
than the knowledge-base (see last updated field). Process files in order,
the oldest first.

The goal is to synthesize these into the `.agent/memory/KNOWLEDGE-BASE.md`
file that will serve as a permanent context for an agent working on this
project. If such a file exist, its knowledge should be updated (not
deleted).

## Instructions:

- **De-duplicate:** Identify overlapping facts or rules.
- **Conflict Resolution:** If conversation A and conversation B provide
  conflicting technical truths, use the most recent as the source of truth.
- **Categorize:** Use the taxonomy provided by the output template.
- **Prune:** Remove information that is no longer relevant or has been
  superseded by newer entries.
- **Generate:** Produce a high-density Markdown file optimized for LLM
  "System Prompt" injection.

## Output Template

> # Project Intelligence
> *Last Updated: [Date]*
>
> ## 🛠 System Architecture
> - [Fact 1]
> - [Fact 2]
>
> ## 📋 Rules, Constraints & Preferences
> - Always use [Library/Method] for [Task].
> - Never [Action] because [Reason].
>
> ## 🧠 Heuristics & Suggestions
> - When [Scenario X] occurs, the solution is usually [Y].
>
> ## ⏳ Pending Context
> - [Unresolved items from the last 2-3 sessions]

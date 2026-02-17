---
name: archive-conversation
description: Extracts and structures knowledge from a conversation for persistent storage.
synonyms: [summarize session, save conversation, archive chat]
---

# archive-conversation

## Preconditions
- The session must contain at least one significant exchange or decision.
- The agent must have access to the full conversation history.

## Activation
Trigger this skill when the user requests to "archive conversation",
"save session", or at the conclusion of a significant milestone.

## Processing Logic
Analyze the conversation and provide a structured summary. Store the results
into `.agent/memory/conversation-YYYY-MM-DD-HHMM.md` or a file provided by the
user. Use the conversation start timestamp in the file name. If such a file
already exists, create a new one using a later timestamp instead.

Provide a concise and relevant title. Add conversation metadata at the top
(dates, id, etc). Summarize the conversation with a focus on:

- Goal: The primary user intent of the session
- Key Facts: Explicit information shared by the user (preferences, specific data)
- Technical Details: Architectural decisions, chosen libraries, patterns, or constraints
- Insights: Lessons learned, operational workflows, and "things to remember"
- Action Items: Pending tasks or follow-ups for the agent (if any)

Any section can be omitted if there is nothing to report.

## Output Template

> # [Title]
>
> **ID:** [ID]
> **Created:** [Created]
> **Last Modified:** [Last Modified]
>
> ## Goal
> [Goal]
>
> ## Key Facts
> [Key Facts]
>
> ## Technical Details
> [Technical Details]
>
> ## Insights
> [Insights]
>
> ## Action Items
> [Action Items]

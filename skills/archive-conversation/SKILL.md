---
name: archive-conversation
description: Extracts and structures knowledge from a conversation for persistent storage.
synonyms: [summarize session, save conversation, archive chat]
---

# archive-conversation

## Preconditions
- The session must contain at least one significant exchange of information or
  a technical decision.
- The agent must have access to the full conversation history.

## Activation
Trigger this skill when the user requests to "archive conversation",
"save session", or at the conclusion of a significant milestone.

## Processing Logic
Analyze the conversation and provide a structured summary. Store the results
into `.agent/memory/conversation-YYYY-MM-DD-HHMM.md` or a file provided by the
user. Use the conversation start timestamp in the file name.

Provide a consise and relevant title. Add conversation metadata at the top
(dates, id, etc).

If file already exists, keep existing title and metadata (don't remove it).

Focus on:

- Goal: The primary user intent with of the session.
- Key Facts: Explicit information shared by the user.
- Technical Details: Specific technical choices, code patterns, or constraints
  discussed.
- Action Items: Pending tasks or follow-ups for the agent (if any)

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
> ## Action Items
> [Action Items]

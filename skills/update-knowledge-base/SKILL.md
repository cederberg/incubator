---
name: update-knowledge-base
description: Distills interaction history into a high-density system prompt.
synonyms: [summarize knowledge, save knowledge, sync knowledge, update brain]
---

# update-knowledge-base

## Preconditions
- Existing conversation summaries exist in `.agent/memory/conversation-*.md`.

## Activation
Trigger when the user requests to "update knowledge" or after significant
architectural decisions.

## Processing Logic
1. Read `.agent/memory/KNOWLEDGE-BASE.md` (if it exists).
2. Identify `.agent/memory/conversation-YYYY-MM-DD-HHMM.md` files to process
3. Ignore files strictly older than the KNOWLEDGE-BASE modified date
4. Read files chronologically (oldest first)
5. Synthesize a new `KNOWLEDGE-BASE.md` by merging new insights into the
   existing categories.

## Extraction Rules
- **Permanence:** Only extract information that remains true over time. Ignore
  transient debugging steps.
- **Novelty:** Exclude standard documentation/practices. Only record
  project-specific deviations.
- **Conflict:** Newer conversation summaries supersede older Knowledge Base
  entries.
- **Redundancy:** Do not document what is already enforced by code/linters.
- **Density:** The final file should be < 100 lines. Aggressive pruning is
  required.

## Style Guide (Strict High-Density)
- **Imperative:** "Use X" (not "The user wants X", not "It was decided to use X").
- **Categorized:** Start bullets with **Topic:** (e.g., **Testing:**, **Naming:**).
- **Compressed:** Remove filler words. Max 1 line per fact.

## Transformation Examples
> *Input:* "I want us to switch to using `vitest` instead of `jest` for speed."
> *Output:* **Testing:** Use `vitest` instead of `jest`.

## Output Template

> # Project Intelligence
> *Last Updated: [Date]*
>
> ## 🛠 System Architecture
> - **[Component]:** [Brief architectural decision/pattern]
>
> ## 📋 Development Constraints
> - **[Topic]:** [Strict rule, e.g. "Values must be immutable"]
>
> ## 🧠 Operational Workflow
> - **[Process]:** [Workflow steps, deployment notes, or "things to remember"]
>
> ## ⚡ Project Preferences
> - **[Preference]:** [Specific stylistic or behavior preference]

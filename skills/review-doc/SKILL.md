---
name: review-doc
description: Review a document for internal consistency, brevity, clarity, and usefulness.
argument-hint: "<file(s)> [additional instructions]"
disable-model-invocation: true
allowed-tools: Agent, Read
---
User provided one or more documents for review. If missing, ask for it.

Launch a general-purpose sub-agent to review the document(s). Pass any
additional user instructions to the sub-agent. Instruct it to review:
- Brevity
- Clarity
- Consistency
- Terminology
- Usefulness

Assess whether each issue in the sub-agent response is genuine or mistaken.

Present a summary to the user. Group findings by theme. Note whether you agree
or not. Suggest action points.

---
name: review-doc
description: >
  Review a document for internal consistency, brevity, clarity, and usefulness.
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
Present each finding in a numbered list. Quote the sub-agent text verbatim, then
write your assessment inline:

    1. {{sub-agent finding}}
       Assessment: Ignore/Fix/Discuss {{rationale}}

End by asking the user which issues to address or discuss further.

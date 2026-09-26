---
name: review-instructions
description: >
  Review a prompt, skill, or other instructions for problems. Checks language
  (brevity, clarity, terminology, tone, voice), structure (consistency, flow,
  format, redundancy), and precision (ambiguity, assumptions, coverage,
  omissions). Sub-agent isolates review from conversation context. Covers prompt
  files and tool descriptions.
argument-hint: "<file(s)> [additional instructions]"
allowed-tools: Agent, Read, Write
---

If no file is provided, ask for it.

Launch a sub-agent and instruct it to read `references/reviewer.md` and review
the instructions in the provided file(s) (or embedded within them).

Assess whether each issue in the sub-agent response is genuine or mistaken.
Present each finding in a numbered list. Quote the sub-agent text verbatim, then
write your assessment inline:

    1. {{sub-agent finding}}
       Assessment: Ignore/Fix/Discuss {{rationale}}

When tasked with fixing instructions, apply the changes directly. End by
reporting all findings or changes. Offer to fix problems or discuss further.

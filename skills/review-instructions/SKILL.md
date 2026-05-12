---
name: review-instructions
description: >
    Review a prompt, skill, or other instructions for problems. Checks language
    (brevity, clarity, terminology, tone, voice), structure (consistency, flow,
    format, redundancy), and precision (ambiguity, assumptions, coverage,
    omissions). Sub-agent isolates review from conversation context.
argument-hint: "<file(s)> [additional instructions]"
disable-model-invocation: true
allowed-tools: Agent, Read
---
If no file is provided, ask for it.

Launch a sub-agent using the best available model. Instruct it to read
`references/reviewer.md` and review the provided file(s), including any
additional user instructions.

Assess whether each issue in the sub-agent response is genuine or mistaken.
Present each finding in a numbered list. Quote the sub-agent text verbatim,
then write your assessment inline:

    1. {{sub-agent finding}}
       Assessment: Ignore/Fix/Discuss {{rationale}}

End by asking the user which issues to address or discuss further.

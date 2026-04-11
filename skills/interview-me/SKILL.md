---
name: interview-me
description: >
    Conduct a deep, structured interview to reach shared understanding
    of a plan or topic, then document the outcome.
disable-model-invocation: true
allowed-tools: Write
---

# Interview Me

Interview the user about their plan or topic until you reach a shared
understanding of it. Then document that understanding for them to keep.

## How to run the interview

**One question at a time.** Don't batch questions — it's overwhelming and
people give shallower answers.

**Suggest answers when you can.** If context gives you a reasonable guess,
offer it. If you can find an answer from the codebase, use a sub-agent in the
background to explore it (before asking).

**Follow branches.** Each answer might open sub-questions. Follow them before
moving on.

**Surface tensions.** If two answers seem in conflict, ask about it.

**Don't skip the mundane.** Stakeholders, success metrics, failure modes,
handoffs — these are often underdeveloped and they matter.

## Knowing when you're done

- No obvious open questions remain
- You understand the *why* behind the plan, not just the *what*
- Apparent contradictions or gaps have been surfaced and resolved

Don't rush to the recap. If an answer opens new territory, explore it.

## The recap

When done interviewing, present a comprehensive recap organized around the
plan's major dimensions. Ask user to confirm correctness and completeness,
or to provide additional information.

## Save the output

After confirmation, offer to save the recap to a `plan-[topic].md` file in the
current directory or to a path of the users choice.

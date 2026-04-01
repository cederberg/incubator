---
name: session-review
description: Analyze Claude Code or Copilot session logs for insights, gaps,
  and learnings. Produces a report of findings with targeted suggestions for
  the highest-leverage ones.
disable-model-invocation: true
argument-hint: "[session-id | 'latest' | 'list']"
allowed-tools: Read, Grep, Glob
---
# Session Review

## Goal

Agent sessions accumulate corrections, dead ends, missing context, and
occasional insights. The goal of this skill is to learn from these — as
AGENTS.md rules, new tools, scripts, or skills — making future agents faster
and less error-prone. The output is a report of findings followed by targeted
suggestions for the highest-leverage ones.

---

## Step 1: Determine mode

Parse `$ARGUMENTS`:

| Argument           | Mode                                        |
|--------------------|---------------------------------------------|
| `list` (default)   | Scan recent sessions and surface candidates |
| `latest`           | Analyze the most recent session             |
| `<uuid or prefix>` | Analyze the specified session               |

## Step 2: Select session tool

Based on your identity, use one of these commands as the `[TOOL]` reference.

| Agent        | Command                           |
|--------------|-----------------------------------|
| Claude Code  | `python scripts/claude-sessions`  |
| Copilot      | `python scripts/copilot-sessions` |

---

## Mode: List

Surface candidate sessions from the current working directory for the user
to choose from. Do not search other projects unless requested by the user.

```bash
[TOOL] -n 10 [-d <dir>]
```

For each candidate session, run:

```bash
[TOOL] <id>
```

Read the turns table. Scan user messages for these signals:

- **Corrections**
- **Repeated requests**
- **Short dismissive messages**
- **User takeover**
- **Tool denials**
- **Reflection signals**

List all sessions in a table — session ID, date, duration, turn count, one
line of quoted evidence — with the top 3 by interest marked. Ask the user
which to review — or whether to search a different directory.

---

## Mode: Analyze

### Read session summary

```bash
[TOOL] <id>
```

### Pull targeted transcript sections

Do not read the full transcript upfront. Use the turns table to identify
interesting segments, then pull selectively:

```bash
[TOOL] <id> --turn <range> --raw
```

Prioritize:
- Turns with corrections or reversals (and the turns immediately before them)
- Turns with unusually long response times
- Turns where the user edited files themselves
- Sub-agent turns — what was the task, did the result land correctly?
- Any turn where the user signals something is worth remembering

### Report findings

Write the report directly in your response to the user.

```markdown
# Session Review

**Session:** <id (first 8 chars)>
**Date:** <date>
**Duration:** <duration>
**Model:** <model>
**Turns:** <count>
**Summary:** <one sentence: what was the user trying to accomplish?>

## Context Gaps

Facts the agent didn't know, had to be told, or got wrong. Candidates for
AGENTS.md, project docs, or per-filetype rules. Top 3, prioritized by impact.

- **Turn N** — "<quoted evidence>" — *agent assumed X; reality was Y* — **pattern: ...**

## Capability Gaps

Places where a missing tool, script, or skill forced a longer path — inline
bash, multi-step workarounds, or manual steps the user had to perform.
Top 3, prioritized by impact.

- **Turn N** — "<quoted evidence>" — *agent lacked a tool for X; used Y
  instead* — **pattern: ...**

## Process Failures

Corrections, reversals, repeated requests, tool denials, missing allow-list
entries, or moments where the user took over. Top 3, prioritized by impact.

- **Turn N** — "<quoted evidence>" — *agent did X when asked for Y* — **pattern: ...**

## Insights

Explicit requests to remember or reflect, end-of-session observations, or
moments where the agent expressed a realization.
Top 3, prioritized by impact.

- **Turn N** — "<quoted or paraphrased>" — *why this matters* — **pattern: ...**
```

Leave any section empty with "— none found —" rather than padding it. Be
specific: quote directly, cite turn numbers, describe the shape of the
problem.

### Reflect and suggest

Re-read the report. Identify the 1–2 findings with the highest leverage —
the ones that, if addressed, would most improve future sessions. For each,
suggest a concrete remedy: an AGENTS.md rule, a new tool or script, or a
change to a skill. Do not suggest a remedy for every finding — only where
the pattern is clear and the fix is actionable.

---
name: session-review
description: Analyze Claude Code or Copilot session logs for insights, gaps,
  and learnings. Produces a structured report of findings — no solutions
  prescribed.
disable-model-invocation: true
argument-hint: "[session-id | 'latest' | 'list']"
allowed-tools: Read, Grep, Glob, Bash(scripts/*), Bash(ls *), Bash(wc *)
---

# Session Review

## Goal

Agent sessions accumulate hard-won knowledge: corrections, dead ends,
missing context, and occasional insights. The goal of this skill is to
surface that knowledge so it can be persisted — as AGENTS.md rules, new
tools, scripts, or skills — making future agents faster and less error-prone.
The output is a structured report of findings; acting on them is a separate
step.

---

## Step 1: Determine mode

Parse `$ARGUMENTS`:

| Argument           | Mode                                        |
|--------------------|---------------------------------------------|
| `list` (default)   | Scan recent sessions and surface candidates |
| `latest`           | Analyze the most recent session             |
| `<uuid or prefix>` | Analyze the specified session               |

## Step 2: Select session tool

Select the script that matches the current agent. Use it as `SESSION_TOOL`
for all subsequent commands.

| Agent        | Script                     |
|--------------|----------------------------|
| Claude Code  | `scripts/claude-sessions`  |
| Copilot      | `scripts/copilot-sessions` |

---

## Mode: List

Surface candidate sessions for the user to choose from.
**Do not analyze yet.**

```bash
$SESSION_TOOL -n 30
```

Working from the most recent sessions first, prefer those with higher turn
counts. For each candidate, run:

```bash
$SESSION_TOOL <id>
```

Read the turns table. Scan user messages for these signals:

- **Corrections**
- **Repeated requests**
- **Short dismissive messages**
- **User takeover**
- **Tool denials**
- **Reflection signals**

Quick-check sessions until you have 3 that appear worth diving into. List
up to 10 candidate sessions, with a table showing session ID, date, duration,
turn count, signal count, and one line of quoted evidence. Mark the top 3
clearly. Then ask: *"Which session would you like to review?"*

---

## Mode: Analyze

### Load the session

```bash
$SESSION_TOOL <id>
```

Read the full output: session metadata, tool usage, sub-agent table, and
turns table. This is your map.

### Pull targeted transcript sections

Do not read the full transcript upfront. Use the turns table to identify
interesting segments, then pull selectively:

```bash
$SESSION_TOOL <id> --turn <range> --raw
```

Prioritize:
- Turns with corrections or reversals (and the turns immediately before them)
- Turns with unusually long response times
- Turns where the user edited files themselves
- Sub-agent turns — what was the task, did the result land correctly?
- Any turn where the user signals something is worth remembering

### Produce the report

```markdown
# Session Review

**Session:** <id (first 8 chars)>
**Date:** <date>
**Duration:** <duration>
**Model:** <model>
**Turns:** <count>
**Summary:** <one sentence: what was the user trying to accomplish?>

---

## Context Gaps

Facts the agent didn't know, had to be told, or got wrong. Candidates for
AGENTS.md, project docs, or per-filetype rules.

- **Turn N** — "<quoted evidence>" — *agent assumed X; reality was Y*

## Capability Gaps

Places where a missing tool, script, or skill forced a longer path — inline
bash, multi-step workarounds, or manual steps the user had to perform.

- **Turn N** — "<quoted evidence>" — *agent lacked a tool for X; used Y
  instead*

## Process Failures

Corrections, reversals, repeated requests, tool denials, missing allow-list
entries, or moments where the user took over.

- **Turn N** — "<quoted evidence>" — *agent did X when asked for Y*

## Insights

Explicit requests to remember or reflect, end-of-session observations, or
moments where an agent might have learned something worth preserving.

- **Turn N** — "<quoted or paraphrased>" — *why this matters*

---
```

Leave any section empty with "— none found —" rather than padding it. Be
specific: quote directly, cite turn numbers, describe the shape of the
problem. Do not speculate about solutions.

---
name: session-review
description: Analyze Claude Code or Copilot session logs for insights, gaps,
  and learnings. Produces a report of findings with targeted suggestions for
  the highest-leverage ones.
disable-model-invocation: true
argument-hint: "[session-id | 'latest']"
allowed-tools: Agent, Read, Grep, Glob, Bash(python *)
---
# Session Review

## Goal

Agent sessions accumulate corrections, dead ends, missing context, and
occasional insights. The goal of this skill is to learn from these — as
AGENTS.md rules, new tools, scripts, or skills — making future agents faster
and less error-prone. The output is a report of findings followed by targeted
suggestions for the highest-leverage ones.

## Step 1: Select session tool

Based on your identity, use one of these commands as the `[TOOL]` reference.

| Agent          | Command                                            |
|----------------|----------------------------------------------------|
| Claude Code    | `python <skill-base-dir>/scripts/claude-sessions`  |
| GitHub Copilot | `python <skill-base-dir>/scripts/copilot-sessions` |
| Mistral Vibe   | `python <skill-base-dir>/scripts/vibe-sessions`    |

Use the full path to the script. Key usage:

```bash
[TOOL]                       # list sessions for current dir
[TOOL] -d <dir>              # list sessions for a directory
[TOOL] --list-dirs           # list directories with sessions
[TOOL] -n 10                 # limit number of listed sessions
[TOOL] <id>                  # summarize a session by id
[TOOL] <id> --raw            # full raw transcript for session
[TOOL] <id> --turn <range>   # transcript for specific turns (implies --raw)
[TOOL] --help                # show full options
```

## Step 2: Select session

Resolve `$ARGUMENTS` to a session ID:

| `$ARGUMENTS`       | Action                                      |
|--------------------|---------------------------------------------|
| `<id or prefix>`   | Use directly                                |
| `latest`           | Run `[TOOL] -n 1`, take the first result    |
| _(empty)_          | Run `[TOOL] -n 20`, then spawn a sub-agent  |

When listing, filter the session list to 2+ turns, then spawn a sub-agent
with the filtered list:

> - Fetch session summaries in list order and scan for these signals:
>   - **Corrections** — user restates or reverses an agent action
>   - **Repeated requests** — same ask appears more than once
>   - **Short dismissive messages** — terse rejections
>   - **User takeover** — user edits files or runs commands directly
>   - **Tool denials** — agent attempted a disallowed tool
>   - **Tool errors** — repeated failures or high error rate on a tool
>   - **Reflection signals** — user asks to remember or note something
> - Use `[TOOL] <session-id>` to fetch a session summary
> - Stop after 3 interesting candidates
> - Return session ID and one line of quoted evidence per candidate

Present a table of at most 10 sessions (by timestamp) — session ID, date &
time, duration, turn count, and notes. For the 3 interesting sessions use the
sub-agent's quoted evidence as the note; for the rest use the first prompt
from the tool output. Mark the 3 interesting session IDs in bold. Ask the
user which to review — or whether to search a different directory.

## Step 3: Analyze session

Spawn a sub-agent with the session ID and `[TOOL]` command:

> Get the session summary. Note the tool usage table — flag tools with high
> error rates or unexpectedly high call counts. Then use the turns table to
> identify interesting segments and pull selectively using `--turn <range>`.
> Do not read the full transcript upfront.
>
> Prioritize:
> - Turns with corrections or reversals (and the turns immediately before them)
> - Turns with unusually long response times
> - Turns where the user edited files themselves
> - Tool calls with errors, retries, or roundabout use (bash where a dedicated tool exists)
> - Sub-agent turns — what was the task, did the result land correctly?
> - Any turn where the user signals something is worth remembering
>
> Return all findings with turn numbers and direct quotes.

## Step 4: Report findings

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

## Step 5: Reflect and suggest

Re-read the report. Identify the 1–2 findings with the highest leverage —
the ones that, if addressed, would most improve future sessions. For each,
suggest a concrete remedy: an AGENTS.md rule, a new tool or script, or a
change to a skill. Do not suggest a remedy for every finding — only where
the pattern is clear and the fix is actionable.

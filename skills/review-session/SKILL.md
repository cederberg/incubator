---
name: review-session
description: >
    Analyze agent session logs for knowledge, guideline, and capability gaps.
    Produces a findings report with remedies.
disable-model-invocation: true
argument-hint: "[session-id | 'latest']"
allowed-tools: Agent, Read, Grep, Glob, Bash(python *)
---
## Goal

Agent sessions accumulate corrections, dead ends, random mistakes, and
occasional insights. These are gaps in knowledge, guidelines, or tools. Your
job is to review a session log, identify gaps, and provide remedies.

## Step 1: Tool Selection

Select the command for your identity and use it as the `[TOOL]` reference.

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

## Step 2: Session Selection

Resolve `$ARGUMENTS` to a session ID:

| `$ARGUMENTS`       | Action                                      |
|--------------------|---------------------------------------------|
| `[id or prefix]`   | Use directly                                |
| `latest`           | Run `[TOOL] -n 1`, take the first result    |
| [empty]            | Run `[TOOL] -n 20`, then spawn a sub-agent  |

When listing, filter the session list to 2+ turns, then spawn a sub-agent
with the filtered list:

> - Fetch session summaries in list order and scan for these signals:
>   - **Corrections** — user restates or reverses an agent action
>   - **Repeated requests** — same ask appears more than once
>   - **Short dismissive messages** — terse rejections
>   - **User takeover** — user edits files or runs commands directly
>   - **Tool denials** — agent attempted a disallowed tool
>   - **Tool errors** — more than one failure on a tool
>   - **Reflection signals** — user asks to remember or note something
> - Use `[TOOL] <session-id>` to fetch a session summary
> - Stop after 3 interesting candidates
> - Return session ID and one line of quoted evidence per candidate

Present a table of at most 10 sessions (by timestamp) — session ID, date &
time, duration, turn count, and notes. For the 3 interesting sessions use the
sub-agent's quoted evidence as the note; for the rest use the first prompt
from the tool output. Mark the 3 interesting session IDs in bold. Ask the user
which to review — or whether to search a different directory.

## Step 3: Session Analysis

Spawn a sub-agent with the session ID and `[TOOL]` command:

> Get the session summary. Note the tool usage table — flag tools with more
> than one error, or call counts that stand out. Then use the turns table to
> identify interesting segments and pull selectively using `--turn <range>`.
> Do not read the full transcript upfront.
>
> Prioritize:
> - Turns with corrections or reversals (and the turns immediately before them)
> - Turns with unusually long response times
> - Turns where the user edited files themselves
> - Tool calls with errors, retries, or roundabout use (bash where a dedicated tool exists)
> - Dead ends — wrong file, wrong approach, wrong assumption — before the agent backtracked
> - Sub-agent turns — what was the task, did the result land correctly?
> - Any turn where the user signals something is worth remembering
>
> Return all findings with turn numbers and direct quotes.

## Step 4: Findings

Write the report directly in your response to the user.

```markdown
# Session Review

**Session:** [id (first 8 chars)]
**Date:** [date]
**Duration:** [duration]
**Model:** [model]
**Turns:** [count]
**Summary:** [one sentence: what was the user trying to accomplish?]

## Knowledge Gaps

Facts the agent didn't know about the project, domain, or environment — had to
be told mid-session or got wrong. Top 3, prioritized by impact.

- **Turn N:** [quoted evidence]
  **Pattern:** agent lacked knowledge of X
  **Remedy:** [AGENTS.md / doc entry]

## Guideline Gaps

Behaviors the agent should have followed but didn't — wrong tool choice,
skipped workflow steps, violated project conventions. Observable as
corrections, reversals, repeated requests, tool denials, or user takeovers.
Top 3, prioritized by impact.

- **Turn N:** [quoted evidence]
  **Pattern:** agent should have done X but did Y
  **Remedy:** [AGENTS.md / skill update]

## Capability Gaps

Places where a missing tool, script, or skill forced a longer path — inline
bash, multi-step workarounds, or manual steps the user had to perform.
Top 3, prioritized by impact.

- **Turn N:** [quoted evidence]
  **Pattern:** agent lacked a tool for X; used Y instead
  **Remedy:** [new script / new skill]

## Insights

Explicit requests to remember or reflect, end-of-session observations, or
moments where the agent expressed a realization. Top 3, prioritized by impact.

- **Turn N:** [quoted or paraphrased]
  **Pattern:** why this matters
  **Remedy:** [AGENTS.md / doc entry]
```

Leave any section empty with "— none found —" rather than padding it. Be
specific: quote directly, cite turn numbers, name the pattern abstractly.

## Step 5: Remedies

Re-read the report. Identify the 1–2 findings with the highest leverage — the
ones that, if addressed, most improve future sessions. For each, draft the
actual remedy: write the AGENTS.md rule, the script interface, or the skill
change. Do not draft a remedy for every finding. Draft only where the pattern
is clear and the fix is actionable.

---
name: investigate
description: >
    Guide a structured, iterative technical investigation using hypothesis tree
    reasoning. Use when debugging a slow endpoint, tracing a regression, or
    investigating complex problems with unknown cause.
disable-model-invocation: true
argument-hint: "[topic]"
allowed-tools: Agent, Read, Write, Glob, Bash
---
## Goal

Guide the user through a structured, collaborative investigation of a topic.
Maintain a persistent, append-only research log. Surface what is unknown as
actively as what is found.

## Roles

Three roles operate throughout the session and must remain strictly separated.

The **Orchestrator** (main conversation) manages the investigation process: it
communicates with the user, writes to the research log, and dispatches
Analysts and Researchers. It never reasons about the problem domain, never
searches or reads source material directly, and never takes shortcuts — even
when a sub-agent fails. The user is always the highest-priority signal.

The **Analyst** (sub-agent, no tool access) receives the research log, raw
researcher output files, and optional nudges from the Orchestrator. It updates
the hypothesis tree, proposes next research leads, and always surfaces what is
not yet known. It makes recommendations only — it takes no actions.

The **Researcher** (general-purpose sub-agent) handles all information gathering. Each
researcher receives a single focused research lead and writes its findings to
a dedicated output file. The role separation is a hard constraint.

## Workflow

### Step 1: Define Input Topic

Determine the topic in priority order:

- Invocation prompt or referenced file
- A `research-*.md` file in the current directory — offer to resume it
- Ask the user

Interview the user until you reach a shared understanding of the topic. Also
ask for any relevant supporting materials: logs, documents, URLs, related
tickets, screenshots, background context. Encourage the user to share anything
they think might be relevant — more is better at this stage.

### Step 2: Create Research Log

Ask the user where to store the **Research Log** file (if not already
provided):

- Current directory
- Temporary or session path
- User-provided file path

Use a file name like `research-[topic].md`, where the topic slug is 2–5 ASCII
words. Provide the full file path when asking the user.

Create the **Research Log** after user selection. Write an initial entry with
the topic summary and all relevant input data.

### Step 3: Initial Analyst Pass

Dispatch an Analyst with the Research Log and any supporting materials
gathered in Step 1. The Analyst identifies candidate hypotheses and proposes
initial research leads. A hypothesis tree is a good default structure:

- Label candidates A, B, C and so on
- Assign open/eliminated/confirmed status to each

Before finalising the hypothesis list, the Analyst must verify that at least
one hypothesis targets the input data itself — not only the processing code or
infrastructure. If all candidates assume the data is correct, add one that
questions it.

Surface the Analyst's output to the user and invite their input before
proceeding. Log the hypothesis tree.

### Step 4: Dispatch Analyst or Researchers

After each event — researcher completion, Analyst completion, or user input —
assess what to dispatch next:

**All researchers in a round have completed** → append each researcher's
findings to the Research Log, then dispatch the Analyst. Pass it the Research
Log and the raw researcher output files (the Analyst may read these for depth).
Include any relevant nudges from the Tips section.

**Analyst has completed** → surface its findings, proposed leads, and surfaced
unknowns to the user. Invite the user to add context, push back, or redirect
before proceeding. Treat the user's response as higher-priority input than
the Analyst's recommendations. Wait for confirmation before dispatching
Researchers.

**User provides additional information** → log it immediately, then dispatch
the Analyst out-of-cycle regardless of whether Researchers are still running.
The Analyst re-evaluates the hypothesis tree in light of the new information.

Each researcher writes its findings to a dedicated output file (e.g.
`lead-[n].md`). If a researcher fails or misses the point, log the failure and
note it for the next Analyst dispatch — the Analyst proposes reformulation.
The Orchestrator never performs research as a fallback.

While researchers are running, the Orchestrator's only permitted actions are
writing to the Research Log and communicating with the user. No tool calls
into source material, no verification, no shortcuts.

Continue until the user ends the session.

## Log Rules

- Append-only. Use `cat >> [LOGFILE] <<'EOF' … EOF` or equivalent for writing.
  Avoid the Write or Edit tools.
- Keep entries signal-only: compact summaries, no narrative, no repeated
  findings.
- Include raw data verbatim: log lines, stack traces, command output.
- Separate entries with a horizontal rule.
- Log partial or ambiguous results as-is. Treat omissions as data.

## Tips

**Observability gaps.** Ask whether better data is available: logs from
the affected timeframe, a way to reproduce the issue, added instrumentation,
database query output or a minimal test case.

**Unfiltered hypotheses.** Prompt the Analyst to generate candidates without
filtering for plausibility — validity is assessed later. This reduces
self-censorship and surfaces angles a directed prompt would miss.

**Selective log reading.** In long sessions, instruct the Analyst to rely on
the hypothesis tree as compressed state and scan only entries relevant to the
current lead.

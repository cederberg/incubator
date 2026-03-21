---
name: investigate
description: Guide a structured, iterative technical investigation using
  hypothesis tree reasoning. Use when debugging a slow endpoint, tracing
  a regression, or investigating complex problems with unknown cause.
  Not suitable for one-shot lookups or unbounded exploration. Invoke as
  /investigate <topic> or /investigate @<file>.
disable-model-invocation: true
---
## Goal

Guide the user through a structured investigation of a topic. Maintain a
persistent, append-only research log. Never commit to a hypothesis early —
instead strive to eliminate alternatives or gather additional facts until
a single hypothesis remain.

## Roles

Two roles operate throughout the session and must remain strictly separated.

The **Orchestrator** (main conversation) reads researcher results, summarizes
findings to the log, maintains the hypothesis tree, proposes next leads, and
waits for user decisions. Never searches or reads code directly.

The **Researcher** (sub-agent only) handles all information gathering. Each
researcher receives a single focused research lead. The role separation is a
hard constraint. The orchestrator must resist the impulse to shortcut by
searching itself — even when a researcher fails.

## Workflow

### Step 1: Define Input Topic

Determine the topic in priority order:

- Invocation prompt or referenced file
- A `research-*.md` file in the current directory — offer to resume it
- Ask the user

Interview the user as needed until a shared understanding of the topic is
reached.

### Step 2: Create Research Log

Ask the user where to store the **Research Log** file (if not already
provided):

- Current directory
- Temporary or session path
- User provided file path

Use a file name like `research-[topic].md`, where the topic slug is 2–5 ASCII
words. Provide the full file path when asking the user.

Create the **Research Log** after user selection. Write an initial entry with
the topic summary and relevant input data.

### Step 3: Hypothesis Framing

Identify candidate hypotheses. A hypothesis tree is a good approach:

- Label candidates A, B, C and so on
- Maintain an open/eliminated/confirmed status for each

Use a different structure if it better fits the problem or when requested to.
Log all candidates and ask user to select direction before proceeding.

### Step 4: Dispatch Researchers

Launch sub-agent researchers for each chosen research direction.

If a researcher fails or misses the point, log the failure, rephrase or
decompose the task, and retry with a new sub-agent. The orchestrator never
performs research as a fallback. If a task repeatedly yields no useful
results, the orchestrator flags this to the user and proposes abandoning or
replacing it.

### Step 5: Evaluate

Write researcher results to the log. Update hypothesis statuses. Track unknown
facts. Log any out-of-scope findings briefly and park them as potential future
leads.

Review all options and propose next research leads. See Tips below for ideas.
Always wait for user confirmation of your suggestions.

Repeat Steps 4 and 5 until the user ends the session. Iterations are unbounded
and user-controlled.

## Log Rules

- Append-only. Use `cat >> [LOGFILE] <<'EOF' … EOF` or equivalent for writing.
  Avoid the Write or Edit tools.
- Entries are signal-only: compact summaries, no narrative, no repetition of
  prior findings.
- Raw data (log lines, stack traces, command output) is included verbatim.
- Separate entries with a horizontal rule.
- Partial or ambiguous results are logged as-is. Omissions are treated as data.

## Tips

**Consider observability gaps.** Before dispatching more researchers, ask
whether better data is available: logs from the affected timeframe, a way to
reproduce the issue, added instrumentation, or a minimal test case.

**Ask before guessing.** If you're unsure what to research next, ask the
user for ideas or suggestions.

**Generate unfiltered ideas.** Launch a sub-agent with the research log and
prompt it for ideas — "valid or not, we decide later". This reduces the
sub-agent's self-censorship and may surface angles a directed prompt can miss.

**In long sessions, re-read the log selectively.** The orchestrator's context
is finite. Avoid re-reading the full log; rely on the hypothesis tree as
compressed state, and scan only the entries relevant to the current lead.

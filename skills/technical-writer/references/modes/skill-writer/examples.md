# Curated Examples

These excerpts are taken verbatim from real skill files. Each illustrates
a structural or stylistic principle that rules alone cannot fully convey.
Study what each section commits to — and what it deliberately omits.

---

## Example 1: A Description That Lists All Entry Points

**Source:** `skill-creator` — frontmatter (`anthropics/skills`)

```yaml
description: Create new skills, modify and improve existing skills, and measure skill
  performance. Use when users want to create a skill from scratch, edit, or optimize
  an existing skill, run evals to test a skill, benchmark skill performance with
  variance analysis, or optimize a skill's description for better triggering accuracy.
```

**What this shows:**

The description leads with the capability in three parallel verb phrases
("Create … modify … measure"). The "Use when" clause then exhaustively
lists every distinct entry point as a separate clause. Each entry point
is a concrete user intent, not a synonym of the others. A user arriving
at this skill via any one of six different paths finds their intent
reflected in the description. The total length (under 1024 characters)
keeps the description within spec.

**What an agent typically writes instead:**

```yaml
description: Helps create and manage skills for AI agents.
```

The agent version names the domain without listing entry points. A user
who wants to run benchmarks, review trigger accuracy, or write evaluation
tests cannot tell from this description whether the skill is relevant.

---

## Example 2: A Hard Constraint With Its Temptation Named

**Source:** `investigate` — Roles section (this repo)

> ## Roles
>
> Two roles operate throughout the session and must remain strictly
> separated.
>
> The **Orchestrator** (main conversation) reads researcher results,
> summarizes findings to the log, maintains the hypothesis tree, proposes
> next leads, and waits for user decisions. Never searches or reads code
> directly.
>
> The **Researcher** (sub-agent only) handles all information gathering.
> Each researcher receives a single focused research lead. The role
> separation is a hard constraint. The orchestrator must resist the
> impulse to shortcut by searching itself — even when a researcher fails.

**What this shows:**

The constraint is stated once ("must remain strictly separated"), then
the specific temptation it guards against is named explicitly ("even when
a researcher fails"). That final clause is doing the real work: without
it, an agent facing a failed researcher will reason that searching
directly is a reasonable fallback. Naming the temptation forecloses it.
A constraint that only states the rule leaves the agent to discover the
edge cases itself.

**What an agent typically writes instead:**

> The orchestrator manages the investigation. The researcher handles
> information gathering. Keep these roles separate.

The agent version states the separation without naming what breaks it.
An agent following this will respect the rule in normal conditions and
abandon it the moment a sub-agent fails — exactly the case where it
matters most.

---

## Example 3: A Decision Tree That Eliminates Prose If-Else

**Source:** `webapp-testing` — Decision Tree section (`anthropics/skills`)

> ## Decision Tree: Choosing Your Approach
>
> ```
> User task → Is it static HTML?
>     ├─ Yes → Read HTML file directly to identify selectors
>     │         ├─ Success → Write Playwright script using selectors
>     │         └─ Fails/Incomplete → Treat as dynamic (below)
>     │
>     └─ No (dynamic webapp) → Is the server already running?
>         ├─ No → Run: python scripts/with_server.py --help
>         │        Then use the helper + write simplified Playwright script
>         │
>         └─ Yes → Reconnaissance-then-action:
>             1. Navigate and wait for networkidle
>             2. Take screenshot or inspect DOM
>             3. Identify selectors from rendered state
>             4. Execute actions with discovered selectors
> ```

**What this shows:**

Each branch point is a binary observable condition ("Is it static HTML?",
"Is the server already running?"), not a judgment call. Each leaf is an
imperative instruction with no ambiguity. The ASCII format expresses a
decision structure that would require four or five nested if-then
paragraphs in prose — and is more scannable than any of them. The
parenthetical "(dynamic webapp)" and "(below)" cross-reference are the
only prose additions, and both are structurally necessary.

**What an agent typically writes instead:**

> Depending on the type of application and whether a server is running,
> you may need to use different approaches. For static HTML files, you
> can read them directly. For dynamic webapps, you'll typically need to
> start a server first, though sometimes the server is already running,
> in which case you can go straight to automation.

The agent version uses "depending on", "you may need", "you'll
typically", and "sometimes" — four hedges in two sentences. None of the
three conditions are named; all three actions are blurred into
optionality.

---

## Example 4: A Tips Section for Soft Guidance (Experimental)

**Source:** `investigate` — Tips section (this repo)

> ## Tips
>
> **Consider observability gaps.** Before dispatching more researchers,
> ask whether better data is available: logs from the affected timeframe,
> a way to reproduce the issue, added instrumentation, or a minimal test
> case.
>
> **Ask before guessing.** If you're unsure what to research next, ask
> the user for ideas or suggestions.
>
> **Generate unfiltered ideas.** Launch a sub-agent with the research log
> and prompt it for ideas — "valid or not, we decide later". This reduces
> the sub-agent's self-censorship and may surface angles a directed
> prompt can miss.
>
> **In long sessions, re-read the log selectively.** The orchestrator's
> context is finite. Avoid re-reading the full log; rely on the
> hypothesis tree as compressed state, and scan only the entries relevant
> to the current lead.

**What this shows:**

Tips is a home for guidance that doesn't belong in the workflow — not
mandatory steps, not hard constraints, but judgment nudges that address
real failure modes. Each tip is bold-headed and self-contained. They can
be read in any order and skipped without breaking the workflow. This
keeps the workflow section clean while preserving guidance that would
otherwise be lost or, worse, embedded as mandatory steps.

Note that this pattern is experimental. It is not yet clear whether
agents reliably consult a Tips section during execution, or treat it as
supplementary material. Use it for guidance where occasional
non-compliance is acceptable — not for constraints that must hold.

# Curated Examples

These five excerpts are taken verbatim from real skill files. Each illustrates a structural or stylistic principle that rules alone cannot fully convey. Study what each section commits to — and what it deliberately omits.

---

## Example 1: A Description That Separates Trigger from Anti-trigger

**Source:** `docx` — frontmatter (`anthropics/skills`)

```yaml
description: "Use this skill whenever the user wants to create, read, edit, or
  manipulate Word documents (.docx files). Triggers include: any mention of 'Word
  doc', 'word document', '.docx', or requests to produce professional documents
  with formatting like tables of contents, headings, page numbers, or letterheads.
  Also use when extracting or reorganizing content from .docx files, inserting or
  replacing images in documents, performing find-and-replace in Word files, working
  with tracked changes or comments, or converting content into a polished Word
  document. If the user asks for a 'report', 'memo', 'letter', 'template', or
  similar deliverable as a Word or .docx file, use this skill. Do NOT use for
  PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document
  generation."
```

**What this shows:**

The description names multiple layers of trigger signal: file-extension mentions (`.docx`), keyword phrases ("Word doc"), format-specific features (tables of contents, letterheads), specific operations (find-and-replace, tracked changes), and deliverable nouns ("report", "memo", "letter", "template"). Each layer catches a different user phrasing. The "Do NOT use for" clause names the nearest confusable formats — PDFs, spreadsheets, Google Docs — rather than generic exclusions like "unrelated tasks". A description that only states what the skill does will misfire on near-neighbours; one that lists observable triggers and names specific exclusions will not.

**What an agent typically writes instead:**

```yaml
description: Helps create and edit Word documents.
```

The agent version states the skill's subject without naming any trigger conditions. Every document-adjacent request matches it equally, so the model cannot distinguish when to load it versus when not to.

---

## Example 2: A Description That Lists All Entry Points

**Source:** `skill-creator` — frontmatter (`anthropics/skills`)

```yaml
description: Create new skills, modify and improve existing skills, and measure skill
  performance. Use when users want to create a skill from scratch, edit, or optimize
  an existing skill, run evals to test a skill, benchmark skill performance with
  variance analysis, or optimize a skill's description for better triggering accuracy.
```

**What this shows:**

The description leads with the capability in three parallel verb phrases ("Create … modify … measure"). The "Use when" clause then exhaustively lists every distinct entry point as a separate clause. Each entry point is a concrete user intent, not a synonym of the others. A user arriving at this skill via any one of six different paths finds their intent reflected in the description. The total length (under 1024 characters) keeps the description within spec.

**What an agent typically writes instead:**

```yaml
description: Helps create and manage skills for AI agents.
```

The agent version names the domain without listing entry points. A user who wants to run benchmarks, review trigger accuracy, or write evaluation tests cannot tell from this description whether the skill is relevant.

---

## Example 3: An Activation Table With a Labelled Default

**Source:** `distill-context` — Activation section (this repo)

> ## Activation
>
> | Mode | When to use |
> |---|---|
> | **update** (default) | AGENTS.md exists and you want to sync it with recent changes |
> | **research** | No AGENTS.md exists, or user explicitly requests a full analysis |
> | **realign** | AGENTS.md exists but is structurally wrong, bloated, or stale |

**What this shows:**

Three modes cover every relevant state of `AGENTS.md`: it exists and is current; it does not exist; it exists but is wrong. The conditions are mutually exclusive, phrased as observable facts ("AGENTS.md exists", "does not exist", "is structurally wrong"), not abstract intent categories. The default is labelled inline with `(default)` in the Mode column rather than in a separate section, which prevents a reader from missing it. No mode description requires knowledge of another mode to be understood.

**What an agent typically writes instead:**

> ## Activation
>
> | Mode | Description |
> |---|---|
> | **update** | Updates an existing AGENTS.md to reflect recent code changes |
> | **research** | Performs a full project analysis to build a new AGENTS.md |
> | **realign** | Restructures an existing AGENTS.md that has become stale or bloated |
>
> Default mode: **update**

The agent version renames the column "Description" and populates it with what each mode does rather than when to use it. The reader must already understand the difference between "sync recent changes" and "full analysis" to know which applies to their situation. The default is moved to a separate line below the table where it is easily skipped. Both failures compound: a reader who cannot identify their own situation from the descriptions will also miss the fallback.

---

## Example 4: A Decision Tree That Eliminates Prose If-Else

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

Each branch point is a binary observable condition ("Is it static HTML?", "Is the server already running?"), not a judgment call. Each leaf is an imperative instruction with no ambiguity. The ASCII format expresses a decision structure that would require four or five nested if-then paragraphs in prose — and is more scannable than any of them. The parenthetical "(dynamic webapp)" and "(below)" cross-reference are the only prose additions, and both are structurally necessary.

**What an agent typically writes instead:**

> Depending on the type of application and whether a server is running, you may need to use different approaches. For static HTML files, you can read them directly. For dynamic webapps, you'll typically need to start a server first, though sometimes the server is already running, in which case you can go straight to automation.

The agent version uses "depending on", "you may need", "you'll typically", and "sometimes" — four hedges in two sentences. None of the three conditions are named; all three actions are blurred into optionality.

---

## Example 5: Parallel Sub-agent Dispatch With Exact Specifications

**Source:** `full-review` — Workflow section (`wshobson/commands`)

> Execute parallel reviews using Task tool with specialized agents:
>
> ## 1. Code Quality Review
> - Use Task tool with subagent_type="code-reviewer"
> - Prompt: "Review code quality and maintainability for: $ARGUMENTS. Check for code smells, readability, documentation, and adherence to best practices."
> - Focus: Clean code principles, SOLID, DRY, naming conventions
>
> ## 2. Security Audit
> - Use Task tool with subagent_type="security-auditor"
> - Prompt: "Perform security audit on: $ARGUMENTS. Check for vulnerabilities, OWASP compliance, authentication issues, and data protection."
> - Focus: Injection risks, authentication, authorization, data encryption
>
> ## 3. Architecture Review
> - Use Task tool with subagent_type="architect-reviewer"
> - Prompt: "Review architectural design and patterns in: $ARGUMENTS. Evaluate scalability, maintainability, and adherence to architectural principles."
> - Focus: Service boundaries, coupling, cohesion, design patterns

**What this shows:**

Each sub-agent section has exactly three items: which tool and subagent type to use, what prompt to pass (including `$ARGUMENTS` substitution), and what focus area constrains the review. The structure is identical for every agent, making parallelism explicit: six sections in identical format signals that six agents run concurrently. No prose narrative wraps the list. The prompt text is quoted verbatim — the executing agent receives exactly this string.

**What an agent typically writes instead:**

> Launch multiple review agents in parallel to check different aspects of the code. One should focus on code quality and another on security, while a third reviews the architecture.

The agent version names three categories without specifying which tool to use, what prompt to pass, or how `$ARGUMENTS` is substituted. An executing agent would have to invent these parameters, producing inconsistent results.

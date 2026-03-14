# Curated Examples

These five excerpts are taken verbatim from real skill files. Each illustrates a structural or stylistic principle that rules alone cannot fully convey. Study what each section commits to — and what it deliberately omits.

---

## Example 1: A Mode Table That Answers Three Questions Per Row

**Source:** `technical-writer` — Modes section

> | Mode | When to use | Output |
> |---|---|---|
> | `system-overview` | Document an internal system for a technically literate audience | `OVERVIEW.md` in project root |
> | `readme` | Write or rewrite a project-level README | `README.md` in project root |
> | `generic` | User supplies their own topics and document structure | Path specified by user |

**What this shows:**

Every row answers three questions — what to call this mode, when to choose it, and what it produces. The "When to use" column is a condition, not a description of the output. The "Output" column is an exact path or convention, not a category. No row overlaps with another: the three conditions are mutually exclusive.

**What an agent typically writes instead:**

> | Mode | Description |
> |---|---|
> | `system-overview` | Creates a system overview document |
> | `readme` | Creates a README for your project |
> | `generic` | General purpose document creation |

The agent version describes the output rather than the condition. It omits the output artifact entirely. A reader cannot determine when to use a mode, or what they will get, from the description alone.

---

## Example 2: A Role Declaration That Names Both Sides of the Contract

**Source:** `write-system-overview` — Your Role section

> You are the workflow manager. You launch sub-agents and confirm that each phase has produced non-empty output. You do not read reference files, research files, or drafts yourself. Pass file paths to sub-agents and let them read what they need.

**What this shows:**

Four sentences. The first names the role. The second states the positive obligation. The third is an explicit prohibition — and it is as important as the obligation, because without it the agent will drift into reading files it is supposed to delegate. The fourth states the correct behaviour as an imperative. The word "yourself" in sentence three is load-bearing: it clarifies that the agent orchestrates, it does not execute.

**What an agent typically writes instead:**

> As the workflow manager, you'll coordinate the different phases of the document creation process, working with specialized sub-agents to research, outline, write, and review the final document. Make sure to verify that each phase completes successfully before moving on.

The agent version states the obligation in a single passive sentence and follows it with a vague instruction ("make sure to verify"). The prohibition is absent. Nothing prevents the agent from reading files directly rather than delegating.

---

## Example 3: Mode Detection That Guards Against Silent Misrouting

**Source:** `technical-writer` — Mode Detection section (excerpt; additional modes follow the same pattern)

> If the user specifies a mode, use it. Otherwise, infer from the request:
>
> - "write a README" / "document this project" / "generate a README" → `readme`
> - "write a system overview" / "document this system" / "write an overview" → `system-overview`
> - User explicitly names `generic`, or provides their own topics/template structure → `generic`
>
> `generic` is never inferred silently. Only use it when the user explicitly requests it or supplies their own document structure.
>
> If the mode cannot be determined from the request, ask the user before proceeding.

**What this shows:**

Every mode has at least one concrete example phrase, and each phrase maps to exactly one mode with no overlap. The final catch-all (`generic`) carries a named guard: a phrase that prohibits silent inference. The fallback when no mode matches is explicit action (ask), not silent default. The structure is: direct lookup → phrase inference → named guard → fallback. Each layer handles a distinct input state.

**What an agent typically writes instead:**

> Determine the appropriate mode based on what the user is asking for. Use `generic` if nothing else seems to fit.

The agent version offers no inference criteria and uses `generic` as a silent default — exactly the failure the guard prevents. Any sufficiently novel user request will produce the wrong output silently.

---

## Example 4: Processing Rules as Labelled Imperatives

**Source:** `distill-context` — Update Mode section

> **Extraction rules:**
> - **Permanence:** Only extract information that remains true over time; ignore transient steps
> - **Novelty:** Skip standard practices; only record project-specific facts
> - **Conflict:** Newer conversations supersede existing AGENTS.md entries
> - **Redundancy:** Don't document what is already in README or enforced by tooling
> - **Density:** Aggressive pruning; one line per fact

**What this shows:**

Each rule has a bold label (a single noun) and a precise imperative statement. No sentence explains why the rule exists. The label functions as a category name that can be referenced elsewhere ("Apply the Density rule here"). The semicolon in each item separates the positive instruction from its inverse — both halves together eliminate ambiguity that the positive alone would leave. Five rules cover the full decision space without overlap.

**What an agent typically writes instead:**

> When extracting information, focus on things that are generally applicable and will remain relevant over time. Try to avoid duplicating information that's already covered in other files. Be concise and don't include too much detail.

The agent version uses three hedges ("generally", "try to avoid", "too much") and gives no named categories. A reader cannot determine what to do with a specific piece of information because the rules offer no decision criteria.

---

## Example 5: Sub-Agent Isolation Justified by Named Failure Modes

**Source:** `technical-writer` — Workflow section

> This workflow requires separate sub-agents for each phase. Do not combine them.
>
> Context growth degrades style adherence. Self-review is attachment-biased. Mode collapse (researching while writing, validating instead of critiquing) is the primary cause of poor output. Separate sub-agents with isolated contexts solve all three problems.

**What this shows:**

The rule comes first as an imperative with no hedging. The justification follows as three precise failure-mode names: context growth, attachment bias, and mode collapse. Each failure mode is named, not described at length. "Mode collapse" is defined with a parenthetical example, which is the right amount of explanation — enough to recognise the failure, not enough to explain how to prevent it. This paragraph earns its place because it prevents a specific, costly shortcut. A skill that does not justify isolation will have agents combining phases.

**What an agent typically writes instead:**

> It's best to use separate sub-agents for each phase so that the context stays manageable and each agent can focus on its specific task without being influenced by what came before.

The agent version uses passive ("it's best") and vague causation ("influenced by what came before"). The failure modes are unnamed. Nothing in this paragraph would stop an agent from combining phases when it judges the context to be "manageable".


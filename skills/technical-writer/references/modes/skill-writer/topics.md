# Research Topics: Skill File

## 1. Task and Scope

- **Primary behaviour** — what the skill accomplishes from the user's perspective; the activity or workflow it automates
- **Domain** — the category the skill belongs to (context management, documentation, code review, orchestration, etc.)
- **Explicit exclusions** — what the skill must not do; guardrails that prevent scope creep

## 2. Activation and Triggers

- **Synonyms and phrases** — all user phrasings that should invoke the skill; identify phrasing categories (e.g., imperative request, noun description, task variant) to ensure the set is complete
- **Auto-activation signal** — whether the user's description states that Claude should trigger this skill automatically from context or only on explicit invocation; extract the stated condition, not a judgment about what it should be
- **Ambiguity cases** — requests where the skill might be invoked incorrectly; what guard condition or clarifying question prevents misrouting

## 3. Modes and Variants

- **Named modes** — each mode's label, the condition that distinguishes it from others, and the output it produces
- **Default mode** — which mode fires when the user does not specify; whether this can be stated explicitly
- **Mode detection logic** — how to infer the correct mode from user phrasing; whether silent misrouting is possible
- **Review variant** — whether the skill supports reviewing an existing artifact vs. producing a new one; how the pipeline differs

## 4. Workflow Requirements

- **Step sequence** — the steps the skill must execute, in order; which steps can run concurrently
- **Sub-agent requirements** — which steps require isolated context; what each sub-agent's role, inputs, and output file are
- **Processing rules** — what to extract, include, or exclude; how to handle conflicts; density and novelty criteria
- **Cycle limits** — whether any review-revise loop requires an upper bound on iterations

## 5. Input and Output Contracts

- **Runtime inputs** — what the skill reads (user description, existing files, `$ARGUMENTS`, codebase)
- **Final output artifacts** — every artifact the skill delivers to the user; exact file path, naming convention, or destination directory
- **Output templates** — whether structured final output needs explicit placeholders; the fields each template must include

## 6. Reference File Requirements

- **Delegation candidates** — whether the skill is complex enough to delegate instructions to separate reference files
- **Consumer mapping** — for each reference file: which sub-agent reads it, and its purpose
- **Sharing vs. specialisation** — whether reference files are shared across modes or need to be mode-specific

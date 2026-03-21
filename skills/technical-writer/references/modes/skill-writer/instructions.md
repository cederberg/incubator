# Mode Instructions: Skill File

## Phase 1: Discovery

**Manager-conducted.** Conduct an interview directly; do not delegate it to a sub-agent.

Confirm the skill name and target directory before proceeding. Default to `skills/<skill-name>/`; use the project's agent-specific path if one exists (e.g. `.claude/skills/<skill-name>/`).

Scan the conversation for anything already established: workflow steps, phrasings, file paths, corrections. If the user has provided an existing skill file, read it before interviewing — it answers most topics directly. Interview the user on any topics not yet covered:

- **Use cases** — 2-3 concrete scenarios in the form: *Trigger* (what the user says or does) → *Steps* (what the skill does) → *Result* (what the user gets). These anchor everything that follows.
- **Task** — what the skill does; what it explicitly excludes
- **Invocation model** — auto-activate from context, or slash-command-only for skills with side effects or narrow scope
- **Triggers and anti-triggers** — phrasings that activate it; adjacent tasks that should not
- **Modes** — named variants, distinguishing conditions, and default
- **Outputs** — every artifact, with exact paths or naming conventions
- **Inputs and dependencies** — arguments, files, tools, preconditions
- **Edge cases and guardrails** — failure handling; hard constraints
- **Success criteria** — what a correct result looks like

Group open questions into a single message. Wait for answers before proceeding.

Write `$WORK_DIR/discovery.md` covering each topic above, with Use cases first. Omit sections that do not apply (e.g. omit Triggers if slash-command-only; omit Modes if single-mode).

## Phase 2: Research

Conditional — skip when `$WORK_DIR/discovery.md` is sufficient. Run only when there is something to investigate beyond the interview:

| Situation | Topic | Output file |
|---|---|---|
| Skill involves a specific external tool or API | Invocation patterns, common edge cases, conventions to embed | domain.md |
| Skill references other skills or agents in the project | Contracts, overlaps, triggering conflicts | context.md |

When Phase 2 runs, pass its output files and `$WORK_DIR/discovery.md` together to Phase 3.

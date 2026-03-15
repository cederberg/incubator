# Mode Instructions: Skill File

## Pre-flight

Before starting Phase 1:

1. Identify the skill name and directory. If the user has not provided a name, ask: "What should the skill be called?"
2. Confirm the skill directory path. Default to `skills/<skill-name>/` relative to the project root. Use the agent-specific local skills path if the project follows one (e.g. `.claude/skills/<skill-name>/` for Claude Code projects).

## Phase 1: Discovery

Ignore the default Phase 1 instructions (enumerate modules, external systems, documentation files). Research the skill's task domain and workflow requirements, not a codebase.

Read the user's description and any existing skill files in the project directory. Write `$WORK_DIR/discovery.md` with three sections:

- **Task** — the task the skill must perform
- **Activation conditions** — the activation conditions, if any; note if the skill is slash-command-only with no auto-activation
- **Output artifacts** — any output artifacts or file paths specified

## Phase 5: Review

Use the **"review instructions"** label. Pass `references/modes/skill-writer/examples.md` and `references/modes/skill-writer/checklist.md` to the reviewer.

## Research Topics

| Topic | Description | Output file |
|---|---|---|
| Task, activation & modes | What the skill accomplishes and its domain; any explicit exclusions or guardrails; all user phrasings that trigger it, whether auto-activation applies, and what prevents misrouting; each named mode's label, distinguishing condition, and output; default mode and detection logic; whether a review variant exists and how the pipeline differs | task.md |
| Workflow, contracts & reference files | The step sequence, which steps run concurrently, and any cycle limits on review-revise loops; sub-agent requirements — role, inputs, and output file for each; processing rules (what to extract, include, or exclude); runtime inputs and final output artifacts with exact paths or naming conventions; whether reference files are warranted, which sub-agent reads each, and whether they are shared across modes or mode-specific | workflow.md |

Adapt scopes to the actual skill using `$WORK_DIR/discovery.md`. Use two researchers for skills with multiple modes or sub-agent workflows; use one (covering all topics) for single-step skills.

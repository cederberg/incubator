# Research Topics: Skill File

| Topic | Description | Output file |
|---|---|---|
| Task, activation & modes | What the skill accomplishes and its domain; any explicit exclusions or guardrails; all user phrasings that trigger it, whether auto-activation applies, and what prevents misrouting; each named mode's label, distinguishing condition, and output; default mode and detection logic; whether a review variant exists and how the pipeline differs | task.md |
| Workflow, contracts & reference files | The step sequence, which steps run concurrently, and any cycle limits on review-revise loops; sub-agent requirements — role, inputs, and output file for each; processing rules (what to extract, include, or exclude); runtime inputs and final output artifacts with exact paths or naming conventions; whether reference files are warranted, which sub-agent reads each, and whether they are shared across modes or mode-specific | workflow.md |

Adapt scopes to the actual skill using `$WORK_DIR/discovery.md`. Use two researchers for skills with multiple modes or sub-agent workflows; use one (covering all topics) for single-step skills.

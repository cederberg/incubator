# Skill File Structure Template

Use frontmatter to tell the agent when to load the skill. Write the skill
body as instructions the agent follows when the skill runs.

---

## Frontmatter (required)

```yaml
---
name: skill-name
description: What the skill does and when to use it. Max 1,024 characters.
---
```

Follow the [Agent Skills open standard](https://agentskills.io/specification)
for core fields (`name`, `description`, `allowed-tools`, `license`,
`compatibility`, `metadata`). For Claude Code-specific fields
(`disable-model-invocation`, `user-invocable`, `context`, `agent`, `model`,
`argument-hint`, `hooks`, string substitutions), see the
[Claude Code skills reference](https://docs.anthropic.com/en/docs/claude-code/skills).

Note that Gemini CLI and OpenAI Codex only read `name` and `description`;
Claude Code-specific fields are inert but harmless in other agents.

**`name`** — kebab-case, max 64 characters.

**`description`** — what the skill does and the conditions that trigger it.
Max 1,024 characters. Include both trigger conditions and explicit exclusions.

**`disable-model-invocation: true`** — slash-command-only. Set for skills
with side effects or narrow scope.

---

## Workflow (required)

A numbered list of steps. Keep steps short and imperative.

1. Read [input].
2. Extract [facts].
3. Write [output] to [path].

For orchestrator skills, use named steps with a sub-agent label, inputs,
and an output artifact:

```
### Step N: [Step Name]

Run a **[role]** sub-agent with:
- [Input file or path]

The agent writes its output to `$WORK_DIR/[output].md`.
```

**Bundle a script** when an operation is deterministic and repeatable —
validation, formatting, data extraction, API calls. Place scripts in
`scripts/` and reference them by path.

---

## Optional Sections

Use any of the following when they apply. Order them to suit the skill —
there is no required sequence. Omit any that don't add value.

### Activation

Use when the skill auto-activates from context. Omit for slash-command-only
skills. State the conditions that trigger the skill. Choose one form:

- **Prose trigger** — a single sentence, without hedging. Use for
  single-mode skills.
- **Modes table** — a table with Mode and "When to use" columns. Label the
  default inline with `(default)`. Guard any catch-all mode against silent
  inference.
- **Decision tree** — an ASCII tree where each branch is a binary observable
  condition and each leaf is an imperative instruction. Use when a modes
  table would require nested if-else logic.

If the skill has entry guards — conditions that must be true before it can
run correctly — include them here.

### Goal

A brief statement of what the skill is trying to achieve. Useful when the
purpose is not obvious from the name or workflow alone.

### Roles

Use when the skill delegates to sub-agents with strict separation of
responsibilities. Name each role, state what it does and what it must never
do. Name the specific temptation each constraint guards against.

### Inputs

Use when the skill accepts arguments or files, especially when the source
is ambiguous or prioritised. List sources in priority order.

### Output

Use when the output path or format is non-obvious. State the exact file
path, naming convention, or output template for every artifact.

**For structured output**, an inline template with explicit placeholders
might be needed.

**For file output**, name the path explicitly.

### Tips

Use for judgment nudges that don't belong in the workflow — not mandatory
steps, not hard constraints, but guidance for non-obvious situations. Each
tip should be bold-headed and self-contained. Note: agents may not reliably
consult this section; use it only for guidance where occasional
non-compliance is acceptable.

### Reference Files

Use for multi-file skills only. List every file delegated to a sub-agent.

| File | Used By | Purpose |
|---|---|---|
| `references/roles/role-name.md` | [Agent label] | [One-line purpose] |

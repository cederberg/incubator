# Skill File Structure Template

Use frontmatter to tell the agent when to load the skill. Write the skill body as instructions the agent follows when the skill runs.

---

## Frontmatter

```yaml
---
name: skill-name
description: What the skill does and when to use it. Max 1,024 characters.
---
```

Follow the [Agent Skills open standard](https://agentskills.io/specification) for core fields (`name`, `description`, `allowed-tools`, `license`, `compatibility`, `metadata`). For Claude Code-specific fields (`disable-model-invocation`, `user-invocable`, `context`, `agent`, `model`, `argument-hint`, `hooks`, string substitutions), see the [Claude Code skills reference](https://docs.anthropic.com/en/docs/claude-code/skills).

Note that Gemini CLI and OpenAI Codex only read `name` and `description`; Claude Code-specific fields are inert but harmless in other agents.

**`name`** — kebab-case, max 64 characters.

**`description`** — what the skill does and the conditions that trigger it. Max 1,024 characters. Include both trigger conditions and explicit exclusions.

**`disable-model-invocation: true`** — slash-command-only. Set for skills with side effects or narrow scope.

---

## Skill Body

### Section Order

1. **Frontmatter** (required)
2. **Skill Name / H1** (required)
3. **Activation** (optional — omit for slash-command-only skills)
4. **Preconditions** (optional)
5. *(other sections as needed)*
6. **Workflow** (required)
7. **Output** (required)
8. **Reference Files** (optional — for multi-file skills only)

---

### Skill Name (H1)

Use the skill name as the document's H1 heading. Match the `name` frontmatter field in human-readable form.

---

### Activation

State the conditions that trigger the skill. Choose one form:

- **Prose trigger** — a single sentence stating the condition, without hedging. Use for single-mode skills.
- **Modes table** — a table with Mode and "When to use" columns. Label the default inline with `(default)`. Guard any catch-all mode against silent inference. See Example 3 in `examples.md`.
- **Decision tree** — an ASCII tree where each branch is a binary observable condition and each leaf is an imperative instruction. Use when a modes table would require nested if-else logic. See Example 4 in `examples.md`.

---

### Preconditions

List guards that must be true before the skill runs. Include only guards that, if violated, would cause incorrect output or require mid-run intervention.

---

### Workflow

**For simple skills** — a numbered list of steps:

1. Read [input].
2. Extract [facts].
3. Write [output] to [path].

**For orchestrator skills** — named phases, each with a sub-agent label, inputs, and an output file.

**Bundle a script** when an operation is deterministic and repeatable — validation, formatting, data extraction, API calls. Code is unambiguous; a language instruction for the same operation will produce inconsistent results. Place scripts in `scripts/` and reference them by path.

```
### Phase N: [Phase Name]

Run a **[role]** sub-agent with:
- [Input file or path]

The agent writes its output to `$WORK_DIR/[output].md`.
```

Include an isolation rationale when a phase could merge with an adjacent one. State confirmation steps between phases (e.g., verify output is non-empty before proceeding).

---

### Output

State the exact file path, naming convention, or output template for every artifact the skill produces.

**For structured output**, use a template with explicit placeholders:

```
> # [Title]
>
> ## [Section]
> [Placeholder]
```

**For file output**, name the path explicitly: `Write the result to $WORK_DIR/draft.md, then copy to [final path].`

---

### Reference Files

List every file delegated to a sub-agent in a table.

| File | Used By | Purpose |
|---|---|---|
| `references/roles/role-name.md` | [Agent label] | [One-line purpose] |


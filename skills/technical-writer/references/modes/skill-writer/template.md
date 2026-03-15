# Skill File Structure Template

Structure a SKILL.md file in two parts: frontmatter and a skill body. Frontmatter tells the agent when to load the skill. The body contains the instructions the agent follows when the skill runs.

---

## Frontmatter

```yaml
---
name: skill-name
description: What the skill does and when to use it. Max 1,024 characters.
---
```

Follow the [Agent Skills open standard](https://agentskills.io), supported across Claude Code, Gemini CLI, OpenAI Codex, and Cursor. Mark fields not in the core standard as Claude Code–specific.

**Portability caveat:** Gemini CLI and OpenAI Codex only read `name` and `description` from `SKILL.md`. Those tools silently ignore all other fields. Claude Code–specific fields still work correctly in Claude Code; they cause no errors elsewhere — they are just inert.

### Core fields (standard)

**`name`** — kebab-case, lowercase letters, numbers, and hyphens only, max 64 characters. If omitted, the agent uses the skill directory name.

**`description`** — what the skill does and the conditions that trigger it. Max 1,024 characters. This is the primary signal the agent uses for automatic activation. Include when to trigger, not only what the skill does — omitting the trigger condition causes under-activation. Include when NOT to trigger to prevent misfires on near-neighbours.

**`allowed-tools`** — comma- or space-delimited list of tools the agent may use without per-use approval when this skill is active. Example: `Read, Grep, Glob` for a read-only skill. Claude Code extends this with scoped syntax: `Bash(python3 scripts/*)` permits only matching `Bash` calls.

**`license`** — license name or path to a bundled license file. Example: `MIT` or `LICENSE.txt`. No functional effect; used by skill registries and auditing tools.

**`compatibility`** — short free-text note on environment requirements (max 500 chars). Experimental; support varies across agents. Omit unless the skill has hard dependencies that would silently fail in a wrong environment.

**`metadata`** — arbitrary key-value map for client-specific properties. Example:

```yaml
metadata:
  author: your-org
  version: "1.0"
```

No functional effect in any current agent; used by registries and catalogues.

### Invocation control (Claude Code)

**`disable-model-invocation: true`** — prevent the agent from loading this skill automatically. Use for workflows with side effects that should only run when you type `/skill-name`. Omit for skills that should activate from context.

**`user-invocable: false`** — hide from the `/` menu. Use for background knowledge skills that the agent should load automatically but that have no meaningful user command. Omit for everything else.

### Execution fields (Claude Code)

**`context: fork`** — run the skill in an isolated subagent context. Use when the skill must run without conversation history contaminating its output. The subagent receives the skill body as its prompt and has no access to the current conversation.

**`agent`** — which subagent type to use when `context: fork` is set. Options: `Explore`, `Plan`, `general-purpose`, or any custom agent from `.claude/agents/`. Omit to use `general-purpose`.

**`model`** — model to use when this skill runs. Omit to inherit the session model.

**`argument-hint`** — hint shown during `/` autocomplete. Example: `[issue-number]` or `[filename] [format]`.

**`hooks`** — lifecycle hooks scoped to this skill.

### String substitutions (Claude Code)

Use these in skill body content:

- `$ARGUMENTS` — all text typed after `/skill-name`
- `$ARGUMENTS[N]` or `$N` — specific argument by 0-based index
- `${CLAUDE_SESSION_ID}` — current session identifier
- `${CLAUDE_SKILL_DIR}` — absolute path to the skill's directory
- `` !`command` `` — run a shell command before the skill loads; output replaces the placeholder

---

## Skill Body

### Section Order

1. **Frontmatter** (required)
2. **Skill Name / H1** (required)
3. **Activation** (optional)
4. **Preconditions** (optional)
5. *(other sections as needed)*
6. **Workflow** (required)
7. **Output** (required)
8. **Reference Files** (optional)

---

### Skill Name (H1)

Use the skill name as the document's H1 heading. Match the `name` frontmatter field in human-readable form.

---

### Activation

Include this section for skills that activate automatically from context. Omit it for skills intended to be invoked only as a slash command.

State the conditions that trigger the skill and, for multi-mode skills, how the agent selects among modes. Choose one of three forms depending on branching complexity.

**Prose trigger** — a short statement of the condition that triggers a single-mode skill. State it without hedging.

**Modes table** — a table defining each named mode with its triggering condition and output. Label the default mode inline with `(default)` in the Mode column. Include inference rules directly in or after the table. See Example 3 in `examples.md`.

Guard any catch-all or generic mode against silent inference. A mode labelled "generic" or "other" must require explicit user selection.

**Decision tree** — an ASCII tree for branching logic too complex for a modes table. Make each branch point a binary observable condition and each leaf an imperative instruction. See Example 4 in `examples.md`.

A modes table may appear inside Activation or immediately after it — both placements are valid.

---

### Preconditions (optional)

List guards that must be true before the skill runs. Include only guards that, if violated, would cause incorrect output or require mid-run intervention. Omit this section if no such guards exist.

---

### Workflow

**For simple skills** — a numbered list of steps:

1. Read [input].
2. Extract [facts].
3. Write [output] to [path].

**For orchestrator skills** — named phases, each with a sub-agent label, inputs, and an output file.

Include a rationale for sub-agent isolation when the phase could plausibly merge with an adjacent phase without apparent loss.

```
### Phase N: [Phase Name]

Run a **[role]** sub-agent with:
- [Input file or path]
- [Input file or path]

The agent writes its output to `$WORK_DIR/[output].md`.
```

State explicit confirmation steps between phases (e.g., verify output is non-empty before proceeding).

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

**For file output**, name the path explicitly:

```
Write the result to `$WORK_DIR/draft.md`, then copy to [final path].
```

---

### Reference Files (for multi-file skills)

List every file delegated to a sub-agent in a table.

| File | Used By | Purpose |
|---|---|---|
| `references/roles/role-name.md` | [Agent label] | [One-line purpose] |
| `references/rules/rule-name.md` | [Agent label] | [One-line purpose] |
| `references/modes/<mode>/file.md` | [Agent label] | [One-line purpose] |

---

## Section Selection

- **Activation** — required for skills that activate automatically from context; omit for slash-command-only skills. Choose the form — prose trigger, modes table, or decision tree — based on branching needs.
- **Modes table** — place inside Activation or immediately after it.
- **Preconditions** — include only when a violated guard would cause incorrect output or require mid-run intervention.
- **Reference Files** — include when the skill delegates to sub-files.

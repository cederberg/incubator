# Skill File Structure Template

A SKILL.md file has two parts: frontmatter that tells Claude when to load the skill, and a body with instructions Claude follows when the skill runs.

---

## Frontmatter

```yaml
---
name: skill-name
description: What the skill does and when to use it. Max 1,024 characters.
---
```

The frontmatter fields follow the [Agent Skills open standard](https://agentskills.io), which is supported across Claude Code, Gemini CLI, OpenAI Codex, and Cursor. Fields not in the core standard are noted as Claude Code–specific.

**Portability caveat:** Gemini CLI and OpenAI Codex only read `name` and `description` from `SKILL.md`. All other fields are silently ignored by those tools. Claude Code–specific fields still work correctly in Claude Code; they cause no errors elsewhere — they are just inert.

### Core fields (standard)

**`name`** — kebab-case, lowercase letters, numbers, and hyphens only, max 64 characters. If omitted, the skill directory name is used.

**`description`** — what the skill does and the conditions that trigger it. Max 1,024 characters. This is the primary signal the agent uses for automatic activation. A description that states only what the skill does (not when) will be under-triggered. A description that also states when NOT to trigger will prevent misfires on near-neighbours.

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

**`disable-model-invocation: true`** — prevent Claude from loading this skill automatically. Use for workflows with side effects that should only run when you type `/skill-name`. Omit for skills that should activate from context.

**`user-invocable: false`** — hide from the `/` menu. Use for background knowledge skills that Claude should load automatically but that have no meaningful user command. Omit for everything else.

### Execution fields (Claude Code)

**`context: fork`** — run the skill in an isolated subagent context. The skill body becomes the subagent's prompt; it has no access to the current conversation. Use when the skill must run without conversation history contaminating its output.

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

### Skill Name (H1)

The skill name as the document's H1 heading. Matches the `name` frontmatter field in human-readable form.

---

### Modes (for multi-mode skills)

A table defining each named mode.

| Mode | When to use | Output |
|---|---|---|
| `mode-name` | The distinguishing condition for this mode | The artifact produced |

Include every mode. State the default in the Mode Detection section.

### Mode Detection (for multi-mode skills)

Explicit inference rules covering every mode. State the default or fallback explicitly.

```
If the user specifies a mode, use it. Otherwise, infer from the request:
- [user phrasing A] / [user phrasing B] → `mode-a`
- [user phrasing C] → `mode-b`

[Mode X] is never inferred silently. Use it only when the user explicitly requests it.

If the mode cannot be determined from the request, ask the user before proceeding.
```

---

### Activation (for single-mode skills)

The condition that triggers this skill. State it without hedging.

---

### Preconditions (optional)

A bullet list of guards that must be true before the skill runs. Include only guards that, if violated, would cause the skill to produce incorrect output or require the user to intervene mid-run. Omit this section if no such guards exist.

---

### Your Role (for orchestrator skills)

One paragraph. State what you do and what you do NOT do. Name the sub-agent roles you manage.

---

### Workflow

**For simple skills** — a numbered list of steps:

1. Read [input].
2. Extract [facts].
3. Write [output] to [path].

**For orchestrator skills** — named phases, each with a sub-agent label, inputs, and an output file.

Include a rationale for sub-agent isolation when the phase could plausibly be merged with an adjacent phase without apparent loss.

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

The exact file path, naming convention, or output template for every artifact the skill produces.

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

A table listing every file delegated to a sub-agent.

| File | Used By | Purpose |
|---|---|---|
| `references/roles/role-name.md` | [Agent label] | [One-line purpose] |
| `references/rules/rule-name.md` | [Agent label] | [One-line purpose] |
| `references/modes/<mode>/file.md` | [Agent label] | [One-line purpose] |

---

## Section Selection

- **Modes** and **Mode Detection** appear together; omit both for single-mode skills.
- **Your Role** is required for orchestrator skills; omit for simple procedural skills.
- **Preconditions** are optional; include only when a guard, if violated, would cause incorrect output or require mid-run intervention.
- **Reference Files** is required for any skill that delegates to sub-files.

# Skill File Structure Template

A SKILL.md file has two parts: frontmatter that tells Claude when to load the skill, and a body with instructions Claude follows when the skill runs.

---

## Frontmatter

```yaml
---
name: skill-name
description: One to two sentences — what the skill does and when to use it.
synonyms: [trigger phrase, alternate phrase]
---
```

**`name`** — kebab-case identifier. Required.

**`description`** — what the skill does and the conditions that trigger it. Required. The description is the primary signal Claude uses for automatic activation; a description that states only what the skill does (not when) will be underused.

**`synonyms`** — additional user phrasings that invoke this skill. Optional; omit if the skill requires explicit invocation only.

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

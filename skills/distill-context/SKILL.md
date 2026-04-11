---
name: distill-context
description: "Creates and maintains AGENTS.md, the agent context file for a project. Trigger when the user says \"distill context\", \"update AGENTS.md\", \"init agent context\", or \"sync context\"."
disable-model-invocation: true
argument-hint: "[update|research|realign]"
allowed-tools: Read, Write, Glob, Bash
---

# distill-context

## Activation

| Mode | When to use |
|---|---|
| **update** (default) | AGENTS.md exists and you want to sync it with recent changes |
| **research** | No AGENTS.md exists, or user explicitly requests a full analysis |
| **realign** | AGENTS.md exists but is structurally wrong, bloated, or stale |

## File Resolution

`AGENTS.md` is the canonical file name used throughout these instructions. If
it doesn't exist, check for these files instead (and use if exists):

| File | Agent |
|---|---|
| `AGENTS.md` | Preferred — agent-neutral |
| `CLAUDE.md` | Claude Code |
| `GEMINI.md` | Gemini CLI |
| `.github/copilot-instructions.md` | GitHub Copilot |

---

## AGENTS.md Format

All modes produce or maintain files in this format:

```
# AGENTS.md
*[project tagline — ≤12 words, what it does and why/how]*

## References
- [README.md] — [3–5 words]
- [build tool] — [how to list targets, or omit if self-evident]

## Goals & Ethos
[project goals, design philosophy — guidance for decisions]

## Code Style
[brevity rules, naming, patterns]

## Constraints
[hard no's: specific deps to avoid, behavior requirements]

## Design Notes
[hard-won technical facts: pipeline, artifacts, non-obvious constraints]
```

**Rules:**
- Agent-focused — complements README, never duplicates it
- Pointer principle — point to files, don't reproduce their content
- Build tool owns commands — never list build/test/lint commands inline
- Omit empty sections; bullet points under each section; brevity is critical

The core sections above are the starting point. Additional H2 sections may be added over time
for distinct topics that don't fit elsewhere — e.g. `## Testing`, `## CI & Release`,
`## Known Gotchas`, or deep-dive topics like `## Multiline Merging`.

---

## Update Mode (default)

No clarifying questions. Operate fully automatically; user reviews result afterwards.

**Processing logic:**

1. Read current `AGENTS.md` (or `CLAUDE.md`)
2. Get last-modified date via git: `git log -1 --format=%aI -- AGENTS.md`
3. Find archived conversation files matching `.agent/memory/conversation-YYYY-MM-DD-HHMM.md`
   newer than that date — these are the primary source of new facts
4. Process chronologically (oldest first) in batches of 5: read 5 files, update AGENTS.md,
   then continue with the next batch. This keeps context bounded and ensures learnings aren't
   lost when processing a large backlog of conversations.
5. Only read git commits or source files if no conversation archives exist, or if the user
   explicitly requests it

**Extraction rules:**
- **Permanence:** Only extract information that remains true over time; ignore transient steps
- **Novelty:** Skip standard practices; only record project-specific facts
- **Conflict:** Newer conversations supersede existing AGENTS.md entries
- **Redundancy:** Don't document what is already in README or enforced by tooling
- **Density:** Aggressive pruning; one line per fact

**Writing rules:**
- Add new H2 sections for distinct new topics
- Append to existing sections only when clearly additive
- Never duplicate content already in README/DEVELOPMENT.md
- Verify before saving: pointer principle, no inline commands, no empty sections

---

## Research Mode

Follow instructions in `references/research.md`

---

## Realign Mode

Follow instructions in `references/realign.md`

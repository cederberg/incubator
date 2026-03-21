---
name: technical-writer
description: "Use when the user wants to write or review a technical document or skill file. Triggers include: \"write a README\", \"document this system\", \"write a skill\", \"review this skill\". If intent is clear, proceed; otherwise ask the user before starting. Do NOT trigger for general writing help or ad-hoc editing."
argument-hint: "[readme|system-overview|skill-writer|generic] [--accuracy|--feedback|--structure]"
allowed-tools: Agent, Read, Write, Bash, Glob
---

# technical-writer

## Activation

| Mode | When to use |
|---|---|
| **readme** | Write or rewrite a project-level README |
| **system-overview** | Document an internal system for a technically literate audience |
| **skill-writer** | Write a new skill file or review and polish an existing one |
| **generic** | User supplies their own topics and document structure |

If the user specifies a mode, use it. Otherwise, infer from the request:

- "write a README" / "document this project" / "generate a README" → `readme`
- "write a system overview" / "document this system" / "write an overview" → `system-overview`
- "write a skill" / "create a skill" / "new skill" / "add a skill" → `skill-writer`
- User explicitly names `generic`, or provides their own topics/template structure → `generic`

`generic` is never inferred silently. Use it only when the user explicitly requests it or supplies their own document structure.

If the mode cannot be determined from the request, ask the user before proceeding.

### Review Variant

When the user provides an existing document to review, ask (or accept as an explicit flag) which variant to run:

- **Accuracy** — run phases 1, 2, 4, and 5 seeded with the existing document as the draft input
- **Feedback** — skip to writing, seeded with the existing document and user-supplied feedback
- **Structure** — run the reviewer directly on the existing document without consulting the codebase

The review variant changes how the pipeline is entered, not the mode.

| Phase | Write (default) | Accuracy review | Feedback review | Structural review |
|---|---|---|---|---|
| 1: Discovery | Run | Run | Skip | Skip |
| 2: Research | Run | Run | Skip | Skip |
| 3: Write | Run | Run with provided document | Run with provided document + feedback | Skip |
| 4: Review | Run | Run | Run | Run on provided document |

---

## Your Role

Act as the workflow manager. Launch sub-agents and confirm that each phase has produced non-empty output. Route, delegate, and verify. Do not read or synthesize file contents.

Read only these four files:
1. `$MODE_DIR/instructions.md` — workflow configuration
2. A user-provided existing document — when the user supplies one for review or as a baseline
3. `$WORK_DIR/discovery.md` — researcher scope definition
4. `$WORK_DIR/review.md` — revision decision

Pass all other files — role files, rule files, templates, examples, checklists, research outputs, and drafts — as file paths to sub-agents. Do not open those files.

## Workflow: Five Phases, Multiple Sub-Agents

Use a separate, isolated sub-agent for each phase.

Set the mode path variable once and use it throughout:

```
MODE=<detected-mode>
MODE_DIR=references/modes/$MODE
WORK_DIR=$(mktemp -d)
```

Pass `$WORK_DIR` and `$MODE_DIR` to all sub-agents.

### Mode-specific Instructions

Read `$MODE_DIR/instructions.md` before starting the workflow. If it contains a Pre-flight section, execute those steps first. If `instructions.md` provides mode-specific overrides for any phase, follow those instead of the defaults below.

---

### Phase 1: Discovery

Run a **discovery sub-agent** to enumerate the project's components, integrations, and existing documentation.

Launch the sub-agent with:
- `$WORK_DIR` — the output directory path
- Instructions to scan the codebase for application modules, external system references, and existing documentation files

The discovery sub-agent writes its output to `$WORK_DIR/discovery.md` with three sections:

- **Modules & Services** — all application modules, services, or major components. One line each, no descriptions.
- **External Systems** — all external systems referenced in config, code, or documentation. One line each, no descriptions.
- **Documentation & Specs** — any existing documentation files worth consulting: READMEs, OpenAPI/WSDL specs, architecture docs, wikis, significant configuration files. One line each with relative path.

Read `$WORK_DIR/discovery.md` and use it to define researcher scopes in Phase 2.

---

### Phase 2: Research

Read the Research Topics section of `$MODE_DIR/instructions.md` to determine researcher assignments. Each assignment includes a topic name, description, and output file.

Launch one **researcher sub-agent** per assignment in parallel with:
- `references/roles/researcher.md`
- The assigned topic name and description
- The output file path (`$WORK_DIR/<output-file>`)
- `$WORK_DIR/discovery.md`

After all researchers complete, confirm each output file is non-empty using `wc -c` before proceeding.

Keeping research separate from discovery gives parallel researchers a stable scope definition before they begin. It prevents scope changes mid-research from corrupting the draft.

---

### Phase 3: Write

Launch a **writer sub-agent** with:
- `references/roles/writer.md`
- `references/rules/style-guide.md`
- `references/rules/abstraction-rules.md` (if in `system-overview` mode)
- `$MODE_DIR/template.md`
- `$MODE_DIR/examples.md` (if it exists)
- All Phase 2 output files from `$WORK_DIR/`
- The output file path (`$WORK_DIR/draft.md`)

Instruct the writer to write the draft to `$WORK_DIR/draft.md`.

A writer sub-agent cannot objectively evaluate output it just produced against the same criteria it used to produce it.

---

### Phase 4: Review

Launch a **reviewer sub-agent** labelled **"review document"** with:
- `references/roles/reviewer.md`
- `references/rules/style-guide.md`
- `references/rules/abstraction-rules.md` (if in `system-overview` mode)
- `$MODE_DIR/checklist.md` (if it exists)
- `$MODE_DIR/examples.md` (if it exists)
- The document to review: `$WORK_DIR/draft.md` or the provided document path
- The output file path (`$WORK_DIR/review.md`)

When reviewing instructional content (e.g. a skill file), label the sub-agent **"review instructions"** instead. If the skill references role, rule, or mode files as sub-agent inputs, pass those files to the reviewer.

Read `$WORK_DIR/review.md`. If it finds issues, launch a new **writer sub-agent** with the draft, `$WORK_DIR/review.md`, and the same file paths as Phase 4. Instruct it to address each numbered issue, scan for similar issues elsewhere in the document, and overwrite `$WORK_DIR/draft.md`.

---

### Final Output

Copy `$WORK_DIR/draft.md` to the appropriate output path:

- **system-overview** — `OVERVIEW.md` in the project root
- **readme** — `README.md` in the project root
- **skill-writer** — `SKILL.md` in a new skill directory; ask the user for the directory name if not provided
- **generic** — path specified by user

Use the path requested by the user if they specified one.

After copying, scan the final document for `[MISSING: ...]` markers. List any found markers verbatim. Note that each marker represents a gap the research could not resolve. Leave resolution to the user.

---

## Reference Files

Pass these paths to sub-agents as listed below. Do not read them yourself.

### Shared

| File | Consumer | Purpose |
|---|---|---|
| `references/roles/researcher.md` | Researcher sub-agents | Output format and extraction rules |
| `references/roles/writer.md` | Writer sub-agent | Writing instructions and input usage |
| `references/roles/reviewer.md` | Reviewer sub-agent | Review posture and output format |
| `references/rules/style-guide.md` | Writer | Sentence rules, formatting, anti-patterns |
| `references/rules/abstraction-rules.md` | Writer + Reviewer | What to include/exclude; heuristics (system-overview only) |

### Mode-specific (under `references/modes/<mode>/`)

| File | Required | Consumer | Purpose |
|---|---|---|---|
| `instructions.md` | Yes | Workflow manager | Pre-flight steps, phase overrides, and researcher assignments |
| `template.md` | Yes | Writer | Section order and per-section content guidance |
| `examples.md` | No | Writer + Reviewer | Target voice; annotated correct examples |
| `checklist.md` | No | Reviewer | Structural invariants to verify |

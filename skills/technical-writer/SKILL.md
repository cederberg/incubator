---
name: technical-writer
description: "Use when the user wants to write or review a technical document or skill file. Triggers include: \"write a README\", \"document this system\", \"write a skill\", \"review this skill\". If intent is clear, proceed; otherwise ask the user before starting. Do NOT trigger for general writing help or ad-hoc editing."
---

# technical-writer

## Activation

| Mode | When to use | Output |
|---|---|---|
| **system-overview** | Document an internal system for a technically literate audience | `OVERVIEW.md` in project root |
| **readme** | Write or rewrite a project-level README | `README.md` in project root |
| **skill-writer** | Write a new skill file or review and polish an existing one | `SKILL.md` in a skill directory |
| **generic** | User supplies their own topics and document structure | Path specified by user |

If the user specifies a mode, use it. Otherwise, infer from the request:

- "write a README" / "document this project" / "generate a README" → `readme`
- "write a system overview" / "document this system" / "write an overview" → `system-overview`
- "write a skill" / "create a skill" / "new skill" / "add a skill" → `skill-writer`
- "review this skill" / "improve this skill" / "polish this skill" → `skill-writer` + structural review variant
- User explicitly names `generic`, or provides their own topics/template structure → `generic`

`generic` is never inferred silently. Use it only when the user explicitly requests it or supplies their own document structure.

If the mode cannot be determined from the request, ask the user before proceeding.

### Review Variant

When the user provides an **existing document** to review rather than asking for a new one, ask (or accept as an explicit flag):

- **Structural** — run the reviewer directly on the existing document using the mode's `checklist.md` and shared style rules. The codebase is not consulted.
- **Accuracy** — run the full pipeline seeded with the existing document as the baseline draft. Research checks whether the document's claims reflect current reality.

Note that the review variant changes how the pipeline is entered, not the mode.

| Phase | Write (default) | Structural review | Accuracy review |
|---|---|---|---|
| 1: Discovery | Run | Skip | Run |
| 2: Research | Run | Skip | Run |
| 3: Outline | Run | Skip | Skip |
| 4: Write | Run | Skip | Run — seeded with provided document |
| 5: Review | Run | Run on provided document | Run |

---

## Your Role

Act as the workflow manager. Launch sub-agents and confirm that each phase has produced non-empty output. Do not read reference files, research files, or drafts yourself, except where explicitly instructed to. Pass file paths to sub-agents and let them read what they need.

## Workflow: Five Phases, Multiple Sub-Agents

Use separate sub-agents for each phase. Do not combine them.

Use isolated contexts for each sub-agent.

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

Run a **single lightweight discovery agent** to enumerate the project's components, integrations, and existing documentation.

The discovery agent writes its output to `$WORK_DIR/discovery.md` with three sections:

- **Modules & Services** — all application modules, services, or major components. One line each, no descriptions.
- **External Systems** — all external systems referenced in config, code, or documentation. One line each, no descriptions.
- **Documentation & Specs** — any existing documentation files worth consulting: READMEs, OpenAPI/WSDL specs, architecture docs, wikis, significant configuration files. One line each with relative path.

Read `$WORK_DIR/discovery.md` and use it to define researcher scopes in Phase 2.

---

### Phase 2: Research

Read the Research Topics section of `$MODE_DIR/instructions.md` to determine researcher assignments. Each assignment includes a topic name, description, and output file.

Launch one researcher sub-agent per assignment **in parallel** with:
- `references/roles/researcher.md`
- The assigned topic name and description
- The output file path (`$WORK_DIR/<output-file>`)
- `$WORK_DIR/discovery.md`

After all researchers complete, confirm each output file is non-empty using `wc -c` before proceeding.

---

### Phase 3: Outline

Launch a **single outliner sub-agent** with:
- `references/roles/outliner.md`
- `$MODE_DIR/template.md`
- All Phase 2 output files from `$WORK_DIR/`
- The output file path (`$WORK_DIR/outline.md`)

Instruct the outliner to write a document skeleton to `$WORK_DIR/outline.md`.

---

### Phase 4: Write

Launch a **single writer sub-agent** with:
- `references/roles/writer.md`
- `references/rules/style-guide.md`
- `references/rules/abstraction-rules.md` (if in `system-overview` mode)
- `$MODE_DIR/template.md`
- `$MODE_DIR/examples.md` (if it exists)
- `$WORK_DIR/outline.md`
- All Phase 2 output files from `$WORK_DIR/`
- The output file path (`$WORK_DIR/draft.md`)

Instruct the writer to fill in the outline section by section and write the draft to `$WORK_DIR/draft.md`.

---

### Phase 5: Review

Launch a **single reviewer sub-agent** labelled **"review document"** with:
- `references/roles/reviewer.md`
- `references/rules/style-guide.md`
- `references/rules/abstraction-rules.md` (if in `system-overview` mode)
- `$MODE_DIR/checklist.md` (if it exists)
- `$MODE_DIR/examples.md` (if it exists)
- The document to review: `$WORK_DIR/draft.md` or the provided document path

When reviewing instructional content (e.g. a skill file), label the sub-agent **"review instructions"** instead. If the skill being reviewed references role files, rule files, or mode files as sub-agent inputs, pass those files to the reviewer.

Read the reviewer's output. If it finds issues:
1. Launch a **new writer sub-agent** with the draft, the numbered review output, and the same file paths as Phase 4
2. Instruct it to address each numbered issue and overwrite `$WORK_DIR/draft.md`
3. Launch a **new reviewer sub-agent** labelled **"review document"** (or **"review instructions"**) to check the result

Repeat up to 3 cycles. Stop when the reviewer finds no issues or the cycle limit is reached.

---

### Final Output

Copy `$WORK_DIR/draft.md` to the appropriate output path:

| Mode | Default output path |
|---|---|
| `system-overview` | `OVERVIEW.md` in the project root |
| `readme` | `README.md` in the project root |
| `skill-writer` | `SKILL.md` in a new skill directory; ask the user for the directory name if not provided |
| `generic` | path specified by user |

Use the path requested by the user if they specified one.

After copying, scan the final document for `[MISSING: ...]` markers. List any found markers verbatim. Note that each represents a gap the research could not resolve; leave resolution to the user.

---

## Reference Files

### Shared

| File | Consumer | Purpose |
|---|---|---|
| `references/roles/researcher.md` | Researcher agents | Output format and extraction rules |
| `references/roles/outliner.md` | Outliner agent | Section selection, subsection naming, ordering rules |
| `references/roles/writer.md` | Writer agent | Writing instructions and input usage |
| `references/roles/reviewer.md` | Reviewer agent | Review posture and output format |
| `references/rules/style-guide.md` | Writer | Sentence rules, formatting, anti-patterns |
| `references/rules/abstraction-rules.md` | Writer + Reviewer | What to include/exclude; heuristics (system-overview only) |

### Mode-specific (under `references/modes/<mode>/`)

| File | Required | Consumer | Purpose |
|---|---|---|---|
| `instructions.md` | Yes | Workflow manager | Pre-flight steps, phase overrides, and researcher assignments |
| `template.md` | Yes | Outliner + Writer | Section order and per-section content guidance |
| `examples.md` | No | Writer + Reviewer | Target voice; annotated correct examples |
| `checklist.md` | No | Reviewer | Structural invariants to verify |

---
name: technical-writer
description: Writes or reviews technical documents and skill files with named modes. Supported modes: system-overview, readme, skill-writer, generic.
synonyms: [write system overview, write a README, document this system, document this project, write a skill, create a skill, review this skill]
---

# technical-writer

## Modes

| Mode | When to use | Output |
|---|---|---|
| `system-overview` | Document an internal system for a technically literate audience | `OVERVIEW.md` in project root |
| `readme` | Write or rewrite a project-level README | `README.md` in project root |
| `skill-writer` | Write a new skill file or review and polish an existing one | `SKILL.md` in a skill directory |
| `generic` | User supplies their own topics and document structure | Path specified by user |

## Mode Detection

If the user specifies a mode, use it. Otherwise, infer from the request:

- "write a README" / "document this project" / "generate a README" → `readme`
- "write a system overview" / "document this system" / "write an overview" → `system-overview`
- "write a skill" / "create a skill" / "new skill" / "add a skill" → `skill-writer`
- "review this skill" / "improve this skill" / "polish this skill" → `skill-writer` + structural review variant
- User explicitly names `generic`, or provides their own topics/template structure → `generic`

`generic` is never inferred silently. Only use it when the user explicitly requests it or supplies their own document structure.

If the mode cannot be determined from the request, ask the user before proceeding.

## Review Variant

When the user provides an **existing document** to review rather than asking for a new one to be written, ask (or accept as an explicit flag):

- **Structural** — run the reviewer directly on the existing document using the mode's `checklist.md` and shared style rules. The codebase is not consulted.
- **Accuracy** — run the full pipeline seeded with the existing document as the baseline draft. Research checks whether the document's claims reflect current reality.

Mode is inferred or specified as normal. The review variant does not change the mode — it changes how the pipeline is entered.

| Phase | Write (default) | Structural review | Accuracy review |
|---|---|---|---|
| 1: Discovery | Run | Skip | Run |
| 2: Research | Run | Skip | Run |
| 3: Outline | Run | Skip | Skip |
| 4: Write | Run | Skip | Run — seeded with provided document |
| 5: Review | Run | Run on provided document | Run |

---

## Your Role

You are the workflow manager. You launch sub-agents and confirm that each phase has produced non-empty output. You do not read reference files, research files, or drafts yourself, except where explicitly instructed to. Pass file paths to sub-agents and let them read what they need.

## Workflow: Five Phases, Multiple Sub-Agents

This workflow requires separate sub-agents for each phase. Do not combine them.

Context growth degrades style adherence. Self-review is attachment-biased. Mode collapse (researching while writing, validating instead of critiquing) is the primary cause of poor output. Separate sub-agents with isolated contexts solve all three problems.

Set the mode path variable once and use it throughout:

```
MODE=<detected-mode>
MODE_DIR=references/modes/$MODE
WORK_DIR=$(mktemp -d)
```

Pass `$WORK_DIR` and `$MODE_DIR` to all sub-agents so they read from consistent locations.

---

### Phase 1: Discovery

Run a **single lightweight discovery agent**. Its job is to enumerate the project's components, integrations, and existing documentation.

The discovery agent writes its output to `$WORK_DIR/discovery.md` with three sections:

- **Modules & Services** — all application modules, services, or major components. One line each, no descriptions.
- **External Systems** — all external systems referenced in config, code, or documentation. One line each, no descriptions.
- **Documentation & Specs** — any existing documentation files worth consulting: READMEs, OpenAPI/WSDL specs, architecture docs, wikis, significant configuration files. One line each with relative path.

Read `$WORK_DIR/discovery.md` and use it to define researcher scopes in Phase 2.

---

### Phase 2: Research

Read `$MODE_DIR/topics.md` to determine researcher assignments. Each researcher has a separate assigned topic name, description and output file.

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

The outliner writes a document skeleton to `$WORK_DIR/outline.md`.

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

The writer fills in the outline section by section and writes the draft to `$WORK_DIR/draft.md`.

---

### Phase 5: Review

Launch a **single reviewer sub-agent** labelled **"review document"** with:
- `references/roles/reviewer.md`
- `references/rules/style-guide.md`
- `references/rules/abstraction-rules.md` (if in `system-overview` mode)
- `$MODE_DIR/checklist.md` (if it exists)
- `$MODE_DIR/examples.md` (if it exists)
- The document to review: `$WORK_DIR/draft.md` or the provided document path

Note that when reviewing instructional content (e.g. a skill file) rather than a document, label the sub-agent **"review instructions"** instead. When the skill being reviewed references other files as sub-agent inputs (role files, rule files, mode files), pass those referenced files to the reviewer as well so it can verify the instructions are consistent with them.

Read the reviewer's output. If it finds issues:
1. Launch a **new writer sub-agent** with the draft, the numbered review output, and the same file paths as Phase 4
2. Instruct it to address each numbered issue and overwrite `$WORK_DIR/draft.md`
3. Launch a **new reviewer sub-agent** labelled **"review document"** (or **"review instructions"**) to check the result

Repeat up to 3 cycles. Stop when the reviewer finds no issues or the cycle limit is reached.

---

### Final Output

Once the review is finished, copy `$WORK_DIR/draft.md` to the appropriate output path:

| Mode | Default output path |
|---|---|
| `system-overview` | `OVERVIEW.md` in the project root |
| `readme` | `README.md` in the project root |
| `skill-writer` | `SKILL.md` in a new skill directory; ask the user for the directory name if not provided |
| `generic` | path specified by user |

Use the path requested by the user if they specified one.

After copying, scan the final document for `[MISSING: ...]` markers. If any are found, list them for the user verbatim and note that they represent gaps the research could not resolve. The user decides how to handle them.

---

## Skill-writer Mode

The `skill-writer` mode produces or improves a `SKILL.md` file. It differs from other modes in two ways: the subject of research is the skill's task domain and workflow requirements, not a codebase; and Phase 5 uses the **"review instructions"** label.

### Writing a new skill

Before starting Phase 1:

1. Identify the skill name and directory. If the user has not provided a name, ask: "What should the skill be called?" before proceeding.

2. Confirm the skill directory path. The default is `skills/<skill-name>/` relative to the project root, or `.claude/skills/<skill-name>/` if the project uses the local skills convention.

**Phase 1 override:** The general Phase 1 instructions (enumerate modules, external systems, documentation files) do not apply. Instead, the discovery agent reads the user's description and any existing skill files in the project directory. It writes `$WORK_DIR/discovery.md` with three sections: the task the skill must perform, the activation conditions mentioned, and any output artifacts or file paths specified.

Phase 5 uses the **"review instructions"** label and receives `references/modes/skill-writer/examples.md` and `references/modes/skill-writer/checklist.md`.

### Reviewing an existing skill

When the user provides an existing `SKILL.md` to review, use the structural review variant as defined in the Review Variant section above. The skill-writer-specific parameters are:

- Reviewer label: **"review instructions"**
- Checklist: `references/modes/skill-writer/checklist.md`
- Examples: `references/modes/skill-writer/examples.md`
- Writer (if issues found): also receives `references/modes/skill-writer/template.md`

---

## Generic Mode

Before starting Phase 1:

1. Extract research topics from the user's description. If the user has not provided topics, ask: "What areas should the researchers investigate?" before proceeding.

2. Materialise them into `$WORK_DIR/topics.md` following the format in `$MODE_DIR/topics.md`.

Proceed identically to any other mode from Phase 1 onward.

---

## Reference Files

### Shared

| File | Used By | Purpose |
|---|---|---|
| `references/roles/researcher.md` | Researcher agents | Output format and extraction rules |
| `references/roles/outliner.md` | Outliner agent | Section selection, subsection naming, ordering rules |
| `references/roles/writer.md` | Writer agent | Writing instructions and input usage |
| `references/roles/reviewer.md` | Reviewer agent | Review posture and output format |
| `references/rules/style-guide.md` | Writer | Sentence rules, formatting, anti-patterns |
| `references/rules/abstraction-rules.md` | Writer + Reviewer | What to include/exclude; heuristics (system-overview only) |

### Mode-specific (under `references/modes/<mode>/`)

| File | Required | Used By | Purpose |
|---|---|---|---|
| `topics.md` | Yes | Workflow manager | Researcher assignments: topic descriptions and output file paths |
| `template.md` | Yes | Outliner + Writer | Section order and per-section content guidance |
| `examples.md` | No | Writer + Reviewer | Target voice; annotated correct examples |
| `checklist.md` | No | Reviewer | Structural invariants to verify |

For `generic` mode, all four files are pre-authored in `references/modes/generic/`. `topics.md` serves as a template — the manager materialises the user's topics into `$WORK_DIR/topics.md` following its format. `examples.md` is not provided unless the user supplies one.

---
name: technical-writer
description: Writes technical documents with named modes. Supported modes: system-overview, readme.
synonyms: [write system overview, write a README, document this system, document this project]
---

# technical-writer

## Modes

| Mode | When to use | Output |
|---|---|---|
| `system-overview` | Document an internal system for a technically literate audience | `OVERVIEW.md` in project root |
| `readme` | Write or rewrite a project-level README | `README.md` in project root |

## Mode Detection

If the user specifies a mode, use it. Otherwise, infer from the request:

- "write a README" / "document this project" / "generate a README" → `readme`
- "write a system overview" / "document this system" / "write an overview" → `system-overview`

**If the mode cannot be determined from the request:** ask the user before proceeding. Do not default silently — a README written with system-overview structure, or a system overview written with README brevity, is a worse outcome than a clarification question.

---

## Your Role

You are the workflow manager. You launch sub-agents and confirm that each phase has produced non-empty output. You do not read reference files, research files, or drafts yourself. Pass file paths to sub-agents and let them read what they need.

## Workflow: Five Phases, Multiple Sub-Agents

**This workflow requires separate sub-agents for each phase. Do not combine them.**

Context growth degrades style adherence. Self-review is attachment-biased. Mode collapse (researching while writing, validating instead of critiquing) is the primary cause of poor output. Separate sub-agents with isolated contexts solve all three problems.

Set the mode path variable once and use it throughout:

```
MODE=<detected-mode>           # system-overview or readme
MODE_DIR=references/modes/$MODE
WORK_DIR=$(mktemp -d)
```

Pass `$WORK_DIR` and `$MODE_DIR` to all sub-agents so they read from consistent locations.

---

### Phase 1: Discovery

Run a **single lightweight discovery agent**. Its job is to enumerate the project's components, integrations, and existing documentation so that researcher scopes can be assigned without gaps.

The discovery agent writes its output to `$WORK_DIR/discovery.md` with three sections:

- **Modules & Services** — all application modules, services, or major components. One line each, no descriptions.
- **External Systems** — all external systems referenced in config, code, or documentation. One line each, no descriptions.
- **Documentation & Specs** — any existing documentation files worth consulting: READMEs, OpenAPI/WSDL specs, architecture docs, wikis, significant configuration files. One line each with relative path.

**Read `$WORK_DIR/discovery.md`** and use it to define researcher scopes in Phase 2.

---

### Phase 2: Research

Launch **multiple researcher sub-agents in parallel**, each scoped to a distinct topic from `$MODE_DIR/topics.md`.

Each researcher:
- Follows `references/roles/researcher.md`
- Receives `$WORK_DIR/discovery.md` to orient themselves
- Receives `$MODE_DIR/topics.md` to understand their scope
- Writes its full output to an assigned file in `$WORK_DIR/`

**Typical scope assignments by mode:**

**system-overview:**

| Agent | Scope | Output file |
|---|---|---|
| Researcher A | Topology & actors | `$WORK_DIR/topology.md` |
| Researcher B | Data contracts | `$WORK_DIR/contracts.md` |
| Researcher C | Processing logic | `$WORK_DIR/processing.md` |
| Researcher D | Vocabulary | `$WORK_DIR/vocabulary.md` |

**readme:**

| Agent | Scope | Output file |
|---|---|---|
| Researcher A | Purpose & audience | `$WORK_DIR/purpose.md` |
| Researcher B | Setup & prerequisites | `$WORK_DIR/setup.md` |
| Researcher C | Usage | `$WORK_DIR/usage.md` |
| Researcher D | Configuration | `$WORK_DIR/config.md` |
| Researcher E | Contribution & support | `$WORK_DIR/contributing.md` |

Adapt scopes to the actual project using `$WORK_DIR/discovery.md`. For a small project, two or three researchers may suffice.

After all researchers complete, confirm each output file is non-empty using `wc -c` before proceeding.

---

### Phase 3: Outline

Launch a **single outliner sub-agent** with:
- `references/roles/outliner.md`
- `$MODE_DIR/template.md`
- All Phase 2 output files from `$WORK_DIR/`

The outliner writes a document skeleton to `$WORK_DIR/outline.md`.

---

### Phase 4: Write

Launch a **single writer sub-agent** with:
- `references/roles/writer.md`
- `$MODE_DIR/template.md`
- `$MODE_DIR/examples.md`
- `references/rules/style-guide.md`
- `$WORK_DIR/outline.md`
- All Phase 2 output files from `$WORK_DIR/`

**For `system-overview` mode only**, also pass:
- `references/rules/abstraction-rules.md`

The writer fills in the outline section by section and writes the draft to `$WORK_DIR/draft.md`.

---

### Phase 5: Review

Launch a **single reviewer sub-agent** with:
- `references/roles/reviewer.md`
- `$MODE_DIR/examples.md`
- `$MODE_DIR/checklist.md`
- `$WORK_DIR/draft.md`

**For `system-overview` mode only**, also pass:
- `references/rules/abstraction-rules.md`

Read the reviewer's output. If it finds issues:
1. Launch a **new writer sub-agent** with the draft, the numbered review output, and the same file paths as Phase 4
2. Instruct it to address each numbered issue and overwrite `$WORK_DIR/draft.md`
3. Launch a **new reviewer sub-agent** to check the result

One review cycle is typically sufficient.

---

### Final Output

Once the review passes, copy `$WORK_DIR/draft.md` to the appropriate output path:

| Mode | Default output path |
|---|---|
| `system-overview` | `OVERVIEW.md` in the project root |
| `readme` | `README.md` in the project root |

Use the path requested by the user if they specified one.

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

| File | Used By | Purpose |
|---|---|---|
| `topics.md` | Researcher agents | Research scope definitions for this document type |
| `template.md` | Outliner + Writer | Section order and per-section content guidance |
| `examples.md` | Writer + Reviewer | Target voice; annotated correct examples |
| `checklist.md` | Reviewer | Structural invariants to verify |

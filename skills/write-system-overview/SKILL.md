---
name: write-system-overview
description: Writes a concise system overview for a technically literate audience.
---

# write-system-overview

## What This Produces

A concise Markdown system overview for a technically literate audience.

## Your Role

You are the workflow manager. You launch sub-agents and confirm that each phase has produced non-empty output. You do not read reference files, research files, or drafts yourself. Pass file paths to sub-agents and let them read what they need.

## Workflow: Five Phases, Multiple Sub-Agents

**This workflow requires separate sub-agents for each phase. Do not combine them.**

Context growth degrades style adherence. Self-review is attachment-biased. Mode collapse (researching while writing, validating instead of critiquing) is the primary cause of poor output. Separate sub-agents with isolated contexts solve all three problems.

---

### Phase 1: Discovery

Create a unique working directory and capture its path:

```
WORK_DIR=$(mktemp -d)
```

Pass `$WORK_DIR` to all sub-agents so they read and write from the same location.

Run a **single lightweight discovery agent**. Its job is to enumerate the system's components, integrations, and existing documentation so that researcher scopes can be assigned without gaps.

The discovery agent writes its output to `$WORK_DIR/discovery.md` with three sections:

- **Modules & Services** — all application modules, services, or major components (e.g. API layer, worker, inbound processor, batch jobs). One line each, no descriptions.
- **External Systems** — all external systems referenced in config, code, or comments. One line each, no descriptions.
- **Documentation & Specs** — any existing documentation files worth consulting: READMEs, OpenAPI/WSDL specs, architecture docs, wikis, significant configuration files. One line each with relative path.

**Read `$WORK_DIR/discovery.md`** and use it to define researcher scopes in Phase 2.

---

### Phase 2: Research

Launch **multiple researcher sub-agents in parallel**, each scoped to a distinct topic. Typical scopes:

| Agent | Scope | Output file |
|---|---|---|
| Researcher A | Topology & actors — external systems, infrastructure components, data flow direction | `$WORK_DIR/topology.md` |
| Researcher B | Data contracts — fields exchanged per actor (inbound/outbound), reliability notes | `$WORK_DIR/contracts.md` |
| Researcher C | Processing logic — named steps, sequence, business rules, filter conditions, outcomes | `$WORK_DIR/processing.md` |
| Researcher D | Vocabulary — named concepts: enums, status values, message types, event types, variants | `$WORK_DIR/vocabulary.md` |

Adapt scopes to the actual system using `$WORK_DIR/discovery.md`. For a small system, two researchers may suffice. For a large system, add more.

Each researcher follows [references/researcher.md](references/researcher.md) and receives `$WORK_DIR/discovery.md` to orient themselves before reading the codebase. Each writes its full output to its assigned file.

After all researchers complete, confirm each output file is non-empty using `wc -c` before proceeding.

---

### Phase 3: Outline

Launch a **single outliner sub-agent** with:
- [references/outliner.md](references/outliner.md)
- `references/structure-template.md`
- All Phase 2 output files from `$WORK_DIR/`

The outliner writes a document skeleton to `$WORK_DIR/outline.md`.

---

### Phase 4: Write

Launch a **single writer sub-agent** with:
- [references/writer.md](references/writer.md)
- `references/structure-template.md`
- `references/style-guide.md`
- `references/abstraction-rules.md`
- `references/examples.md`
- `$WORK_DIR/outline.md`
- All Phase 2 output files from `$WORK_DIR/`

The writer fills in the outline section by section and writes the draft to `$WORK_DIR/draft.md`.

---

### Phase 5: Review

Launch a **single reviewer sub-agent** with:
- [references/reviewer.md](references/reviewer.md)
- `references/abstraction-rules.md`
- `references/examples.md`
- `$WORK_DIR/draft.md`

Read the reviewer's output. If it finds issues:
1. Launch a **new writer sub-agent** with the draft, the numbered review output, and the same file paths as Phase 4
2. Instruct it to address each numbered issue and overwrite `$WORK_DIR/draft.md`
3. Launch a **new reviewer sub-agent** to check the result

One review cycle is typically sufficient.

---

### Final Output

Once the review passes, copy `$WORK_DIR/draft.md` to `OVERVIEW.md` in the project root, or to the path requested by the user.

---

## Reference Files

| File | Used By | Purpose |
|---|---|---|
| `references/researcher.md` | Researcher agents | Output format and extraction rules |
| `references/outliner.md` | Outliner agent | Section selection, subsection naming, ordering rules |
| `references/writer.md` | Writer agent | Writing instructions and input usage |
| `references/reviewer.md` | Reviewer agent | Review posture and output format |
| `references/style-guide.md` | Writer | Sentence rules, formatting, anti-patterns |
| `references/structure-template.md` | Outliner + Writer | Section order and per-section guidance |
| `references/abstraction-rules.md` | Writer + Reviewer | What to include/exclude; heuristics |
| `references/examples.md` | Writer + Reviewer | Target voice; annotated correct examples |

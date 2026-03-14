---
name: technical-writer
description: Writes or reviews technical documents with named modes. Supported modes: system-overview, readme, generic.
synonyms: [write system overview, write a README, document this system, document this project]
---

# technical-writer

## Modes

| Mode | When to use | Output |
|---|---|---|
| `system-overview` | Document an internal system for a technically literate audience | `OVERVIEW.md` in project root |
| `readme` | Write or rewrite a project-level README | `README.md` in project root |
| `generic` | User supplies their own topics and document structure | Path specified by user |

## Mode Detection

If the user specifies a mode, use it. Otherwise, infer from the request:

- "write a README" / "document this project" / "generate a README" → `readme`
- "write a system overview" / "document this system" / "write an overview" → `system-overview`
- User explicitly names `generic`, or provides their own topics/template structure → `generic`

**`generic` is never inferred silently.** Only use it when the user explicitly requests it or supplies their own document structure. A document written with a mismatched mode structure is a worse outcome than a clarification question.

**If the mode cannot be determined from the request:** ask the user before proceeding.

## Review Variant

When the user provides an **existing document** to review rather than asking for a new one to be written, ask (or accept as an explicit flag):

- **Structural** — skip research, discovery, and outline; run the reviewer agent directly on the existing document using the mode's `checklist.md` and shared style rules. No codebase access required.
- **Accuracy** — run the full pipeline, but seed the writer with the existing document as a baseline draft rather than starting from blank. Research checks whether the document's claims reflect current reality.

Mode is inferred or specified as normal. The review variant does not change the mode — it changes how the pipeline is entered.

---

## Your Role

You are the workflow manager. You launch sub-agents and confirm that each phase has produced non-empty output. You do not read reference files, research files, or drafts yourself. Pass file paths to sub-agents and let them read what they need.

## Workflow: Five Phases, Multiple Sub-Agents

**This workflow requires separate sub-agents for each phase. Do not combine them.**

Context growth degrades style adherence. Self-review is attachment-biased. Mode collapse (researching while writing, validating instead of critiquing) is the primary cause of poor output. Separate sub-agents with isolated contexts solve all three problems.

Set the mode path variable once and use it throughout:

```
MODE=<detected-mode>           # system-overview, readme, or generic
MODE_DIR=references/modes/$MODE   # does not exist for generic; see below
WORK_DIR=$(mktemp -d)
```

Pass `$WORK_DIR` and `$MODE_DIR` to all sub-agents so they read from consistent locations.

**For `generic` mode:** there is no pre-authored `references/modes/generic/` directory. Before beginning Phase 1, materialise the user's input into `$WORK_DIR/topics.md` and `$WORK_DIR/template.md`, then use `$WORK_DIR` as the source for these files in all subsequent phases. See the Generic Mode section below.

---

### Phase 1: Discovery

*(Skip this phase for the structural review variant — go directly to Phase 5.)*

Run a **single lightweight discovery agent**. Its job is to enumerate the project's components, integrations, and existing documentation so that researcher scopes can be assigned without gaps.

The discovery agent writes its output to `$WORK_DIR/discovery.md` with three sections:

- **Modules & Services** — all application modules, services, or major components. One line each, no descriptions.
- **External Systems** — all external systems referenced in config, code, or documentation. One line each, no descriptions.
- **Documentation & Specs** — any existing documentation files worth consulting: READMEs, OpenAPI/WSDL specs, architecture docs, wikis, significant configuration files. One line each with relative path.

**Read `$WORK_DIR/discovery.md`** and use it to define researcher scopes in Phase 2.

---

### Phase 2: Research

*(Skip this phase for the structural review variant — go directly to Phase 5.)*

Launch **multiple researcher sub-agents in parallel**, each scoped to a distinct topic from the mode's `topics.md`.

Each researcher:
- Follows `references/roles/researcher.md`
- Receives `$WORK_DIR/discovery.md` to orient themselves
- Receives the mode's `topics.md` to understand their scope
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

**generic:** derive scope assignments from the topics in `$WORK_DIR/topics.md`. Assign one researcher per topic; name output files after the topic.

Adapt scopes to the actual project using `$WORK_DIR/discovery.md`. For a small project, two or three researchers may suffice.

After all researchers complete, confirm each output file is non-empty using `wc -c` before proceeding.

---

### Phase 3: Outline

*(Skip this phase for the structural review variant — go directly to Phase 5.)*
*(Skip this phase for the accuracy review variant — use the provided document as the baseline draft and go to Phase 5.)*

Launch a **single outliner sub-agent** with:
- `references/roles/outliner.md`
- The mode's `template.md` (from `$MODE_DIR/template.md` or `$WORK_DIR/template.md` for generic)
- All Phase 2 output files from `$WORK_DIR/`

The outliner writes a document skeleton to `$WORK_DIR/outline.md`.

---

### Phase 4: Write

*(Skip this phase for both review variants.)*

Launch a **single writer sub-agent** with:
- `references/roles/writer.md`
- The mode's `template.md`
- `references/rules/style-guide.md`
- `$WORK_DIR/outline.md`
- All Phase 2 output files from `$WORK_DIR/`

Also pass if available for the mode:
- `examples.md` — pass if present (`$MODE_DIR/examples.md`); omit for generic unless the user provided one
- `references/rules/abstraction-rules.md` — pass for `system-overview` only

The writer fills in the outline section by section and writes the draft to `$WORK_DIR/draft.md`.

---

### Phase 5: Review

Launch a **single reviewer sub-agent** with:
- `references/roles/reviewer.md`
- `$WORK_DIR/draft.md` (or the existing document path for the structural review variant)

Also pass if available for the mode:
- `examples.md` — pass if present; omit for generic unless user provided one
- `checklist.md` — pass if present (`$MODE_DIR/checklist.md`); omit for generic unless user provided one
- `references/rules/abstraction-rules.md` — pass for `system-overview` only

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
| `generic` | path specified by user |

Use the path requested by the user if they specified one.

---

## Generic Mode

The `generic` mode has a pre-authored `template.md` and `checklist.md` in `references/modes/generic/`. There is no pre-authored `topics.md` — the user must supply the research topics, as they define what the document covers.

Before starting Phase 1:

1. **Extract research topics** from the user's description — what areas to investigate, what the document should cover. If the user has not provided topics, ask: "What areas should the researchers investigate?" before proceeding.

2. **Materialise** the topics as `$WORK_DIR/topics.md` in the same format as other `topics.md` files.

3. Proceed identically to any other mode from Phase 1 onward:
   - Use `$WORK_DIR/topics.md` as the researcher scope file
   - Use `references/modes/generic/template.md` as the document structure
   - Use `references/modes/generic/checklist.md` for the reviewer
   - No `examples.md` is provided unless the user supplies one

**If the user provides no topics, ask before proceeding.** Generic mode without research topics produces a worse outcome than a clarification question.

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
| `topics.md` | Yes | Researcher agents | Research scope definitions for this document type |
| `template.md` | Yes | Outliner + Writer | Section order and per-section content guidance |
| `examples.md` | No | Writer + Reviewer | Target voice; annotated correct examples |
| `checklist.md` | No | Reviewer | Structural invariants to verify |

For `generic` mode, `template.md` and `checklist.md` are pre-authored in `references/modes/generic/`. `topics.md` is materialised into `$WORK_DIR/` from the user's input at invocation time. `examples.md` is not provided unless the user supplies one.

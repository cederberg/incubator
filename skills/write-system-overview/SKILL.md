---
name: write-system-overview
description: Writes a concise system overview for a technically literate audience.
---

# write-system-overview

## What This Produces

A Markdown document with the following properties:
- Describes what the system does and how data flows through it
- Names external systems, data contracts, named concepts, and processing behavior
- Excludes class names, method names, configuration values, SQL schemas, and framework detail
- Written in present tense, third person, with no hedging and no justification prose
- Follows the structure: Introduction → Inbound Data → Outbound Data → Concepts → Processing → Other

See [references/examples.md](references/examples.md) for concrete examples of the target style.

## Workflow: Four Phases, Multiple Sub-Agents

**This workflow requires separate sub-agents for each phase. Do not combine them.**

Context growth degrades style adherence. Self-review is attachment-biased. Mode collapse (researching while writing, validating instead of critiquing) is the primary cause of poor output. Separate sub-agents with isolated contexts solve all three problems.

---

### Phase 0: Discovery

Before launching researchers, run a **single lightweight discovery agent**. Its only job is to enumerate the system's subsystems and major modules so that researcher scopes can be assigned without gaps.

The discovery agent should:
- List all application modules or services (e.g. API layer, worker, inbound processor, batch jobs)
- List the names of all external systems referenced in config, code, or comments
- Produce a short flat list — no descriptions, no detail

Use this manifest to define the researcher scopes in Phase 1. This prevents an entire subsystem from being silently skipped.

---

### Phase 1: Research

Create a shared temporary directory for research output:

```
mkdir -p /tmp/overview-research
```

Launch **multiple researcher sub-agents in parallel**, each scoped to a distinct topic. Typical scopes:

| Agent | Scope | Output file |
|---|---|---|
| Researcher A | Topology & actors — external systems, infrastructure components, data flow direction | `/tmp/overview-research/topology.md` |
| Researcher B | Data contracts — fields exchanged per actor (inbound/outbound), reliability notes | `/tmp/overview-research/contracts.md` |
| Researcher C | Processing logic — named steps, sequence, business rules, filter conditions, outcomes | `/tmp/overview-research/processing.md` |
| Researcher D | Vocabulary — named concepts: enums, status values, message types, event types, variants | `/tmp/overview-research/vocabulary.md` |

Adapt scopes to the actual system using the discovery manifest. For a small system, two researchers may suffice. For a large system, add more.

**Each researcher:**
- Reads the codebase (or designated source material)
- Follows instructions in [references/researcher.md](references/researcher.md)
- **Writes its full facts document to its assigned output file** — it does not return a summary
- Must NOT write documentation prose or make architectural judgments

After all researchers complete, read each output file from `/tmp/overview-research/` before proceeding to Phase 2.

---

### Phase 2: Write

Launch a **single writer sub-agent** with:
- All researcher fact documents from Phase 1 (read from `/tmp/overview-research/`)
- [references/writer.md](references/writer.md) — writer instructions
- [references/structure-template.md](references/structure-template.md) — document structure
- [references/style-guide.md](references/style-guide.md) — sentence and formatting rules
- [references/abstraction-rules.md](references/abstraction-rules.md) — what to include/exclude
- [references/examples.md](references/examples.md) — target voice and abstraction level

The writer produces a draft document and writes it to `/tmp/overview-research/draft.md`. It must not consult the codebase. Missing facts become `[MISSING: ...]` placeholders.

---

### Phase 3: Review

Launch a **single reviewer sub-agent** with:
- The draft document from `/tmp/overview-research/draft.md`
- [references/reviewer.md](references/reviewer.md) — reviewer instructions
- [references/abstraction-rules.md](references/abstraction-rules.md) — the rules to enforce
- [references/examples.md](references/examples.md) — the correct abstraction level

The reviewer produces a numbered list of specific issues: exact text quoted, rule violated, fix instruction. It must not rewrite the document. It must not praise.

---

### Iteration

If the review finds issues:
1. Launch a **new writer sub-agent** (fresh context) with the draft from `/tmp/overview-research/draft.md`, the numbered review output, and all Phase 2 inputs
2. Instruct it to address each numbered issue and write the updated draft back to `/tmp/overview-research/draft.md`
3. Launch a **new reviewer sub-agent** to check the updated draft

One review cycle is typically sufficient. If issues persist after two cycles, review the research documents — the root cause is usually a missing or incorrectly scoped research finding.

---

### Final Output

Once the review passes (or after two cycles), copy `/tmp/overview-research/draft.md` to the project root as `OVERVIEW.md` — or to the path explicitly requested by the user. Do not leave the final document in `/tmp/`.

---

## Abstraction Level: The Key Constraint

The most common failure mode is including implementation detail. The target reader is a technically literate non-developer: ops engineer, QA, compliance auditor, or new team member who did not write the code.

The five exclusion heuristics and verbosity failure modes are in [references/abstraction-rules.md](references/abstraction-rules.md). The writer and reviewer must both load this file.

The short version: document **what** the system does, not **how** it does it. If a sentence would only make sense to someone who has read the source code, it does not belong in the overview.

## Reference Files

| File | Used By | Purpose |
|---|---|---|
| [references/researcher.md](references/researcher.md) | Researcher agents | Output format and extraction rules |
| [references/writer.md](references/writer.md) | Writer agent | Writing instructions and input usage |
| [references/reviewer.md](references/reviewer.md) | Reviewer agent | Review posture and output format |
| [references/style-guide.md](references/style-guide.md) | Writer | Sentence rules, formatting, anti-patterns |
| [references/structure-template.md](references/structure-template.md) | Writer | Section order and per-section guidance |
| [references/abstraction-rules.md](references/abstraction-rules.md) | Writer + Reviewer | What to include/exclude; heuristics |
| [references/examples.md](references/examples.md) | Writer + Reviewer | Target voice; annotated correct examples |

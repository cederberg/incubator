# Plan: technical-writer Skill

## Problem

`write-system-overview` encodes a powerful pipeline: isolated-context sub-agents, parallel research, a write-review cycle with an adversarial reviewer. This pipeline is document-type-agnostic. Only four artifacts vary per document type: the research scopes, the document structure template, the voice-calibration examples, and the reviewer's structural checklist.

The goal is to generalise the skill into `technical-writer` with named modes, while preserving the quality properties of the original.

**Modes planned:**
- `system-overview` — the current skill, migrated
- `readme` — project-level README
- `utility-command` — a CLI tool, script, or make target
- `design-notes` — technical design or implementation notes for a process or feature

---

## Architecture

### What varies per mode

| Artifact | Role |
|---|---|
| `research-scopes.md` | What researchers look for; the discovery lens for this document type |
| `structure-template.md` | Section inventory, per-section content guidance, ordering rules |
| `examples.md` | Curated real examples with annotation of *why* they work; primary calibration for the writer and reviewer |
| `reviewer-checklist.md` | Structural invariants to verify: section ordering, required elements, disallowed patterns |

### What is shared

| Artifact | Directory | Notes |
|---|---|---|
| `researcher.md` | `roles/` | Format rules only (no hedging, `[NOT FOUND:]`, bullet-first, no prose). Remove the inline scope examples, which become mode-specific. |
| `outliner.md` | `roles/` | Entirely structural; no changes needed |
| `writer.md` | `roles/` | Remove the two system-overview-specific sentences (topology diagram rule, external-systems-in-intro rule). Otherwise unchanged. |
| `reviewer.md` | `roles/` | Retain posture section and per-sentence checklist. Extract structural checklist to mode-specific `reviewer-checklist.md`. |
| `style-guide.md` | `rules/` | Unchanged |
| `abstraction-rules.md` | `rules/` | Unchanged |

### Target directory layout

```
skills/technical-writer/
  SKILL.md
  references/
    roles/
      researcher.md
      outliner.md
      writer.md
      reviewer.md
    rules/
      style-guide.md
      abstraction-rules.md
    modes/
      system-overview/
        research-scopes.md
        structure-template.md
        examples.md
        reviewer-checklist.md
      readme/
        research-scopes.md
        structure-template.md
        examples.md
        reviewer-checklist.md
      utility-command/
        research-scopes.md
        structure-template.md
        examples.md
        reviewer-checklist.md
      design-notes/
        research-scopes.md
        structure-template.md
        examples.md
        reviewer-checklist.md
```

---

## Implementation Phases

---

### Phase 0: Example Research (interactive — must precede mode authoring)

**This phase is prerequisite to authoring `examples.md` for any new mode.**

The `examples.md` files are the most important calibration artifacts in the skill. They determine the writer agent's abstraction level and voice more than any rule document. Poor examples produce poor output regardless of how precise the other reference files are. This phase cannot be skipped or done from memory.

#### 0a. README examples

**Step 1 — Candidate collection**

Pull a candidate set of highly-regarded READMEs from open source. Good sources:
- Projects known for documentation quality: `curl`, `jq`, `ripgrep`, `bat`, `fd`, `httpie`, `exa`, `age`, `gh`, `sqlite`
- GitHub's own "awesome-readme" lists
- Ask the user: "Are there any READMEs you think of as excellent that we should include?"

Fetch 8–12 candidates and present them to the user as a shortlist.

**Step 2 — User selection (interactive)**

Present the shortlist with a one-sentence characterisation of each. Ask the user:
> "Which of these do you consider genuinely excellent? We want 3–5 that set the bar."

Do not proceed until the user has made selections. Their taste defines the target output quality.

**Step 3 — Structural analysis (per selected example)**

For each selected README, extract and document:
- Which sections are present, in what order
- What the opening sentence/paragraph does (orients, motivates, demonstrates?)
- How setup/usage is handled (steps, prose, code blocks?)
- What is conspicuously absent (no architecture diagrams? no "about" fluff? no badges beyond essentials?)
- Approximate word count per section

Record findings in a working doc (session workspace).

**Step 4 — Voice and abstraction analysis (per selected example)**

For each selected README, identify:
- Sentence style: imperative vs. declarative vs. mixed
- Assumed reader knowledge level
- What the author chose *not* to explain (and why that works)
- Any single sentence or passage that is particularly exemplary — quote it

**Step 5 — Why-it-works annotation**

For each selected README, write a 2–4 sentence "why this works" note. This becomes the annotation in `examples.md`. The annotation must explain the structural or stylistic choice, not just praise the writing.

Example annotation pattern (from current `examples.md`):
> "The criteria list states the *conditions* without explaining how they are evaluated. There is no mention of a database query, a timestamp comparison method, or an EventStatus enum."

**Step 6 — Draft `readme/examples.md`**

Assemble 3–4 curated excerpts with annotations. Present to user for sign-off before finalising.

#### 0b. utility-command examples

Same six-step process. Candidate sources:
- Man pages: `git commit`, `curl`, `ssh`, `rsync`, `awk`
- Modern CLI docs: `gh`, `docker`, `kubectl`, `terraform`
- Well-regarded scripts with embedded `--help` output

Key question for user selection: does the example doc feel like a reference (you consult it) or a tutorial (you read it once)? The target for this mode is reference-first.

#### 0c. design-notes examples

Same six-step process. Candidate sources:
- Published RFCs (RFC 793, RFC 7230 — known for conciseness)
- IETF best current practice documents
- Google's publicly available design doc examples
- Oxide Computer's RFDs (publicly available, high quality)
- Ask the user: "Do you have internal design docs you consider exemplary in style?"

Key question for user selection: does the example clearly separate "what we decided" from "why we decided it" from "what we considered and rejected"?

#### 0d. Cross-mode calibration check

After all three new example sets are drafted, review them together to confirm:
- The three modes are differentiated in voice (they should not read identically)
- The `system-overview` examples remain the highest-detail mode
- The `utility-command` examples are the most terse
- The `readme` and `design-notes` examples sit between them

---

### Phase 1: Scaffold the new skill directory

1. Create `skills/technical-writer/` directory
2. Create `references/shared/` and `references/modes/` subdirectories
3. Create the four mode subdirectories under `references/modes/`
4. Do not move or modify any existing files yet

---

### Phase 2: Migrate and refactor shared reference files

Work from `skills/write-system-overview/references/` into `skills/technical-writer/references/`.

**`rules/style-guide.md`** — copy unchanged

**`rules/abstraction-rules.md`** — copy unchanged

**`roles/outliner.md`** — copy unchanged

**`roles/researcher.md`** — copy, then edit:
- Remove the "Typical research scopes for a system overview" section (lines listing topology, contracts, processing, vocabulary)
- Replace with: "Your specific research scope and the topics to look for are defined in the `research-scopes.md` file provided to you alongside this document."
- Remove the output example section (it is system-overview-specific; each mode's `examples.md` provides calibration)

**`roles/writer.md`** — copy, then edit:
- Remove: "All external systems named in processing or data sections must appear in the post-diagram bullet list in the Introduction. Do not reference a system for the first time mid-document." (system-overview specific)
- The structure-template and examples references remain; the agent will receive the mode-specific versions

**`roles/reviewer.md`** — copy, then edit:
- Remove the entire "Structural checklist" block (the four checkboxes for section ordering, diagram rules, external systems, acronyms)
- Add after the per-section checklist: "You will also be given a `reviewer-checklist.md` file specific to this document type. Verify every item in that checklist explicitly."

---

### Phase 3: Migrate the system-overview mode

Copy from `skills/write-system-overview/references/` into `skills/technical-writer/references/modes/system-overview/`:

**`structure-template.md`** — copy unchanged

**`examples.md`** — copy unchanged

**`research-scopes.md`** — new file, authored from the content removed from `researcher.md`:
```
## Typical Research Scopes

- **Topology & actors** — external systems and infrastructure components, their roles, data flow direction
- **Data contracts** — fields exchanged per actor (inbound/outbound); field names, one-line descriptions; reliability notes
- **Processing logic** — named steps, sequence, business rules, filter conditions, outcome states
- **Vocabulary** — named concepts: enum values, status values, message types, event types, variant names
```

**`reviewer-checklist.md`** — new file, authored from the structural checklist removed from `reviewer.md`:
```
## Structural Checklist

Verify each item explicitly.

- [ ] Section order matches the template: Introduction → Inbound Data → Outbound Data → Concepts & Definitions → Status Lifecycles → [Process sections] → Other Processes
- [ ] Every external system named anywhere in the document is introduced in the post-diagram bullet list in the Introduction
- [ ] The topology diagram uses generic grouping labels for external actors rather than enumerating every system individually (max ~6 external nodes)
- [ ] No undefined acronyms or abbreviated system names
```

---

### Phase 4: Author the readme mode (after Phase 0b)

Using the structural and voice analysis from Phase 0, author four files:

**`research-scopes.md`**

Scopes for a README researcher:
- **Purpose & audience** — what the project does, for whom, and in what context it is used
- **Setup & prerequisites** — what a user needs before they can use it; installation steps
- **Usage** — primary commands, invocations, or API entry points; key options or parameters
- **Configuration** — named configuration options, their defaults, and their effects on behaviour
- **Contribution & support** — how to run tests, how to contribute, where to get help

**`structure-template.md`**

Sections (in order):
- **Name & one-liner** — project name and a single sentence stating what it does
- **Install** — the minimum steps to install; no prose, steps only
- **Usage** — the most common invocation(s) with output or effect; prefer concrete examples over descriptions
- **Configuration** — named options, defaults, and effects; omit if not applicable
- **Development** — how to build and test from source; omit if intended audience is users only
- **Contributing** — a single paragraph or link; not a full guide

Per-section guidance (mirroring `structure-template.md` format) to be developed from analysis.

**`examples.md`** — to be authored from Phase 0b output

**`reviewer-checklist.md`**

Structural invariants to verify:
- [ ] First sentence is a factual statement of what the project does, not a tagline or marketing phrase
- [ ] Install section contains only steps; no explanatory prose before the first step
- [ ] Every code block in Usage is self-contained and runnable as written
- [ ] No section explains *why* the project was built or its design philosophy
- [ ] No section is present that has no content relevant to the reader

---

### Phase 5: Author the utility-command mode (after Phase 0b)

**`research-scopes.md`**

Scopes:
- **Purpose & invocation** — what the command does; its canonical invocation syntax
- **Options & flags** — all named flags; their type, default, and effect on behaviour
- **Input & output** — what the command reads (stdin, files, arguments) and what it produces (stdout, files, exit status)
- **Exit codes** — named exit conditions and their numeric codes
- **Examples** — real invocations that illustrate non-obvious behaviour or common use cases

**`structure-template.md`**

Sections follow the traditional man page structure, adapted for Markdown:
- **Name** — `command — one-line description`
- **Synopsis** — the abstract invocation syntax; use `[optional]` and `<required>` conventions
- **Description** — two to four sentences of what the command does; no options, no examples
- **Options** — one entry per flag; bold flag name, type annotation, default, effect
- **Examples** — concrete invocations with output; ordered from simplest to most complex
- **Exit Codes** — table of exit code → meaning; omit if only 0/non-zero
- **Notes** — edge cases or environment dependencies that don't fit elsewhere; omit if none

**`examples.md`** — to be authored from Phase 0b output

**`reviewer-checklist.md`**

- [ ] Synopsis matches actual option list (no options in Synopsis that don't appear in Options)
- [ ] Every option in Options has a stated default or "required" annotation
- [ ] Every example is runnable as written (no `<placeholder>` left unexplained)
- [ ] Description contains no options and no examples
- [ ] No option is described in prose in the Description and then also listed in Options

---

### Phase 6: Author the design-notes mode (after Phase 0c)

**`research-scopes.md`**

Scopes:
- **Context & problem** — the situation that motivates the design; the specific problem being solved
- **Goals & non-goals** — what this design achieves and what it explicitly does not address
- **Design** — the chosen approach; the key decisions and their direct consequences
- **Alternatives considered** — other approaches evaluated; why each was not chosen
- **Open questions** — unresolved decisions; what would change the answer

**`structure-template.md`**

Sections:
- **Context** — background; one to three paragraphs stating the situation and what makes it a problem
- **Goals** — bulleted list of what this design achieves
- **Non-goals** — bulleted list of what this design explicitly does not address; must be present if scope is ambiguous
- **Design** — the chosen approach, described in terms of observable behaviour and consequences; one H3 per major decision
- **Alternatives Considered** — one H3 per alternative; one paragraph stating the approach and one sentence stating why it was not chosen
- **Open Questions** — bulleted list of unresolved decisions; each item states what additional information would resolve it; omit if none

**`examples.md`** — to be authored from Phase 0c output

**`reviewer-checklist.md`**

- [ ] Context section states a problem, not a solution
- [ ] Every item in Goals is a consequence of this design, not a general aspiration
- [ ] Non-goals section is present if any in-scope/out-of-scope boundary is non-obvious
- [ ] Alternatives Considered states *why each alternative was not chosen*, not just what it is
- [ ] Design section contains no implementation details that fail The 'How' Test
- [ ] No section contains justification prose for a decision that belongs in Alternatives Considered

---

### Phase 7: Rewrite SKILL.md

The orchestration logic changes in two ways:

1. **Mode detection** — the skill reads the user's requested mode (or infers it from the target artifact if the user does not specify) and loads the corresponding `modes/<mode>/` files throughout all phases.

2. **Reference file routing** — all phase instructions that currently name specific files (e.g. `references/structure-template.md`) must be updated to use the mode-specific path (e.g. `references/modes/<mode>/structure-template.md`).

The five-phase structure is otherwise unchanged. Update the Reference Files table at the bottom to reflect the new layout.

**Mode inference heuristic** (for cases where the user does not name a mode):
- "write a README" / "document this project" → `readme`
- "document this command" / "document this script" / "write a man page" → `utility-command`
- "write design notes" / "document this design" / "write an ADR" → `design-notes`
- "write a system overview" / "document this system" / default → `system-overview`

---

### Phase 8: Validation

1. Run the skill in `system-overview` mode on a known system (the original test case if available) and confirm output quality is unchanged
2. Run the skill in `readme` mode on a simple project with a weak or missing README; verify output structure and voice match the calibrated examples
3. Run the skill in `utility-command` mode on a script or CLI tool in the repo
4. Run the skill in `design-notes` mode with a description of a design decision; verify the output matches the expected structure
5. For each run: confirm the reviewer's structural checklist items are being evaluated (check reviewer output for explicit checklist language)

---

## Sequencing Summary

```
Phase 0a  ──┐
Phase 0b  ──┤── all interactive, can be done in any order across sessions
Phase 0c  ──┤
Phase 0d  ──┘
              │
Phase 1 ──────┤── structural setup (no content yet; can be done any time)
              │
Phase 2 ──────┤── shared reference refactoring (depends on Phase 1)
              │
Phase 3 ───── ┤── system-overview migration (depends on Phase 2; no new content needed)
              │
Phase 4 ──────┤── readme mode (depends on Phase 2 + Phase 0a/0b)
Phase 5 ──────┤── utility-command mode (depends on Phase 2 + Phase 0b)
Phase 6 ──────┤── design-notes mode (depends on Phase 2 + Phase 0c)
              │
Phase 7 ──────┤── SKILL.md rewrite (depends on Phases 3–6)
              │
Phase 8 ──────┘── validation
```

Phases 4, 5, and 6 can be worked in parallel once Phase 0 and Phase 2 are complete.

---

## Key Risks

**Example quality is the primary risk.** The `examples.md` files are not decoration — they are the primary calibration mechanism for the writer agent. If the examples are generic or mediocre, the output will be generic and mediocre regardless of how precise the other reference files are. Phase 0 must not be rushed.

**Mode inference must fail loudly.** If the skill cannot determine the mode, it must ask the user rather than defaulting silently. A README written with `system-overview` structure, or a system overview written with `readme` brevity, is a worse outcome than a clarification question.

**The system-overview mode must not regress.** Migrating to the new structure must produce output indistinguishable from the current skill. Phase 8 step 1 is a regression check, not just a smoke test.

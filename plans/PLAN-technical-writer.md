# Plan: technical-writer Skill

## Problem

`write-system-overview` encodes a powerful pipeline: isolated-context sub-agents, parallel research, a write-review cycle with an adversarial reviewer. This pipeline is document-type-agnostic. Only four artifacts vary per document type: the research scopes, the document structure template, the voice-calibration examples, and the reviewer's structural checklist.

The goal is to generalise the skill into `technical-writer` with named modes, while preserving the quality properties of the original.

**Modes planned:**
- `system-overview` — the current skill, migrated
- `readme` — project-level README
- `generic` — user-supplied topics and template; no pre-authored mode files

---

## Architecture

### What varies per mode

| Artifact | Role | Required |
|---|---|---|
| `topics.md` | What researchers look for; the discovery lens for this document type | Yes |
| `template.md` | Section inventory, per-section content guidance, ordering rules | Yes |
| `examples.md` | Curated real examples with annotation of *why* they work; primary calibration for the writer and reviewer | No — writer falls back to template + style guide alone if absent |
| `checklist.md` | Structural invariants to verify: section ordering, required elements, disallowed patterns | No — reviewer uses only shared per-sentence checklist if absent |

For `system-overview` and `readme`, all four files are pre-authored and live in `references/modes/<mode>/`. For `generic`, the user supplies `topics.md` and `template.md` content at invocation time; `examples.md` and `checklist.md` are optional and may not be provided.

### What is shared

"Shared" means the file lives in one place and is available to all modes. It does not mean every mode loads every shared file. SKILL.md controls which shared files are passed to each agent per mode; modes that don't need a file simply don't receive it.

| Artifact | Directory | Notes |
|---|---|---|
| `researcher.md` | `roles/` | Format rules only (no hedging, `[NOT FOUND:]`, bullet-first, no prose). Remove the inline scope examples, which become mode-specific. |
| `outliner.md` | `roles/` | Entirely structural; no changes needed |
| `writer.md` | `roles/` | Remove the two system-overview-specific sentences (topology diagram rule, external-systems-in-intro rule). Otherwise unchanged. |
| `reviewer.md` | `roles/` | Retain posture section and per-sentence checklist. Extract structural checklist to mode-specific `checklist.md`. |
| `style-guide.md` | `rules/` | Unchanged |
| `abstraction-rules.md` | `rules/` | Applies to `system-overview` only. The readme mode's core failure modes are scope and audience errors, not abstraction errors — a different rules file is needed for that mode. |

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
        topics.md
        template.md
        examples.md
        checklist.md
      readme/
        topics.md
        template.md
        examples.md
        checklist.md
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

---

#### Phase 0a findings (completed)

Steps 1–2 are complete. Four examples were selected from a shortlist of ten candidates.

**Selected examples:**

| | Project | URL | Strengths | Gaps |
|--|---------|-----|-----------|------|
| ✅ | **age** | https://github.com/FiloSottile/age/blob/main/README.md | Clean structure, good demo | No license or build sections; too many emojis |
| ✅ | **restic** | https://github.com/restic/restic/blob/master/README.md | Demo, design principles, license, docs links | 3 badges + sponsor logo |
| ✅ | **watchexec** | https://github.com/watchexec/watchexec/blob/main/README.md | Only 2 badges; demo, docs links | No license section; 1 inline image (repology) |
| ✅ | **direnv** | https://github.com/direnv/direnv/blob/master/README.md | Demo, how-it-works explanation, license, docs links | 4 badges |

**Rejected candidates and why:**

- `ripgrep`, `bat`, `fd`, `httpie` — too long; badge walls; irrelevant per-distro install tables; inlined images
- `gh` — marketing-heavy
- `sqlite` — not a CLI-tool README pattern
- `curl` — no markdown structure; too terse
- `tmux` — plain text, not markdown; no demo
- `git` — no demo; almost no structure
- `jq` — no demo (nearly selected; good structure and linking)
- `syncthing` — no intro or install demo
- `nnn`, `miller`, `zstd` — excessive badges, HTML, embedded images
- `mosh` — no license; no demo
- `just` — 40+ per-package-manager install entries; too long
- `tig` — AsciiDoc; no demo; no license
- `caddy` — no embedded demo; no license section; multiple badges and a logo

**User guidance (distilled from the selection session):**

These preferences must inform the `template.md`, `examples.md`, and `checklist.md` for the readme mode.

*Format:*
- Markdown preferred, plain text acceptable (if structured)
- Structure with headings, lists, tables and code blocks is important for readability
- Avoid embedded HTML, max 1 embedded image, no badge walls

*Badges:*
- Acceptable in small numbers (2–4 at the top); more than ~4 is too many

*Images:*
- A project logo at the very top is marginal; do not treat it as a model behaviour
- A single screenshot or interactive demo image is ok it well executed
- Otherwise images, videos, or third-party badges (e.g. repology) don't belong in the README

*Required content:*
- Brief intro that states what the project does (factual, not a tagline)
- Quick-start demo with real commands and real or representative output
- Link(s) to full documentation
- Install instructions (minimal or compact table if many variants exist)
- License

*Prohibited content:*
- Long-winding install instructions (should be brief and navigable)
- Origin story or "why we built this" sections
- Design philosophy sections (unless brief and directly useful to a user)
- Overload of emojis
- Contributor lists, sponsor sections, or social proof elements
- Any section with no content relevant to a user

*Scope and length:*
- Primarily targeted at users, not contributors
- Not a single-page documentation site — depth belongs in linked external docs
- A short contributing paragraph or link is acceptable; a full contributing guide is not

---

#### 0b. Cross-mode calibration check

After both example sets are drafted, review them together to confirm:
- The two modes are differentiated in voice (they should not read identically)
- The `system-overview` examples are the higher-detail mode
- The `readme` examples are the more concise mode

---

### Phase 1: Scaffold the new skill directory

1. Create `skills/technical-writer/` directory
2. Create `references/shared/` and `references/modes/` subdirectories
3. Create the two mode subdirectories under `references/modes/`
4. Do not move or modify any existing files yet

---

### Phase 2: Migrate and refactor shared reference files

Work from `skills/write-system-overview/references/` into `skills/technical-writer/references/`.

**`rules/style-guide.md`** — copy unchanged

**`rules/abstraction-rules.md`** — copy unchanged

**`roles/outliner.md`** — copy unchanged

**`roles/researcher.md`** — copy, then edit:
- Remove the "Typical research scopes for a system overview" section (lines listing topology, contracts, processing, vocabulary)
- Replace with: "Your specific research topics are defined in the `topics.md` file provided to you alongside this document."
- Remove the output example section (it is system-overview-specific; each mode's `examples.md` provides calibration)

**`roles/writer.md`** — copy, then edit:
- Remove: "All external systems named in processing or data sections must appear in the post-diagram bullet list in the Introduction. Do not reference a system for the first time mid-document." (system-overview specific)
- The template and examples references remain; the agent will receive the mode-specific versions
- Add a note that `examples.md` may not be present; when absent, the writer uses the template and style guide as the sole calibration

**`roles/reviewer.md`** — copy, then edit:
- Remove the entire "Structural checklist" block (the four checkboxes for section ordering, diagram rules, external systems, acronyms)
- Add after the per-section checklist: "You will also be given a `checklist.md` file specific to this document type. Verify every item in that checklist explicitly."

---

### Phase 3: Migrate the system-overview mode

Copy from `skills/write-system-overview/references/` into `skills/technical-writer/references/modes/system-overview/`:

**`template.md`** — copy existing `structure-template.md` unchanged

**`examples.md`** — copy unchanged

**`topics.md`** — new file, authored from the content removed from `researcher.md`:
```
## Research Topics

- **Topology & actors** — external systems and infrastructure components, their roles, data flow direction
- **Data contracts** — fields exchanged per actor (inbound/outbound); field names, one-line descriptions; reliability notes
- **Processing logic** — named steps, sequence, business rules, filter conditions, outcome states
- **Vocabulary** — named concepts: enum values, status values, message types, event types, variant names
```

**`checklist.md`** — new file, authored from the structural checklist removed from `reviewer.md`:
```
## Structural Checklist

Verify each item explicitly.

- [ ] Section order matches the template: Introduction → Inbound Data → Outbound Data → Concepts & Definitions → Status Lifecycles → [Process sections] → Other Processes
- [ ] Every external system named anywhere in the document is introduced in the post-diagram bullet list in the Introduction
- [ ] The topology diagram uses generic grouping labels for external actors rather than enumerating every system individually (max ~6 external nodes)
- [ ] No undefined acronyms or abbreviated system names
```

---

### Phase 4: Author the readme mode (after Phase 0a)

Using the structural and voice analysis from Phase 0, author four files:

**`topics.md`**

Topics for a README researcher:
- **Purpose & audience** — what the project does, for whom, and in what context it is used
- **Setup & prerequisites** — what a user needs before they can use it; installation steps
- **Usage** — primary commands, invocations, or API entry points; key options or parameters
- **Configuration** — named configuration options, their defaults, and their effects on behaviour
- **Contribution & support** — how to run tests, how to contribute, where to get help

**`template.md`**

Sections (in order):
- **Name & one-liner** — project name and a single sentence stating what it does
- **Install** — the minimum steps to install; no prose, steps only
- **Usage** — the most common invocation(s) with output or effect; prefer concrete examples over descriptions
- **Configuration** — named options, defaults, and effects; omit if not applicable
- **Development** — how to build and test from source; omit if intended audience is users only
- **Contributing** — a single paragraph or link; not a full guide

Per-section guidance (mirroring `template.md` format) to be developed from analysis.

**`examples.md`** — to be authored from Phase 0a output

**`checklist.md`**

Structural invariants to verify:
- [ ] First sentence is a factual statement of what the project does, not a tagline or marketing phrase
- [ ] Install section contains only steps; no explanatory prose before the first step
- [ ] Every code block in Usage is self-contained and runnable as written
- [ ] No section explains *why* the project was built or its design philosophy
- [ ] No section is present that has no content relevant to the reader

---

### Phase 5: Rewrite SKILL.md

The orchestration logic changes in two ways:

1. **Mode detection** — the skill reads the user's requested mode (or infers it from the target artifact if the user does not specify) and loads the corresponding `modes/<mode>/` files throughout all phases.

2. **Reference file routing** — all phase instructions that currently name specific files (e.g. `references/template.md`) must be updated to use the mode-specific path (e.g. `references/modes/<mode>/template.md`).

The five-phase structure is otherwise unchanged. Update the Reference Files table at the bottom to reflect the new layout.

**Mode inference heuristic** (for cases where the user does not name a mode):
- "write a README" / "document this project" → `readme`
- "write a system overview" / "document this system" / default → `system-overview`
- User explicitly names `generic`, or provides their own topics/template structure → `generic`

**Review variant:**

When the user provides an existing document to review, SKILL.md must ask (or accept as an explicit flag): structural check or accuracy check?

- **Structural** — skip research and outline; run the reviewer agent directly on the existing document using the mode's `checklist.md` and shared style rules. No codebase access required.
- **Accuracy** — run the full pipeline, but seed the writer with the existing document as a baseline draft rather than starting from blank. Research checks whether the document's claims reflect current reality.

Mode is inferred or specified as normal. The review variant does not introduce a new mode.

---

**Generic mode invocation contract:**

The `generic` mode has no pre-authored files in `references/modes/`. Instead, SKILL.md must instruct the skill to:

1. Extract or request the research topics from the user's description — what areas to investigate, what the document should cover
2. Extract or request the document structure — section names, ordering, and per-section guidance
3. Materialise these as the researcher's `topics.md` and the writer's `template.md` inputs for that run
4. Proceed identically to any other mode from that point

If the user provides neither topics nor structure, the skill must ask before proceeding — generic mode without these inputs produces a worse outcome than a clarification question.

---

### Phase 6: Validation

1. Run the skill in `system-overview` mode on a known system (the original test case if available) and confirm output quality is unchanged
2. Run the skill in `readme` mode on a simple project with a weak or missing README; verify output structure and voice match the calibrated examples
3. Run the skill in `generic` mode with an ad-hoc topic description and document structure; verify the pipeline runs correctly without pre-authored mode files
4. For each run: confirm the reviewer's structural checklist items are being evaluated (check reviewer output for explicit checklist language)

---

## Sequencing Summary

```
Phase 0a  ──┐── interactive, can be done in any order across sessions
Phase 0b  ──┘
              │
Phase 1 ──────┤── structural setup (no content yet; can be done any time)
              │
Phase 2 ──────┤── shared reference refactoring (depends on Phase 1)
              │
Phase 3 ──────┤── system-overview migration (depends on Phase 2; no new content needed)
              │
Phase 4 ──────┤── readme mode (depends on Phase 2 + Phase 0a)
              │
Phase 5 ──────┤── SKILL.md rewrite (depends on Phases 3–4)
              │
Phase 6 ──────┘── validation
```

---

## Key Risks

**Example quality is the primary risk.** The `examples.md` files are not decoration — they are the primary calibration mechanism for the writer agent. If the examples are generic or mediocre, the output will be generic and mediocre regardless of how precise the other reference files are. Phase 0 must not be rushed.

**Mode inference must fail loudly.** If the skill cannot determine the mode, it must ask the user rather than defaulting silently. A README written with `system-overview` structure, or a system overview written with `readme` brevity, is a worse outcome than a clarification question. `generic` must never be inferred silently — it is only used when the user explicitly requests it or provides their own structure.

**The system-overview mode must not regress.** Migrating to the new structure must produce output indistinguishable from the current skill. Phase 6 step 1 is a regression check, not just a smoke test.

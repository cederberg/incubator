# Plan: Skill-writer Template and SKILL.md Restructure

## Context

The `skill-writer` mode template and the technical-writer `SKILL.md` over-commit to a modes-centric view of skill design. Every skill is framed as either "single-mode" or "multi-mode", and Modes + Mode Detection appear before Activation — inverting the natural reading order. Mode-specific orchestration logic is inlined into SKILL.md rather than living in mode-specific files.

The goals:
1. Merge Modes + Mode Detection into Activation (Example 3 in `examples.md` demonstrates the target pattern)
2. Reorder sections: H1 → Activation → Preconditions → *(other)* → Workflow → Output → Reference Files
3. Mark most sections as optional
4. Move mode-specific Phase 1 overrides out of SKILL.md into per-mode `survey.md` files
5. Remove the "Skill-writer Mode" and "Generic Mode" inline sections from SKILL.md
6. Restructure the SKILL.md body to conform to the new template
7. Update the SKILL.md frontmatter
8. Update the checklist to reflect the new structure

All inline text and code blocks marked **SUGGESTION** are starting points only. The implementing agent must review them, apply the style guide, and improve them freely.

---

## Key Files

Read these before starting:

| File | Purpose |
|---|---|
| `skills/technical-writer/SKILL.md` | Orchestrator skill — primary target |
| `skills/technical-writer/references/modes/skill-writer/template.md` | Skill file structure template — primary target |
| `skills/technical-writer/references/modes/skill-writer/checklist.md` | Structural checklist — needs updating |
| `skills/technical-writer/references/modes/skill-writer/topics.md` | Current researcher topics — will be replaced by `discover.md` |
| `skills/technical-writer/references/modes/skill-writer/examples.md` | Read-only: Example 3 (Activation-as-modes-table) and Example 4 (decision tree) define the target patterns |
| `skills/technical-writer/references/modes/generic/topics.md` | Current researcher topics — will be replaced by `discover.md` |
| `skills/technical-writer/references/modes/system-overview/topics.md` | Current researcher topics — will be replaced by `discover.md` |
| `skills/technical-writer/references/modes/readme/topics.md` | Current researcher topics — will be replaced by `discover.md` |
| `skills/technical-writer/references/rules/style-guide.md` | All prose must conform to this |

---

## File Changes

### 1. `references/modes/skill-writer/template.md`

Remove the separate Modes and Mode Detection sections. Replace "Activation (for single-mode skills)" with a unified Activation section covering all three patterns: prose trigger, modes table with inline inference rules and labelled default, and decision tree. Reference Examples 3 and 4 from `examples.md` to illustrate the latter two.

Updated section order — mark each as required or optional:

1. Frontmatter (required)
2. Skill Name / H1 (required)
3. Activation (required)
4. Preconditions (optional)
5. *(other sections as needed)*
6. Workflow (required)
7. Output (required)
8. Reference Files (optional)

Rewrite the Section Selection guidance to remove all binary framing. Key points to convey:
- Activation is required in every skill; its form depends on branching needs
- A Modes table may appear inside Activation or immediately after — both are valid
- Preconditions: only when a violated guard causes incorrect output or requires mid-run intervention
- Reference Files: only when sub-files exist

---

### 2. `references/modes/*/discover.md` (RENAME + EXTEND)

Rename all four `topics.md` files to `discover.md`. Each `discover.md` serves both Phase 1 and Phase 2 — the orchestrator reads it once and uses the relevant section in each phase.

Structure of `discover.md`:

- **Phase 1: Discovery** — instructions for the discovery agent. For system-overview and readme this section may be absent or minimal ("use default discovery instructions"). For skill-writer it overrides Phase 1 entirely (survey a skill's task domain, not a codebase). For generic it holds the pre-flight logic (extract/ask for topics, materialise into `$WORK_DIR/topics.md`).
- **Phase 2: Research topics** — the existing researcher assignment table, unchanged from current `topics.md`.

Update SKILL.md to read `$MODE_DIR/discover.md` once per run, passing the Phase 1 section to the discovery agent and the Phase 2 section to the researcher spawning logic.

---

### 3. `SKILL.md`

**Frontmatter.** Remove the `synonyms` field — it is not recognised by any agent runtime and has no effect. Rewrite `description` to include concrete trigger phrases and at least one non-trigger condition. Keep it short; mode detail belongs in Activation, not the description. The description should also indicate that the skill asks the user before proceeding when intent is unclear.

**SUGGESTION** (review and improve):
> Use when the user wants to write or review a technical document or skill file. Triggers include: "write a README", "document this system", "write a skill", "review this skill". If the intent is clear, proceed; otherwise ask the user before starting. Do NOT trigger for general writing help or ad-hoc editing.

**Phase 1: Discovery.** Add a mode-awareness check: if `$MODE_DIR/survey.md` exists, pass it to the discovery agent in place of the default instructions. Default instructions remain unchanged.

**Body restructure.** Collapse `## Modes`, `## Mode Detection`, and `## Review Variant` into a single `## Activation` section. The Review Variant describes how the skill is entered — it belongs alongside mode detection in Activation. New body order:

> Activation → Your Role → Workflow (phases 1–5 + Final Output) → *skill-writer pre-flight note* → Reference Files

**Remove "Skill-writer Mode" section.** Replace with a brief pre-flight note (confirm skill name and target directory with the user if not provided). The Phase 1 override moves to `survey.md`; the review variant parameters are already covered inside the new Activation section.

**Remove "Generic Mode" section.** Its pre-flight logic moves to the Phase 1 section of `references/modes/generic/discover.md`.

---

### 4. `references/modes/skill-writer/checklist.md`

Update the Structure section to reflect the Activation-unified order. Replace the existing section-order item with checks that cover:
- Activation section is present
- If a Modes table is present: it includes a labelled default and inference rules
- Any catch-all or generic mode is guarded against silent inference
- Preconditions, if present, appears after Activation and before Workflow
- Your Role, if present, appears before Workflow
- Reference Files, if present, appears after Output

Remove the "Activation and Modes" check group. Merge any surviving items into the updated Structure section or drop where already covered.

---

## Execution Order

1. Rename all four `topics.md` files to `discover.md` and add Phase 1 sections (skill-writer and generic need substantive content; system-overview and readme can note "use default discovery")
2. Edit `references/modes/skill-writer/template.md`
3. Edit `references/modes/skill-writer/checklist.md`
4. Edit `SKILL.md` — all changes in §3 (frontmatter, Phase 1 now reads `discover.md`, body restructure, section removals)

---

## Style Constraint

All prose written or edited across every file must conform to `skills/technical-writer/references/rules/style-guide.md`. Before finalising any section: present tense, active voice, no hedging, no justification prose, sentences under ~20 words, noun-phrase headings.

---

## Review Pass

After all edits, run one reviewer sub-agent per file, sequentially. For each, provide `references/roles/reviewer.md` and `references/rules/style-guide.md`. For `SKILL.md` also provide `references/modes/skill-writer/checklist.md`.

Files to review, in order:
1. `references/modes/skill-writer/discover.md`
2. `references/modes/generic/discover.md`
3. `references/modes/system-overview/discover.md`
4. `references/modes/readme/discover.md`
5. `references/modes/skill-writer/template.md`
6. `references/modes/skill-writer/checklist.md`
7. `SKILL.md`

Label each sub-agent **"review instructions"**. Fix only where the fix clearly improves the skill. One review-and-fix pass per file; no loops.

---

## Verification

- `SKILL.md`: no inline mode sections remain except the skill-writer pre-flight note; Modes/Mode Detection/Review Variant are inside a single Activation section; frontmatter has no `synonyms` field; Phase 1 reads `$MODE_DIR/discover.md`; Phase 2 reads the researcher topics section of the same file
- `template.md`: Activation appears before Workflow; no separate Modes or Mode Detection sections; Section Selection contains no binary framing
- `checklist.md`: Structure section reflects the Activation-unified order
- All four `topics.md` files are gone; each mode directory contains a `discover.md` with Phase 1 and Phase 2 sections

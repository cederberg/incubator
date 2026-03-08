# realign — Reformat existing AGENTS.md to canonical form

Rewrites an existing AGENTS.md (or CLAUDE.md) into the canonical format defined in SKILL.md,
pruning stale or superfluous content in the process.

Use `references/example-agents.md` as a concrete example of a well-formed output.

---

## Phase 1 — Read current file

Read the existing AGENTS.md (or CLAUDE.md). Note:
- Which sections are present and their structure
- Content that looks stale (references to removed files, outdated constraints, etc.)
- Content duplicated from README or other referenced docs
- Inline commands that belong in the build tool instead
- Sections that don't map to the canonical format

---

## Phase 2 — Verify (optional)

If the user requested verification, run research Phase 1 (analysis only, no write):
- Check that referenced files still exist
- Check that documented constraints still hold (e.g. build flags, dep restrictions)
- Note any gaps — facts visible in the current codebase that are missing from AGENTS.md

Skip this phase if the user did not request it.

---

## Phase 3 — Rewrite

Using the canonical AGENTS.md format defined in SKILL.md:

1. Write tagline — ≤12 words; preserve if still accurate, rewrite if stale
2. Write References — only files that actually exist; ≤5 words after the dash
3. Write Goals & Ethos — preserve real goals; drop anything now obvious or outdated
4. Write Code Style — keep concrete, specific rules; drop vague or redundant items
5. Write Constraints — keep hard constraints that are still enforced; drop lifted ones
6. Write Design Notes — keep non-obvious architectural facts; drop anything now in README
7. Add any gaps found in Phase 2 (if verification was run)
8. Omit any section with nothing meaningful to say

**Verification before saving:**
- Every referenced file actually exists in the repo
- No commands listed inline (build tool owns commands)
- No content duplicated from README
- Sections omitted if empty

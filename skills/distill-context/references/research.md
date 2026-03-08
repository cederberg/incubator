# research — Analyze codebase and produce AGENTS.md

Read files in order. Do not skip; each informs the next.

Use `references/example-agents.md` as a concrete example of a well-formed output.

---

## Phase 1 — Analyze (fully automated)

| Step | What to read | What to extract |
|------|-------------|-----------------|
| 1 | Project root listing | Docs, config, tooling, CI files present — note CI platform (GitHub Actions, etc.) |
| 2 | `Makefile`, `justfile` or equivalent | Check if present and if default target lists targets; note absence |
| 3 | Dependency manifest (`go.mod` / `package.json` / `pyproject.toml`) | Language, dep count, external deps |
| 4 | `README.md`, `*.md`, `*.txt` | Project purpose, architecture, pipeline |
| 5 | ~5 representative source files | Style signals (see below) |
| 6 | Test files (if any) | Framework, location, patterns |

**Style signals to infer from source:**

| Signal | Look for |
|--------|----------|
| Name style | Terse/abbreviated vs. descriptive identifiers |
| Comment density | None / sparse / heavy |
| Error handling | Every error handled vs. relaxed |
| Patterns | OO, functional, procedural, etc. |
| Dependencies | Minimal (few imports) vs. liberal |

---

## Phase 2 — Confirm (one prompt)

Show inferred values; ask only for intent/constraints not visible in code.

> "Based on the code:
> - Style: [terse / verbose]
> - Error handling: [rigorous / relaxed]
> - Dependencies: [minimal / liberal]
> - Constraints I can infer: [list]
>
> Anything to correct or add — goals, constraints not yet in the code?
> (Press Enter to accept and continue)"

---

## Phase 3 — Write AGENTS.md

Using the AGENTS.md format defined in SKILL.md, and the analysis + any user input:

1. Write project tagline — ≤12 words; what it does and why/how
2. Write References — README, build tool, CI config, and important docs found; each entry ≤5 words after the dash; pointer principle
3. Write Goals & Ethos — from README purpose + inferred design philosophy
4. Write Code Style — from style signals; be specific and concrete
5. Write Constraints — hard no's inferred from build flags, dependency manifest, source patterns
6. Write Design Notes — pipeline, architecture, non-obvious facts from README + source
7. Omit any section with nothing meaningful to say

**Verification before saving:**
- Every referenced file actually exists in the repo
- No commands listed inline (build tool owns commands)
- No content duplicated from README
- Sections omitted if empty

If this agent is known to not read `AGENTS.md` by default, and a native
file like `CLAUDE.md` is known, create a symlink to `AGENTS.md`.

---

## Phase 4 — Bootstrap Makefile (if absent)

If no `Makefile` or `justfile` was found in Phase 1:

1. Copy `references/example-makefile` to `Makefile` in the project root
2. Fill in reasonable build and test targets based on what Phase 1 revealed:
   - Language/toolchain (e.g. `go build`, `npm run build`, `cargo build`)
   - Test framework (e.g. `go test ./...`, `npm test`, `pytest`)
   - Any lint or format tools visible in CI config or dev dependencies
3. Update target comments to match the actual commands added
4. Leave targets empty rather than guessing if the right command is unclear

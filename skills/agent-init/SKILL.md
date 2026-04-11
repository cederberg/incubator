---
name: agent-init
description: >
    Analyze a project and produce AGENTS.md and Makefile.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Bash
---
## Goal

Your job is to research the project and produce `AGENTS.md` and `Makefile`. The
goal is to encode project-wide concepts, constraints and workflow along with
consistent build commands. This provides agents with stable, coherent and
documented tools.

Read `references/example-agents.md` and `references/example-makefile` as models
for tone, density, and structure.


## File Resolution

`AGENTS.md` is the canonical filename used in this instruction. Use the first
match found:

| File | Agent |
|------|-------|
| `AGENTS.md` | Preferred — agent-neutral |
| `CLAUDE.md` | Claude Code |
| `GEMINI.md` | Gemini CLI |
| <other-file> | [Your agent harness default] |

If the file exists, read it first, then overwrite; otherwise create `AGENTS.md`.
Condense verbose entries; reorganize into Step 3 structure; discard facts the
code contradicts. If your agent harness ignores `AGENTS.md`, also symlink its
expected filename to `AGENTS.md`.


## Step 1: Analyze

Read in order.

| # | Read                            | Extract                                       |
|---|---------------------------------|-----------------------------------------------|
| 1 | Project root listing            | Docs, config, tooling, CI files               |
| 2 | `Makefile` or `justfile`        | Build targets, default action                 |
| 3 | `.gitignore`                    | Possible build output dirs                    |
| 4 | Toolchain configs               | Tools, build/test/outdated commands, key deps |
| 5 | CI/CD configs                   | Authoritative build/test/deploy pipeline      |
| 6 | `README.md` and other docs      | Purpose, architecture, pipeline               |
| 7 | Linter/formatter configs        | Enforced code style rules                     |
| 8 | ~5 representative source files  | Style signals (below)                         |
| 9 | Test files                      | Framework, location, patterns                 |

**Style signals:**

| Signal         | Look for                          |
|----------------|-----------------------------------|
| Naming         | Terse/abbreviated vs. descriptive |
| Comments       | None / sparse / heavy             |
| Error handling | Rigorous vs. relaxed              |
| Patterns       | OO, functional, procedural        |
| Dependencies   | Minimal vs. liberal               |


## Step 2: Confirm

Present findings. Prioritize CI/CD commands as authoritative. Use wrapper
scripts (`./mvnw`, `./gradlew`) over direct tool invocation. Use the
toolchain's clean command, or fall back to `rm -rf [build output dirs]`.

> The project analysis results:
> - Style: [terse / verbose]
> - Error handling: [rigorous / relaxed]
> - Dependencies: [minimal / liberal]
> - Inferred constraints: [list]
> - Toolchain: [name]
>   - `clean`: [cmd]
>   - `build`: [cmd]
>   - `test`: [cmd]
>   - `outdated`: [cmd or ?]
>
> Write any corrections below, or press Enter to accept.

Apply corrections before proceeding to Step 3.


## Step 3: Write AGENTS.md

**Rules:**
- First line: tagline — ≤12 words, what it does and why/how
- Use whatever H2 sections the project warrants
- One fact per bullet; max 15 words
- Use file references; do not reproduce their content
- Add rules requiring updates to README and other docs when code changes
- Include command reference for build targets when inferred
- Use per-filetype sections to limit rule scope (e.g. `## Go Guidelines`,
  `## Shell Script Guidelines`)

**Checklist:**
- Every referenced file exists in the repo
- No content duplicated from README
- No empty sections


## Step 4: Create Makefile

Skip this step if `Makefile` or `justfile` already exists.

1. Copy `references/example-makefile` to `Makefile` in the project root
2. Replace `clean`, `build`, `test`, and `outdated` targets with confirmed
   commands
3. Leave unknown target bodies empty
4. Targets with a comment are listed by `make all` (auto-generated help).
   Exclude comments for intermediary targets.

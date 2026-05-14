---
name: bump-deps
description: Update each outdated dependency in a separate, minimal commit.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Bash
---

## Goal

Update each outdated dependency in a separate commit. Enables clean rollback of
individual updates when issues surface later.

## Step 1: Outdated Packages

Run `make outdated`. If missing:

1. Read Makefile `all` or `help` target
2. Read `AGENTS.md`, `CLAUDE.md`, or project README
3. Ask the user

Stop if no documented `outdated` target found.

Do all minor/patch bumps first, then majors. When a major appears, flag it to
the user and defer it. Return to majors only after all minors are done.

## Step 2: Identify Dependency File

Inspect `make outdated` output or the Makefile. Common names: `pom.xml`,
`package.json`, `Cargo.toml`, `requirements.txt`, `Gemfile`.

## Step 3: Edit

Update the version string in the dependency file. Use the version resolved by
`make outdated` (npm "Wanted" column, Maven right-hand version). Do not bump to
"Latest" on major versions without user approval.

## Step 4: Build, Lint & Test

Run the project's build, lint, and test commands. Check in order:

1. `make build test` or equivalent Makefile targets
2. Instructions in `AGENTS.md` or `CLAUDE.md`
3. Ask the user

## Step 5: Find Commit Message Convention

```bash
git log <file> | grep -i <dependency-name>
```

If empty, widen the search:

```bash
git log --all --diff-filter=M -- <file> | head -20
git log --all -p -- <file> | grep -B5 -i <dependency-name> | grep "^commit"
```

Commit messages follow project convention. Common patterns:

- `build: Updated Java library <name> v<old> --> v<new>`
- `chore(deps): bump <name> from <old> to <new>`

If no precedent found, stop and suggest a pattern to the user.

## Step 6: Commit

```bash
git add <file>
git commit -m "<pattern>"
```

Stage only the dependency file. Skip build artefacts.

## Step 7: Repeat

If more outdated deps remain, go back to Step 1.

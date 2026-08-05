---
name: bump-deps
description: Update each outdated dependency in a separate, minimal commit.
argument-hint: "[preview]"
allowed-tools: Read, Write, Edit, Glob, Bash, Agent
---

## Goal

Update each outdated dependency in a separate commit. Enables clean rollback of
individual updates if issues would surface later.

## Mode

If the user asks for a preview, dry-run, changelog or similar we are in
changelog mode:

- Skip Steps 1, 5, 6, 7.
- Follow Steps 2–4 to identify and plan.
- Report with changelog bullets instead of committing.

## Step 1: Clean Worktree

Verify that the worktree has no unstaged, staged, or untracked changes. If it is
not clean, stop and ask the user how to proceed.

## Step 2: Identify Package Manager

Run `make outdated` to find all outdated packages. If missing, determine the
package manager and use its native outdated command directly.

Determine which package manager to use by an exhaustive search for common
dependency manifests, such as: `package.json`, `pom.xml`, `Cargo.toml`,
`requirements.txt`, `Gemfile`.

Note that a project may contain sub-projects, multiple languages, or several
package managers.

Stop if no package manager or dependency manifest can be identified.

## Step 3: Determine Version

Inspect the outdated output and choose the next dependency to update. Determine
the proper latest version, sometimes labelled `Wanted`, frequently the rightmost
version.

Update only patch and minor versions by default. Defer major updates until the
user explicitly approves each one.

If in changelog mode, delegate to a sub-agent to fetch the changelog between
current and target versions. Return terse bullets prioritizing changes relevant
to this project. If unavailable, return "unavailable".

## Step 4: Update

Use the package manager tool to update the dependency and regenerate its
lockfile. If not possible, resort to editing the dependency manifest directly.
Never edit lockfiles manually, as those are automatically updated.

## Step 5: Build, Lint & Test

Run the project's build, lint, and test commands. Check in order:

1. `make build test` or equivalent Makefile targets
2. Instructions in `AGENTS.md`, `CLAUDE.md` or `README.md`
3. Ask the user

## Step 6: Find Commit Message Convention

```bash
git --no-pager log --oneline -- <file>
```

Commit messages follow project convention. Common patterns:

- `build: Updated Java library <name> v<old> --> v<new>`
- `chore(deps): bump <name> from <old> to <new>`

If no precedent found, stop and suggest a pattern to the user.

## Step 7: Commit

Stage only the dependency file and related lockfile if one exists. Skip build
artefacts.

## Step 8: Repeat

If more outdated deps remain, go back to Step 1.

## Step 9: Report

Output one section per package. Include old version, new version, action
(update, skip, ignore) and rationale. Add changelog bullets if relevant. No
tables.

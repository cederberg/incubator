---
name: bump-deps
description: Update each outdated dependency in a separate, minimal commit.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Bash
---

## Goal

Update each outdated dependency in a separate commit. Enables clean rollback of
individual updates when issues surface later.

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

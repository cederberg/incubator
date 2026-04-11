# Project Incubator

A project for experiments, tools and research.


## git-uptodate

Prints branch, stash, and working tree status for one or more repositories.

```bash
git uptodate [<dir>...]
```

Install into `~/.local`:

```bash
mkdir -p ~/.local/bin ~/.local/share/man/man1
cp bin/git-uptodate ~/.local/bin/
cp man/git-uptodate.1 ~/.local/share/man/man1/
```

Update your `PATH`/`MANPATH` if needed in `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
export MANPATH="$HOME/.local/share/man:$MANPATH"
```

Optionally create a git alias in `~/.gitconfig`:

```ini
[alias]
    up = uptodate
```

## frontmatter

Prints the YAML front-matter block from one or more files.

```bash
frontmatter <file>...
```

Install into `~/.local/bin`:

```bash
cp bin/frontmatter ~/.local/bin/
```

## Agent Skills

- **brainstorm** — Open-ended idea generation without filtering for validity.
  Use to explore a design space, when stuck needing fresh angles, or when
  naming something.

  ```
  npx skills@latest add -g cederberg/incubator/skills/brainstorm
  ```

- **discuss** — Facilitate a focused, structured discussion on a topic. Useful
  to crystallize thoughts, develop ideas, or explore a problem.

  ```
  npx skills@latest add -g cederberg/incubator/skills/discuss
  ```

- **interview-me** — Conduct a deep, structured interview to reach shared
  understanding of a plan or topic, then document the outcome.

  ```
  npx skills@latest add -g cederberg/incubator/skills/interview-me
  ```

- **investigate** — Guide a structured, iterative technical investigation using
  hypothesis tree reasoning. Use when debugging a slow endpoint, tracing a
  regression, or investigating complex problems with unknown cause.

  ```
  npx skills@latest add -g cederberg/incubator/skills/investigate
  ```

- **refactor** — Multi-pass convergent refactoring of a specific piece of
  code. Use when code works but feels tangled, over-complicated, or like it
  hasn't found its natural form yet. Not for applying known patterns or fixing
  bugs — for discovering what the code wants to become through repeated small
  transformations.

  ```
  npx skills@latest add -g cederberg/incubator/skills/refactor
  ```

- **what-we-forgot** — Tries to recall forgotten instructions or todo items.
  Then starts working through them.

  ```
  npx skills@latest add -g cederberg/incubator/skills/what-we-forgot
  ```

- **technical-writer** — Write or review technical documents, including READMEs,
  system overviews, feature docs, and skill files.

  ```
  npx skills@latest add -g cederberg/incubator/skills/technical-writer
  ```

- **review-doc** — Review a document for internal consistency, brevity,
  clarity, and usefulness.

  ```
  npx skills@latest add -g cederberg/incubator/skills/review-doc
  ```

- **review-instructions** — Review a prompt, skill, or other instructions for
  problems. Checks language (brevity, clarity, terminology, tone, voice),
  structure (consistency, flow, format, redundancy), and precision (ambiguity,
  assumptions, coverage, omissions). Sub-agent isolates review from
  conversation context.

  ```
  npx skills@latest add -g cederberg/incubator/skills/review-instructions
  ```

- **review-session** — Analyze agent session logs for knowledge, guideline,
  and capability gaps. Produces a findings report with remedies.

  ```
  npx skills@latest add -g cederberg/incubator/skills/review-session
  ```

- **distill-context** — Creates and maintains `AGENTS.md`, the agent context
  file for a project. Syncs it with recent changes, performs full analysis, or
  realigns a stale file.

  ```
  npx skills@latest add -g cederberg/incubator/skills/distill-context
  ```

# Project Incubator

A project for experiments, tools and research.


## git-uptodate

A tool to prints branch, stash, and working tree status for one or
more repositories. Install into `~/.local` like so:

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

## Agent Skills

- **brainstorm** — Open-ended idea generation without filtering for validity.
  Use to explore a design space, when stuck needing fresh angles, or when
  naming something.

  ```
  npx skills@latest add -g cederberg/incubator/skills/brainstorm
  ```

- **discuss** — Facilitate a focused, structured discussion on a topic. Helps
  crystallize thoughts, develop ideas, or explore a problem.

  ```
  npx skills@latest add -g cederberg/incubator/skills/discuss
  ```

- **interview-me** — Conduct a deep, structured interview to reach shared
  understanding of a plan or topic, then document the outcome.

  ```
  npx skills@latest add -g cederberg/incubator/skills/interview-me
  ```

- **investigate** — Guide a structured, iterative technical investigation using
  hypothesis tree reasoning. Use when debugging or tracing a regression with
  an unknown cause.

  ```
  npx skills@latest add -g cederberg/incubator/skills/investigate
  ```

- **refactor** — Multi-pass convergent refactoring of a specific piece of
  code. Use when code works but feels tangled, over-complicated, or like it
  hasn't found its natural form yet.

  ```
  npx skills@latest add -g cederberg/incubator/skills/refactor
  ```

- **what-we-forgot** — Recall forgotten rules or to-do items from instructions
  and conversation, then work through them.

  ```
  npx skills@latest add -g cederberg/incubator/skills/what-we-forgot
  ```

- **technical-writer** — Write or review technical documents including READMEs,
  system overviews, feature docs, and skill files.

  ```
  npx skills@latest add -g cederberg/incubator/skills/technical-writer
  ```

- **review-doc** — Review a document for internal consistency, brevity,
  clarity, and usefulness.

  ```
  npx skills@latest add -g cederberg/incubator/skills/review-doc
  ```

- **review-instructions** — Review a prompt, skill, or instructions file for
  language, structure, and precision problems.

  ```
  npx skills@latest add -g cederberg/incubator/skills/review-instructions
  ```

- **review-session** — Analyze agent session logs for knowledge, guideline,
  and capability gaps. Produce remedies for the highest-leverage ones.

  ```
  npx skills@latest add -g cederberg/incubator/skills/review-session
  ```

- **distill-context** — Creates and maintains `AGENTS.md`, the agent context
  file for a project. Syncs it with recent changes, performs full analysis, or
  realigns a stale file.

  ```
  npx skills@latest add -g cederberg/incubator/skills/distill-context
  ```

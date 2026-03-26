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

- **archive-conversation**: Extracts and structures knowledge from a
  conversation for persistent storage.
- **brainstorm**: Open-ended idea generation without filtering for validity.
  Use to explore a design space, when stuck needing fresh angles, or when
  naming something.
- **discuss**: Facilitate a focused, structured discussion on a topic. Helps
  crystallize thoughts, develop ideas, or explore a problem.
- **distill-context**: Creates and maintains `AGENTS.md`, the agent context
  file for a project. Syncs it with recent changes, performs full analysis, or
  realigns a stale file.
- **interview-me**: Conduct a deep, structured interview to reach shared
  understanding of a plan or topic, then document the outcome.
- **investigate**: Guide a structured, iterative technical investigation using
  hypothesis tree reasoning. Use when debugging or tracing a regression with
  an unknown cause.
- **technical-writer**: Write or review technical documents including READMEs,
  system overviews, feature docs, and skill files.

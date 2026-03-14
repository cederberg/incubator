# Curated Examples: README

These four excerpts are taken from READMEs selected for their quality. Each illustrates something that prose rules alone cannot fully convey. Study the voice, the density of content, and — most importantly — what is *absent*.

The target voice for README is more concise than system-overview. Less background, no topology, no definitions section. The reader wants to know what it does and how to use it, fast.

---

## Example 1: An Opening That Earns Its Place (direnv)

**Source:** `direnv` README — https://github.com/direnv/direnv

> `direnv` is an extension for your shell. It augments existing shells with a new feature that can load and unload environment variables depending on the current directory.

**What this shows:**

The first sentence names the category ("extension for your shell") and the mechanism ("load and unload environment variables depending on the current directory") without marketing language. The reader knows immediately what this is and whether they care. There is no "with direnv, you can…" framing and no explanation of why environment variables per directory is a good idea.

**What an agent typically writes instead:**

> direnv is a powerful shell extension that revolutionizes how you manage your development environment. By automatically loading environment variables when you enter a directory, direnv helps developers maintain clean, isolated configurations across projects, eliminating the need for manual exports and reducing environment-related bugs.

The agent version is a marketing paragraph. It evaluates ("powerful", "revolutionizes") rather than describes. The correct version is a factual statement of category and behavior.

---

## Example 2: An Install Section With No Prose (restic)

**Source:** `restic` README — https://github.com/restic/restic

> ## Installation
>
> To install restic, use your package manager:
>
> ```
> brew install restic        # macOS
> apt install restic         # Debian/Ubuntu
> ```
>
> Or download a binary from the [releases page](https://github.com/restic/restic/releases).
>
> See the [documentation](https://restic.readthedocs.io/en/latest/020_installation.html) for more options.

**What this shows:**

Two package manager commands, one binary option, one link for more. No prose explaining why there are multiple methods, no prerequisites prose (Go is not mentioned here — the binary suffices for most users), no table of 20 distributions. The link to full docs handles the long tail without polluting the README. The section is complete without being exhaustive.

**What an agent typically writes instead:**

> ## Installation
>
> restic can be installed in several ways depending on your operating system and preferences. For macOS users, the easiest method is to use Homebrew, a popular package manager for macOS. For Linux users, restic is available in many distributions' default package repositories. On Debian-based systems such as Ubuntu, you can use apt. Alternatively, if you prefer to install from source or need the latest version, you can build restic yourself — note that Go 1.21 or later is required for this method. Binary releases are also available for all major platforms.

The agent version contains pure prose padding. The reader has to parse a paragraph to extract what the correct version conveys in three lines.

---

## Example 3: A Usage Demo That Shows, Not Tells (watchexec)

**Source:** `watchexec` README — https://github.com/watchexec/watchexec

> ## Usage
>
> ```
> $ watchexec -e rs cargo test
> ```
>
> Runs `cargo test` every time a `.rs` file changes in the current directory or any subdirectory.
>
> ```
> $ watchexec -r -e py python server.py
> ```
>
> Restarts `python server.py` when any `.py` file changes. The `-r` flag kills the previous process before starting the new one.

**What this shows:**

Two commands, each followed by exactly one sentence explaining what it does and what the key flag means. No introduction ("In this section we'll explore the most common usage patterns"). The examples are self-contained: a reader can copy them directly. The prose is subordinate to the code blocks, not the other way around.

**What an agent typically writes instead:**

> ## Usage
>
> watchexec is invoked from the command line with a command to run and optional flags to control its behavior. The basic invocation pattern is `watchexec [flags] <command>`. For example, to run `cargo test` whenever a Rust source file changes, you would use the `-e` flag to specify the file extension to watch: `watchexec -e rs cargo test`. This will cause watchexec to monitor the current directory recursively for changes to `.rs` files, and re-run `cargo test` whenever such a change is detected. If you want watchexec to restart a long-running process rather than just re-run a command, you can use the `-r` (restart) flag...

The agent version explains the pattern in prose, then embeds the command inline, then explains it again. The code blocks are an afterthought. The correct version leads with the command.

---

## Example 4: A License Section That Takes One Line (age)

**Source:** `age` README — https://github.com/FiloSottile/age

> ## License
>
> `age` is licensed under the [BSD 2-Clause License](LICENSE).

**What this shows:**

A license section does not need prose. Name the license, link to the file, done. The correct version is exactly one line. No explanation of what BSD 2-Clause means, no "you are free to use this software for any purpose as long as…" paraphrase.

**What an agent typically writes instead:**

> ## License
>
> This project is open source software, licensed under the BSD 2-Clause "Simplified" License. This means you are free to use, modify, and distribute this software, both in source and binary forms, as long as you retain the copyright notice and the license disclaimer. See the [LICENSE](LICENSE) file for the full license text.

The agent version explains the license. The reader who cares about license terms will read the LICENSE file. The README just needs to name it.

---

## Key Pattern Across All Examples

In every example, the correct version:
1. States the fact and stops — no follow-on explanation of the obvious
2. Leads with code, not prose, when showing commands
3. Trusts the reader to follow links for details
4. Uses one sentence where an agent uses one paragraph

The README voice is more telegraphic than system-overview. The reader is not building mental models — they are deciding whether to install and trying to get started. Every sentence that doesn't help them do that should be cut.

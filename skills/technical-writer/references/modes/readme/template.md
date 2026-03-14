# README Document Structure Template

Use this structure as the canonical starting point. Include only sections that have content. Do not add sections for content that does not exist.

---

## Name & One-liner

**Purpose:** Tell the reader immediately what this project is and does.

**Content:**
- Project name (H1 heading)
- One sentence stating what the project does, in plain factual terms. Not a tagline. Not a marketing phrase.
- Optional: up to 4 status/build badges on a single line immediately after the heading block, before the one-liner.

**Exclude:** Origin story, design philosophy, "why we built this", motivational framing, social proof.

---

## Install

**Purpose:** Give the reader the minimum steps needed to install the project.

**Content:**
- Steps only. No explanatory prose before the first step.
- Code blocks for every command. Use the actual command, not a placeholder.
- If multiple install methods exist (package manager, binary, source), present them as a compact list or table with method name and command. Do not expand each method into its own prose section.
- Prerequisites (e.g. "requires Go 1.21+") may appear as a single bullet before the steps.

**Exclude:** History of the packaging decisions, explanations of why a method is preferred, per-distro install tables with more than ~6 entries.

---

## Usage

**Purpose:** Show the reader how to use the project with real examples.

**Content:**
- The most common invocation(s) with real or representative output. Prefer concrete examples over descriptions.
- Code blocks for every command and output.
- One paragraph of prose per example if the example needs context that is not obvious from the command itself.
- If the project has a primary subcommand pattern, show the most important 2–3 subcommands.

**Exclude:** Full option reference (belongs in linked docs), exhaustive subcommand listings, examples that require significant setup not covered in Install.

---

## Configuration

**Purpose:** Document the named options a user needs to know to make the project behave as they want.

**Content:**
- Named options, their defaults, and the observable effect of changing them.
- Format as a table (option name, default, description) or as a bullet list (`**option** — description (default: value)`).
- Where configuration lives: file path, environment variable name, or CLI flag — whichever is applicable.

**Omit this section entirely** if the project has no meaningful configuration beyond CLI flags already covered in Usage.

---

## Development

**Purpose:** Tell contributors how to build and test from source.

**Content:**
- Prerequisites for building (tools, versions).
- Steps to build and run tests.
- Nothing beyond what is needed to run `make test` or equivalent.

**Omit this section entirely** if the intended audience is users only, or if a DEVELOPMENT.md or BUILD.md covers this.

---

## Contributing

**Purpose:** Tell contributors how to contribute without committing to a full contributing guide.

**Content:**
- A single paragraph or a link to CONTRIBUTING.md.
- At most: how to file issues, how to propose changes.

**Exclude:** Full contribution workflow, code of conduct excerpts, community pledge language.

---

## License

**Purpose:** State the license.

**Content:**
- License name, optionally with a link to the LICENSE file.
- One sentence if the license has a notable constraint (e.g. "commercial use requires a separate license").

**Format:** A single short section. Not a full license text block.

---

## Notes on Section Ordering

- Name & one-liner → Install → Usage → Configuration → Development → Contributing → License is the default order.
- Do not create a section just to have it. Omit sections with nothing to say.
- A short "See also" or "Documentation" link may be added after Usage if the project has substantial external documentation.

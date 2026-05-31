---
drafted: 2026-05-20
updated: 2026-05-22
status: active
---

# Technical writer: notes from discussion

## Background

- Core problem: agentic output is repetitive, too detailed, too wordy
- Technical-writer tries to solve this with separated writer/reviewer agents
- The skill grew large because it handles several document types
- It still contains valuable parts: voice, write/review loop, style guide
- Those parts are hard to use independently inside one large workflow

## Split vs Unified

- Decision is not simply one skill or many
- Install packaging and user-facing entry points can change independently
- Rationale for preserving one installable bundle:
  - `npx skills` installs are simple when references live inside the skill
  - Shared files near dependent skills avoid brittle cross-package paths
  - One bundle reduces coordination overhead while the model is still shifting
- Rationale for splitting into multiple skills:
  - Not every document needs full research/write/review orchestration
  - Review skills were created for convenience
  - Stand-alone review has value, especially with shared style guidance
  - Style guide is broadly useful outside the full technical-writer workflow
- Packaging nuance:
  - Split task surfaces do not require separately installed agents
  - Roles are reusable prompt contracts, not separate agents by themselves
  - Symlinks might allow shared files without duplicating them per skill

## Workflow Shape

- Review loop changed from max 3 cycles to a single pass
- Single pass may be intentional; later reviews had low marginal value
- Agents sometimes failed to follow review-count limits
- ~~The "argument-hint" front-matter isn't helpful~~
- Reword "phase" to "step" again (no longer using both)

## Mode vs Types

- Current "mode" signal is actually document type
- ~~Top-level fallback to system-feature is too eager~~
- Possible document types
  - **readme** — as-is
  - **overview** — collapses system-overview ~~+ system-feature~
  - **instruction** — broadened from skill-writer
  - **other** — requirements, change requests, research notes, etc.
- Document type names are subject to change

## Readme Documents

- No suggested changes (yet)

## Overview Documents

- ~~Template is structured for system overview (important for that type)~~
- ~~Stipulates ASCII art now, but might offer Mermaid as option~~

## Instruction Documents

- Template is too skill specific with front-matter, etc
- Other instructions might be better off without template
- Checklist is where much of the value lives (quite generic)

## Other Documents

- ~~Interview-as-discovery replaces codebase scan when context is missing~~
- ~~No fixed template can exist for unknown document types~~
- ~~User brings structure, agent may help define it or infer from training~~
- ~~Checklist with sections per doc type is an extensible model~~

## Open Questions

- Test whether git symlinks work with `npx skills` installs
- If symlinks work, shared files may stay installable without duplication
- Does manager "do not read" rule make workflow brittle when structure is
  unknown?
- ~~Are system-overview and system-feature one type or related presets?~~
- ~~Is "other" a reworked system-feature/generic path?~~
- ~~Did generic become system-feature too narrowly?~~
- Are the examples.md files provided really useful? Can they be shorter?

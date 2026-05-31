---
drafted: 2026-05-31
status: active
---

# Structured Notes

_Organizes ideas, notes, and plans into a file structure._

## Directory Structure

- Each topic lives in `notes/<topic>/`.
- Topic names are specific; generic names are avoided.
- Filenames are understandable without directory context.
- `frontmatter notes/<topic>` is the topic inventory.

## Front Matter

- Each note in this directory contains YAML front matter:
  - `drafted` for the original creation date.
  - `updated` for the latest edit date; omit if unchanged.
  - `status` for lifecycle: `idea`, `active`, or `archived`.

## Actionable Plans

- [ ] Actionable plans lead with a brief overall goal statement.
- [ ] Use sections as headings, each containing a list of checkbox items.
- [ ] Each checkbox item is limited to a single-line fact or idea.
- [ ] Items are checked off when fixed or graduated into other docs.
- [ ] Kept compact, lean, and human-readable; add nothing without agreement.
- [ ] First section is always `About this file` with the above notes adapted.

## Current Topics

- `outliner-tool/` — outliner planning, review notes, and data-format support.
- `skill-audit-warnings/` — skill audit warnings and mitigation notes.
- `technical-writer/` — technical-writer workflow and mode refinement.

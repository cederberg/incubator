# AGENTS.md

## File Reference
- [README.md] — tools, skills, usage examples
- [skills/technical-writer/references/rules/style-guide.md] - writing style guide

## Command Reference
```bash
frontmatter <file(s)>...               # extract front-matter (skills)
prettier -w --prose-wrap always <file> # format markdown file (post-edit)
```

## General
- Radical brevity — in code, rules, and responses
- Read related reference documents before starting a task
- Update `README.md` when tool or skill usage changes.
- Update `AGENTS.md` for new instructions; don't use the memory tool
- Explore feature additions with user until intent is mutually clear
- Verify any code examples against source or command output

## Skill Instructions
- Edit at `skills/{{name}}/` (project root), ignore global location for edits
- Set `disable-model-invocation: true` to prevent automatic triggering
- Only add instructions where agents will err without them
- Confirm skill edits with user before applying
- After edit, remind user to run /review-instructions
- Use $VARIABLE for exact facts captured once; reference by name thereafter
- Use `{{placeholder}}` for literal slots in generated output
- Use `<arg> [<optional>]` for CLI command templates

## Python Code
- Name what a variable is; e.g. `line` not `raw`
- Prioritize fewer lines; e.g. named lambda vars to allow single-line below
- Prefer returning iterators over lists
- Use positive guards, not `if not COND: continue`

## Shell Scripts
- Use kebab-case function names with single-line comment above
- Color constants: `COLOR_X=$(tput ... 2>/dev/null || echo '')`
- Binary safety: `grep -a`, `head -n 1 ... 2>/dev/null`
- Use `;` (spaces around semicolon): `if cond ; then`, `while cond ; do`

## Sub-Agents

- Resolve document-relative paths to absolute before passing to sub-agents

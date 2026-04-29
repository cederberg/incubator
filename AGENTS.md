# AGENTS.md

## File Reference
- [README.md] — tools, skills, usage examples

## General
- Radical brevity — in code, rules, and responses
- Read related reference documents before starting a task
- Update `README.md` when tool or skill usage changes.
- Write project notes to `AGENTS.md` or `DEVELOPMENT.md`, not to the memory tool
- Explore feature additions with the user; implement only once intent is mutually clear
- Verify examples against source or command output

## Skills
- Use `bin/frontmatter <file>...` to read skill file front-matter
- Set `disable-model-invocation: true` to prevent automatic triggering
- Codify rules when recurring mistakes or unnecessary searches appear
- Only add instructions where agents will err without them
- Confirm changes with user first, then batch edits in one pass
- After edit, remind user to run /review-instructions

## Python Code
- Name what a variable is; e.g. `line` not `raw`
- Prioritize fewer lines; e.g. named lambda vars to allow compact single-line below
- Prefer returning iterators over lists
- Use positive guards, not `if not COND: continue`

## Shell Scripts
- Use kebab-case function names with single-line comment above
- Color constants: `COLOR_X=$(tput ... 2>/dev/null || echo '')`
- Binary safety: `grep -a`, `head -n 1 ... 2>/dev/null`
- Use ` ; ` (spaces around semicolon): `if cond ; then`, `while cond ; do`

## Sub-Agents
- Resolve document-relative paths to absolute before passing to sub-agents

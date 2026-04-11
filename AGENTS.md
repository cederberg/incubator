# AGENTS.md

## References
- [README.md] — tools, skills, usage examples

## General Guidelines
- Use brief and precise wording.
- Confirm feature additions (new options, capabilities, etc.) with user.
- Store project conventions, knowledge and rules in `AGENTS.md` (not in memory tool entries).
- Update `README.md` when tool or skill usage changes.

## Skill Guidelines
- Use `bin/frontmatter <file>...` to read skill file front-matter.
- Set `disable-model-invocation: true` to prevent automatic triggering.
- Codify rules when recurring mistakes or unnecessary searches appear.
- Only add instructions where agents will err without them.
- Confirm changes with user first, then batch edits in one pass.
- After edit, remind user to run /review-instructions.

## Sub-agent Guidelines
- Resolve document-relative paths to absolute before passing to sub-agents.
- For open-ended exploration, ask for all ideas — valid or not.

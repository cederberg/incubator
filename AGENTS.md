# AGENTS.md

## References
- [README.md] — tools, skills, usage examples

## General Guidelines
- Always use brief and precise wording.
- Confirm feature additions with user.
- Store persistent project knowledge as entries in `AGENTS.md`.

## Skill Guidelines
- Use `bin/frontmatter <file>...` to read skill file front-matter.
- Set `disable-model-invocation: true` to only trigger via `/<skill-name>`.
- Prefer open-ended instructions; agents are competent to fill gaps.
- Codify rules when evidence indicates a problem or to reduce agent exploration.
- Confirm changes with user first, then batch edits in one pass.
- After edit, remind user to run /review-instructions.
- After add, rename or remove, update `README.md`

## Sub-agents
- Resolve document-relative paths to absolute before passing to sub-agents.
- For open-ended exploration, ask for all ideas — valid or not.

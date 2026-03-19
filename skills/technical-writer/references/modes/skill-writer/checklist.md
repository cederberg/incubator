# Structural Checklist: Skill File

## Structure

- [ ] Skill body opens with an H1 heading matching the `name` frontmatter field
- [ ] Activation section is present if the skill auto-activates from context
- [ ] If an Activation modes table is present: it includes a labelled default and inference rules
- [ ] Any catch-all or generic mode is guarded against silent inference
- [ ] Preconditions, if present, appears after Activation and before Workflow
- [ ] Reference Files, if present, appears after the output specification

## Frontmatter

- [ ] `name` uses kebab-case and contains only lowercase letters, numbers, and hyphens (max 64 characters)
- [ ] `description` is present and states what the skill does and when to trigger (not only a capability statement)
- [ ] `description` names at least one concrete trigger condition — an observable user action, phrasing pattern, or file state
- [ ] `description` is under 1,024 characters
- [ ] `description` contains no hedging language ("typically", "usually", "generally", "may")
- [ ] If near-neighbour skills exist that overlap with this skill: `description` includes at least one explicit non-trigger condition
- [ ] Ask a subagent: "When would you use the [skill name] skill?" — verify the answer reflects the intended trigger conditions
- [ ] `disable-model-invocation: true` is set for any skill with side effects that must not run automatically
- [ ] `context: fork` is set for any skill that must run without access to conversation history

## Workflow

- [ ] Workflow steps are numbered or named phases; no prose narrative substitutes for ordered steps
- [ ] Every sub-agent phase specifies the agent's role, the inputs it receives, and the artifact or output it produces
- [ ] Any review-revise loop states a maximum number of cycles
- [ ] If sub-agents are used: adjacent phases that could plausibly be merged include an isolation rationale

## Output

- [ ] Every artifact has an exact file path, naming convention, or output template

## Reference Files

- [ ] Every file delegated to a sub-agent appears in a Reference Files table (columns: File, Consumer, Purpose)
- [ ] File paths that vary by mode or invocation are named as variables, not hardcoded strings

## Quality

- [ ] SKILL.md body is under 500 lines
- [ ] Terminology is consistent throughout — the same concept is not referred to by different names
- [ ] No section is empty or consists only of placeholder text

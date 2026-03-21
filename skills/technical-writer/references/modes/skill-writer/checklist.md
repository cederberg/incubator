# Structural Checklist: Skill File

## Structure

- [ ] Activation section is present if the skill auto-activates from context
- [ ] If an Activation modes table is present: it includes a labelled default
      and inference rules
- [ ] Any catch-all or generic mode is guarded against silent inference

## Frontmatter

- [ ] `name` uses kebab-case and contains only lowercase letters, numbers,
      and hyphens (max 64 characters)
- [ ] `description` is present and states what the skill does and when to
      trigger (not only a capability statement)
- [ ] `description` names at least one concrete trigger condition — an
      observable user action, phrasing pattern, or file state
- [ ] `description` is under 1,024 characters
- [ ] `description` contains no hedging language ("typically", "usually",
      "generally", "may")
- [ ] If near-neighbour skills exist that overlap with this skill:
      `description` includes at least one explicit non-trigger condition
- [ ] `disable-model-invocation: true` is set for any skill with side effects
      that must not run automatically
- [ ] `context: fork` is set for any skill that must run without access to
      conversation history

## Workflow

- [ ] Workflow steps are numbered or named; no prose narrative substitutes
      for ordered steps
- [ ] Every sub-agent step specifies the agent's role, the inputs it
      receives, and the artifact or output it produces
- [ ] No workflow step includes verbatim prompt text — specify what the
      prompt should cover, not the wording
- [ ] Any review-revise loop states a maximum number of cycles

## Output

- [ ] Every artifact produced by the skill has an exact file path, naming
      convention, or output template — either in an Output section or inline
      in the workflow step that produces it

## Reference Files

- [ ] Every file delegated to a sub-agent appears in a Reference Files table
      (columns: File, Consumer, Purpose)
- [ ] Every file listed in the Reference Files table exists in the skill
      directory
- [ ] File paths that vary by mode or invocation are named as variables, not
      hardcoded strings

## Quality

- [ ] SKILL.md body is under 500 lines; simple skills (single-agent, linear
      workflow) under 100 lines
- [ ] Each instruction earns its place: would the agent get this wrong
      without it? If not, remove it.
- [ ] Terminology is consistent throughout — the same concept is not referred
      to by different names
- [ ] No section is empty or consists only of placeholder text

# Structural Checklist: Skill File

Verify each item explicitly.

## Frontmatter

- [ ] `name` is present and uses kebab-case
- [ ] `description` states what the skill does and when to use it (not what it produces alone)
- [ ] `description` names at least one concrete trigger condition, not only a capability statement
- [ ] `description` contains no hedging language ("typically", "usually", "generally", "may")
- [ ] No synonym in the frontmatter duplicates a phrase already covered by the Mode Detection inference rules

## Activation and Modes

- [ ] If single-mode: an Activation or Preconditions section states the trigger condition without hedging
- [ ] If multi-mode: a Modes table is present with Mode, When to use, and Output columns
- [ ] If multi-mode: every mode appears in the Mode Detection section with at least one example user phrase
- [ ] If multi-mode: a default or fallback mode is named explicitly
- [ ] If multi-mode: any catch-all or generic mode is guarded against silent inference

## Workflow

- [ ] Workflow steps are numbered or named phases; no prose narrative substitutes for ordered steps
- [ ] Every sub-agent phase specifies the agent's role, the inputs passed to it, and the output file it writes
- [ ] Any review-revise loop states a maximum number of cycles
- [ ] If sub-agents are used: a rationale for phase isolation is present when the phase could plausibly be merged with an adjacent phase without apparent loss

## Output

- [ ] Every artifact the skill produces has an exact file path, naming convention, or output template with explicit placeholders
- [ ] If a `$WORK_DIR` pattern is used: it is set once and referenced consistently

## Reference Files

- [ ] Every file delegated to a sub-agent appears in a Reference Files table with consumer and purpose
- [ ] No file path is hardcoded in instructions where the path should vary by mode or invocation

## Quality

- [ ] No sentence explains the rationale for a design decision ("This is done because…", "The reason for X is…", "X exists to prevent…")
- [ ] No hedging language anywhere in the instruction body: "typically", "usually", "generally", "in most cases", "often"
- [ ] No section is present that has nothing to say

# Structural Checklist: Skill File

## Structure

- [ ] Skill body opens with an H1 heading matching the `name` frontmatter field
- [ ] Section order: H1 → Modes + Mode Detection (multi-mode) or Activation (single-mode) → Preconditions (if present) → Your Role (if orchestrator) → Workflow → Output → Reference Files (if present)
- [ ] Workflow section is present
- [ ] Output section is present

## Frontmatter

- [ ] `name` uses kebab-case and contains only lowercase letters, numbers, and hyphens (max 64 characters)
- [ ] `description` is present and states what the skill does and when to trigger (not only a capability statement)
- [ ] `description` names at least one concrete trigger condition — an observable user action, phrasing pattern, or file state
- [ ] `description` is under 1,024 characters
- [ ] `description` contains no hedging language ("typically", "usually", "generally", "may")
- [ ] If the skill has near-neighbour skills that could be confused with it: `description` includes at least one explicit non-trigger condition
- [ ] `disable-model-invocation: true` is set for any skill with side effects that must not run automatically
- [ ] `context: fork` is set for any skill that must run without access to conversation history

## Activation and Modes

- [ ] If single-mode: an Activation or Preconditions section states the trigger condition without hedging
- [ ] If multi-mode: a Modes table is present with Mode, When to use, and Output columns
- [ ] If multi-mode: every mode appears in the Mode Detection section with at least one example user phrase
- [ ] If multi-mode: a default or fallback mode is named explicitly
- [ ] If multi-mode: any catch-all or generic mode is guarded against silent inference

## Workflow

- [ ] Workflow steps are numbered or named phases; no prose narrative substitutes for ordered steps
- [ ] Every sub-agent phase specifies the agent's role, the inputs passed to it, and the artifact or output it produces
- [ ] Any review-revise loop states a maximum number of cycles
- [ ] If sub-agents are used: a rationale for phase isolation is present when the phase could plausibly be merged with an adjacent phase

## Output

- [ ] Every artifact has an exact file path, naming convention, or output template

## Reference Files

- [ ] Every file delegated to a sub-agent appears in a Reference Files table (columns: File, Consumer, Purpose)
- [ ] File paths that vary by mode or invocation are named as variables, not hardcoded strings

## Quality

- [ ] No section is empty or consists only of placeholder text

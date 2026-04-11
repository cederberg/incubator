---
name: refactor
description: >
    Multi-pass convergent refactoring of a specific piece of code. Use when code
    works but feels tangled, over-complicated, or like it hasn't found its natural
    form yet. Not for applying known patterns or fixing bugs — for discovering
    what the code wants to become through repeated small transformations.
disable-model-invocation: true
argument-hint: "<code reference> [additional instructions]"
allowed-tools: Read, Write, Glob, Bash
---

# Iterative Refactoring

## Background

Most refactoring advice is catalog-based: identify a smell, apply the fix.
That works for clear-cut problems — a method is too long, a name is
misleading, duplication exists. But some code isn't *broken* in any catalogued
way. It's just not right yet. The logic is correct. The tests pass. But the
structure doesn't match the idea it's expressing.

This skill addresses that situation. The process is closer to sculpting than
engineering: remove a bit of material, step back, observe what's revealed,
let that observation guide the next cut. Each transformation is small and
behavior-preserving, but the sequence can produce a result that no single
step could have planned for.

### Why each step matters

The key difficulty is that **each step creates the conditions for the next**.
A transformation that seems minor — switching from a collected list to
a stream — can reveal that two separate code paths are actually the same
path with different predicates. That insight is invisible before the
transformation exists. You cannot plan the full sequence in advance because
the intermediate forms are what generate the ideas.

This means the process is fundamentally exploratory. There is no target state
to specify upfront. The code converges toward a form that feels inevitable —
where every line earns its place and the structure mirrors the intent — but
you only recognize that form when you arrive.

### What drives each step

The engine of the process is a question: **"What bothers me about this?"**
Not "what pattern can I apply?" but "what feels off, redundant, misaligned,
or unnecessarily complex?" The answer might be:

- A variable that exists only to be used once
- Two branches that feel like they should be one
- A name that no longer fits what the code does
- An imperative sequence hiding a declarative idea
- A null check masking a deeper design question
- Structural symmetry that isn't yet expressed in the code

These observations don't come from a checklist. They come from reading the
code with fresh eyes after each change — treating the current form as a new
starting point, not a waypoint toward a predetermined goal.

## Process

The process is a loop, not a pipeline. After each step, genuinely pause and
re-read the code as if seeing it for the first time. Don't rush to the next
transformation.

### 1. Understand

Read the code. Understand what it does and why. Identify the behavioral
contract — what must remain true across all transformations. If tests exist,
note them. If they don't, acknowledge the risk.

### 2. Observe

Look at the code's current form and ask: what's not quite right? What creates
friction when reading? What would you change if you were explaining this code
to someone? Name the observation specifically — not "it's messy" but "the
ternary on line 12 obscures the fallback logic."

If nothing stands out, the code may have reached its natural form. That is a
valid and desirable outcome.

### 3. Transform

Make one small, behavior-preserving change that addresses the observation.
Verify the change preserves behavior. Present the result.

### 4. Re-observe

Read the transformed code as if seeing it for the first time. The question is
not "did my change work?" but **"what does this new form reveal?"** Often the
answer is a new observation that was invisible before.

Return to step 2.

## Working with the user

This is a collaborative process. The human's aesthetic judgment is a primary
signal — often the most important one.

- After each transformation, present the new code and your observation about
  what it reveals. Invite the user's reaction.
- If the user says "that's not quite right" or "I don't like that direction,"
  treat this as the highest-priority signal. Ask what specifically bothers them.
- Be willing to try a direction, discover it doesn't improve things, and
  backtrack. Dead ends are information, not failure.
- When proposing a next step, explain what observation motivates it — not just
  what the change is, but what you noticed that suggested it.
- If you have multiple observations, share them and let the user choose
  the direction.

## Kinds of insight that drive convergence

These are not patterns to apply but categories of noticing — things to be
alert to when re-reading code after a transformation.

**Structural redundancy.** Two code paths that differ only in a predicate or
a constant. Often invisible until imperative code is rewritten functionally,
or vice versa.

**Latent unification.** A special case that is actually the general case with
a constant parameter. The classic: `if (x) return a.first()` and
`return a.filter(pred).first()` are the same operation when `pred` is
`_ -> true`.

**Name–reality drift.** After transformations, a name may no longer describe
what it holds or does. Renaming often triggers further observations about
scope or responsibility.

**Abstraction pressure.** A language idiom, utility, or standard library
concept that would express the intent more directly than the current code.
Using `Objects.equals` instead of manual null checks. Using `Optional.or()`
instead of if-else chains. The language often has a word for what the code
is doing by hand.

**Unnecessary ceremony.** A guard clause, temporary variable, type conversion,
or intermediate collection that was needed in an earlier form but became
redundant after a transformation.

**Inverted emphasis.** The code puts the exception first and the rule second,
or buries main logic inside a branch. Restructuring to lead with the common
case often simplifies everything around it.

## Reference example

See [references/example-findmatch.md](references/example-findmatch.md) for
a complete worked example — seven steps taking a tangled SQL+Java method to a
clean four-line pipeline. Study the *shape* of the journey: what was observed
after each step, and how each transformation revealed the next. The specific
language (Java) and idioms are incidental.

## When to stop

The process ends when re-reading produces no strong observations — when each
line feels necessary and the structure matches the intent. This is a judgment
call, not a metric. Resist the urge to keep going; over-refactoring is real.

Signs the code has converged:

- You can explain what it does in one sentence, and the code reads like that
  sentence
- No line makes you want to add a comment to explain it
- The method name and the body tell the same story
- Removing any line would break behavior or clarity

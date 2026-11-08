---
name: design-session
description: >-
  Lead a design discussion from principles to details while a background
  designer researches and drafts. Use to design a feature or system, or resume a
  session from its ledger.
argument-hint: "<topic|topic-file|ledger-file>"
---

Act as the conversation lead in a design session: facilitate the discussion
between the user and a background AI designer. The user leads the design; you
lead the agenda. Following every tangent is the failure this skill exists to
prevent.

The user's attention is the scarce resource. Focus it along a path that leads
forward without getting stuck on details. Aim for replies that settle something
or ask something. When something cannot be settled now, suggest postponing it or
adopting an interim solution.

Design one increment per session, small enough to settle before the user leaves.
Follow-up sessions build it (and spec it, when the close defers the spec).
Learnings from the prototype then inform the next design. Prioritize decisions
that are costly to reverse, such as API shapes, stored data and contracts with
other services. Prefer leaving cheap decisions to the implementer.

## Roles

### Conversation lead

Talk with the user and brief the designer; leave research, drafting and file
work to it. Brief it with each decision, each piece of work, and each action you
take yourself, so the ledger records it. Keep the next question prepared before
the user answers the current one.

Recommend a direction, surface meaningful tradeoffs, and keep the agenda moving.
The user chooses the design direction; leave routine implementation choices to
the implementer and record what follows from settled decisions. A recommendation
does not become an accepted decision merely because it appears in a draft.

### Background designer

Spawn one long-lived background designer using your own model and effort level.
Brief it with its role, scope, ledger path and the search methods below. It
reports to you only, never to the user. Send its agent id and your session id
with the first follow-up brief, when available.

Send every later task to the same designer through agent messaging, so it keeps
its context. The designer:

- Owns the ledger and updates it with each brief before reporting
- Drafts proposals, researches this repo and sibling repos, and runs one-off
  subagents; writes design files at close
- Consults sibling repos on the user's machine for house conventions and
  existing solutions
- Checks the other project's source before reporting a cross-service fact as
  unverified; cites the source, or states what remains unverified if unavailable
- Raises a rule that no settled decision implies as a question with a pick,
  rather than writing it into a draft or design file unasked
- Keeps reports brief and DRY: verdict first, evidence cited by its section in
  `$SESSION_DIR/research.md` rather than restated
- Ends each report with a `Noticed:` line for discrepancies outside the task,
  and adds each to **Parked**
- Keeps drafts in $SESSION_DIR, never in a scratchpad, so they survive until
  close

### Designer search

The first plausible design anchors later drafts. Brief the designer to widen the
search before consequential recommendations, choosing among these methods:

- **Reframe:** restate the problem at least two ways that imply different
  solutions (a data problem, a contract problem, a feature to delete), and
  sketch one option from each
- **Perspectives:** spawn one subagent per affected viewpoint (API consumer,
  stored data, operations, another service), each mandated to propose the design
  its viewpoint wants
- **Clean slate:** spawn one subagent told not to read the existing
  implementation, so its proposal shows what fitting the existing code costs
- **Cross-repo:** research how sibling repos solve the same problem and what
  they expect from this repo
- **Adversarial review:** spawn reviewers to attack the recommendation, each
  with one focus (simplicity, failure modes, operating cost)

Have the designer give each subagent one mandate and the problem statement; only
adversarial reviewers see the recommendation. When viewpoints disagree, the
designer reports the disagreement as the question to ask; it is the real
decision.

When the user rejects a pick, have the designer reframe before recommending
again in that thread. When a pick copies another service's data or changes its
contract, its alternatives include depending on that service instead.

## Start or resume

Use the supplied design topic, topic file, or ledger path.

For a new session, prefer a topic subdirectory in any existing in-project work
dir. Otherwise, create a temporary directory named for the topic. Capture its
absolute path as $SESSION_DIR; keep the ledger at `$SESSION_DIR/ledger.md`.

- **Topic or topic file:** read the file, if any, then settle the topic's scope
  with the user in one or two turns. Spawn the designer to create the ledger
  from `references/ledger-template.md` and prepare the first principles
  question. Once created, print the ledger's absolute path verbatim; ask for
  confirmation if outside the project base directory.
- **Ledger:** read it, set $SESSION_DIR to its parent directory, and spawn a new
  designer. Its first task is to check each **In flight** entry against existing
  outcomes and finish incomplete work. Restate the topic and layer in one line,
  then ask the first open thread's question with your pick.

## Discussion

### Layers and discovery

Design top-down. Settle each layer before opening the next:

1. **Principles:** the few rules every later decision must follow
2. **Patterns:** the shapes that realise the principles
3. **Details:** contracts, edge cases and configuration

A layer is settled when the user confirms its one-paragraph summary. Brief the
designer to update **Settled layers**, then open the next layer.

Normally park details raised before their layer opens. Record details that
follow from settled principles without asking the user to decide them again.
Prefer leaving cheap, reversible decisions to the implementer; record a view
under **Decisions** when the user volunteers one.

Top-down discussion need not mean top-down discovery. The designer can
investigate a concrete constraint early when it could undermine the direction,
and report the evidence and implication. Backup retention, for example, can
constrain a promise of complete data deletion. Judge whether the implication
belongs at the current layer, or ask the user whether to examine it now. Prefer
a concrete concern over an early tour of edge cases.

### Questions and threads

Have the designer prepare a recommendation, plus one or two alternatives that
differ in kind, if any exist. Prefer a next question independent of the current
answer; a different thread alone does not guarantee independence.

A thread is one entry in **Open threads**, ordered by the agenda. Follow clear
user direction without requiring a special priority phrase. Record incidental
topics in **Open threads** or **Parked**, and say when they will return. A user
revision of a settled decision reopens it at the top of **Open threads**.

Reconsider questions invalidated by new information. Otherwise, prefer the next
prepared question at the current layer, adjusting to the user's direction.

### Lead's operating loop

Keep replies brief and focused on the agenda. Acknowledge what you recorded from
the user's message. As a strong default, raise at most two items; hold surplus
items for the next reply.

- Ask prepared questions in free-form chat, never through structured question
  tools. Give your recommendation with `Pick: <recommendation>`.
- Ask the next prepared question promptly, and brief the designer on the user's
  answer in the same turn. If none is prepared, draft the first open thread's
  question yourself, with your pick.
- Answer the user's questions from what you know, marking ungrounded answers
  unverified. Have the designer ground them, then bring the verified result and
  proposed consequence into a later reply.
- Make a contradiction with a settled decision explicit: `Reopens: <decision>`.
  Seek the user's decision before changing it.
- Announce parking in a short line, such as “Parking X; I'll circle back after
  Y.”

A grounded answer can use `Verified: <result>; I propose <consequence>`. Keep
the verified fact distinct from your recommendation.

### Background results

When the designer or another session reports without a new user message, reply
with exactly `Background work. Questions above.` and nothing else. Bring the
result into your reply to the user's next message, even when the user awaits it.
Do not deliver an awaited report immediately merely because it arrived.

Use the normal discussion reply instead when no question is open in the chat, or
when the result invalidates an open question's premise. In the latter case,
withdraw that question in one line and give its replacement with your pick.

### Ledger

The ledger is the session's only resumption state: a new session resumes from it
alone. Have the designer maintain:

- The lead's session id and designer's agent id, when available, so a compacted
  lead can keep briefing the same designer
- Topic and scope, layer in progress, and design files
- Each settled layer's confirmed summary and date, one short paragraph; edit it
  only when the user reopens and re-confirms the layer. Record later
  clarifications under **Decisions**
- Decisions and rejected alternatives, one line each; replace them with
  references once the canonical text lives in a design file
- Open threads in agenda order, the first carrying its prepared question and
  pick
- Parked details and questions, each with the layer or thread it waits for; move
  each into **Open threads** or drop it when that layer or thread opens
- Work in flight with the designer
- Each commit made and issue filed; during close, each item's confirmed home and
  each superseded `file:line`

## Pause or close

When the user pauses, have the designer update the ledger and finish or park its
work. Print the absolute ledger path verbatim for resuming the skill.

When the last layer settles, prepare the close with the designer:

1. Propose one home per ledger item, following project conventions. Search
   specs, notes, manuals and README files for every rule the design replaces,
   including pages no layer touched. List each hit as `file:line`.
2. Present items grouped by proposed home, marking each item the user never
   decided. The user confirms or redirects each item; write a marked item only
   on their explicit yes.
3. Give each fact one canonical home. Put a one-line pointer in other documents
   that need it, rather than restating it.

Use these destinations as the starting point:

- **Contracts:** API shapes, stored data, errors and rules another service
  relies on belong in the project's spec location, or a spec issue when deferred
- **Follow-ups and deferred ideas:** the project's backlog or planning document
- **Work for this repo or another:** an issue citing the spec sections
- **Manual and README hits:** tasks in the implementation issue; these documents
  change when the code ships

Ask in plain chat which follow-up to take, with your pick:

- Write the spec now; prefer this unless the spec edits outgrow the session
- Create 1–N issues for other agents to spec, each carrying its contracts
- Start another design session for a deferred part
- Take another action the outcome calls for

### Spec writing and review

Have the designer brief one fresh writer from settled layers, accepted
**Decisions**, confirmed homes and superseded `file:line` hits. The writer reads
nothing else in $SESSION_DIR, so discarded options stay out of the text. Only
the writer edits the spec; it makes minimal edits and lists open questions.

The designer reviews the diff against the ledger, then has an independent
subagent attack it. It sends review findings to the writer, except rules no
settled decision implies: those return to you as questions with picks.

Present open questions and those rules as one numbered list, each with its pick,
so the user can answer by exception. The designer sends the answers to the
writer and reviews the result.

### Completion

For every follow-up choice, have the designer:

- Write each confirmed non-spec item to its home
- Commit on the user's instruction; ask whether to push before filing issues
  that cite the commit
- When committing, file issues afterward and cite the committed spec sections.
  Otherwise, file issues carrying their accepted contracts. Update earlier
  issues that the close answers
- Check that every ledger item reached its home, then delete $SESSION_DIR

Avoid continuing into implementation in this session; its context is spent on
the design.

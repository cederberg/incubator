# Abstraction Calibration Rules

The hardest part of writing a system overview is knowing what to exclude. Agents default to including too much because they model "more detail = more correct." In system overview documentation, the opposite is true: unnecessary detail degrades comprehension.

## The Core Test

Before including any fact, ask: **Would a technically literate person who has not read the source code need this fact to understand what the system does?**

- "Technically literate" means comfortable with distributed systems, APIs, and databases.
- "Has not read the source code" means they cannot infer class names, SQL schemas, or algorithm choices from the doc.
- "What the system does" means its externally observable behavior, not its internal implementation.

If the answer is no, exclude the fact.

---

## Five Exclusion Heuristics

### 1. The Rename Test

> "If this name changed — file renamed, column renamed, method renamed — would the system's observable behavior change?"

If no: exclude it. Names of classes, methods, and internal variables are implementation detail.

If yes: it might belong. External API names, named status values, and event type names pass this test because they have behavioral meaning.

**Examples:**
- `OrderRepository.save(order)` — fails. The method name could change without changing behavior.
- `COMPLETED` status — passes. Changing this name would change what operators see in monitoring.
- `entity_state` table name — borderline. Passes if the doc needs to identify a specific data store; fails if it's just incidental.

### 2. The Code-Only Test

> "Does this fact only make sense to someone who has read the source code?"

If yes: exclude it.

**Examples:**
- "The system uses a Comparator chain that sorts by FUP status first" — fails. Requires reading the code.
- "FUP messages take priority over non-FUP messages" — passes. Observable from the system's output.

### 3. The 'How' Test

> "Am I explaining how the system does something, rather than what it does?"

If yes: rewrite it as what, or exclude it.

**Examples:**
- "The system calls `LookupService.findAccount(id)` via HTTP GET and parses the JSON response" — fails. This is how.
- "The system looks up the account details using the entity ID from the event" — passes. This is what.
- "The deduplication check compares the event timestamp to the previous event's `processed_at` column" — fails.
- "Events are ignored if a matching event was processed less than 24 hours ago" — passes.

### 4. The Platform Test

> "Is this detail about the platform or framework, rather than the system itself?"

If yes: exclude it.

**Examples:**
- "Uses Spring Boot's @Scheduled annotation with a 5-minute fixedDelay" — fails. Platform detail.
- "The system periodically fetches updated SMS templates" — passes. Behavioral fact.
- "Kafka consumer group rebalancing triggers a brief processing pause" — fails. Platform behavior.
- "The system processes events in parallel across multiple worker instances" — passes. Behavioral fact with operational implications.

### 5. The Diagram Sufficiency Test

> "Is this already clear from the architecture diagram?"

If yes: exclude it from prose — don't repeat what the diagram already shows.

**Examples:**
- "The system receives events from the message broker" — may fail if the diagram shows this. Use the specific component name only if the diagram doesn't already make this clear.
- The diagram shows Component A → Service B. Don't also write "Component A sends data to Service B" unless you need to add something the diagram doesn't show.

---

## Verbosity Failure Modes

These patterns are the most common ways agents produce over-specified documentation.

### Hedging

Hedging words signal that the writer is not confident enough to state the rule clearly.

**Fail:** "Events are typically processed within a few seconds, but may occasionally take longer depending on system load."
**Pass:** "Events are processed asynchronously." *(If timing is operationally important, state the specific threshold and what happens if it's missed.)*

Cut: "typically", "usually", "generally", "in most cases", "often", "may", "might", "could potentially".

### Meta-Commentary

Sentences that describe the document, not the system.

**Fail:** "This section describes how the system handles duplicate events."
**Pass:** *(Start the section directly: "Both Network Attach and Data Traffic events may be filtered…")*

Cut: "This section describes…", "As mentioned above…", "The following explains…", "It is important to note that…"

### Over-Enumeration

Listing every sub-case when the main rule plus one Note: covers them all.

**Fail:**
```
Events may be duplicate due to:
- Network retransmission
- 3G nodes sending before response
- 3G nodes sending on failed attach
- Application-level retry on error
- Operator sending duplicate notifications
```
**Pass:** "Events may arrive more than once, particularly from 3G nodes which send without waiting for an attach response."

Reserve bullet lists for named, enumerable items (statuses, message types, fields). Don't use them for explanatory prose broken into fragments.

### Passive Re-Stating

Describing in prose what the architecture diagram already shows.

**Fail:** "After the event is received by the intake component, it is stored in the database. The worker then picks it up from the database for processing."
**Pass:** *(This is shown in the topology diagram. Don't repeat it in prose.)*

### Justification Creep

Adding the rationale for a design decision.

**Fail:** "Separate delivery accounts are used per region to reduce the risk of outbound rate limiting, as a single account could be throttled if one region has unusually high traffic."
**Pass:** "Separate delivery accounts are used per region to reduce rate limiting risk."

The reason can be noted in one clause at most. A full explanation belongs in an ADR, not a system overview.

---

## Borderline Cases

Some facts are genuinely ambiguous. These require judgment:

- **Database table names:** Include when the table name is the clearest way to identify a data store the reader needs to reason about (e.g., `entity_state`, `notification_block`). Exclude when the name is incidental.
- **Named error states:** Include when the status is externally visible or operationally significant (e.g., `FAILED` events trigger alerts). Exclude when it's purely internal.
- **External system names:** Include always. They are architectural actors, not implementation detail.
- **"Note:" vs. new sentence:** Use Note: when the caveat would interrupt the flow of the main paragraph. Use a new sentence when the caveat is equally important to the main fact.

When in doubt, exclude. The code executes; the doc does not. An omission is recoverable. A misleading inclusion is not.

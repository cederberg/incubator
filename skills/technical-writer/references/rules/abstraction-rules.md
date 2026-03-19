# Abstraction Calibration Rules

The hardest part of writing a system overview is knowing what to exclude. Agents default to including too much because they model "more detail = more correct." In system overview documentation, the opposite is true: unnecessary detail degrades comprehension.

## The Core Test

Before including any fact, ask: **Would a technically literate person who has not read the source code need this fact to understand what the system does?**

- "Technically literate" means comfortable with distributed systems, APIs, and databases.
- "Has not read the source code" means they cannot infer class names, SQL schemas, or algorithm choices from the doc.
- "What the system does" means its externally observable behavior, not its internal implementation.

If the answer is no, exclude the fact.

---

## Four Exclusion Heuristics

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

If yes: rewrite it as what, or exclude it. Note that state transitions and observable triggers describe what the system does.

**Examples:**
- "The system calls `LookupService.findAccount(id)` via HTTP GET and parses the JSON response" — fails.
- "The system looks up the account details using the entity ID from the event" — passes.
- "The deduplication check compares the event timestamp to the previous event's `processed_at` column" — fails.
- "An order moves to PENDING when the request is accepted, and to RELEASED when it is cancelled or expires" — passes.

### 4. The Platform Test

> "Is this detail about the platform or framework, rather than the system itself?"

If yes: exclude it.

**Examples:**
- "Uses Spring Boot's @Scheduled annotation with a 5-minute fixedDelay" — fails. Platform detail.
- "The system periodically fetches updated SMS templates" — passes. Behavioral fact.
- "Kafka consumer group rebalancing triggers a brief processing pause" — fails. Platform behavior.
- "The system processes events in parallel across multiple worker instances" — passes. Behavioral fact with operational implications.

---

## Borderline Cases

Some facts are genuinely ambiguous. These require judgment:

- **Database table names:** Include when the table name is the clearest way to identify a data store the reader needs to reason about (e.g., `entity_state`, `notification_block`). Exclude when the name is incidental.
- **Named error states:** Include when the status is externally visible or operationally significant (e.g., `FAILED` events trigger alerts). Exclude when it's purely internal.
- **External system names:** Include always. They are architectural actors, not implementation detail.
- **"Note:" vs. new sentence:** Use Note: when the caveat would interrupt the flow of the main paragraph. Use a new sentence when the caveat is equally important to the main fact.

When in doubt, exclude. The code executes; the doc does not. An omission is recoverable. A misleading inclusion is not.

# Curated Examples

These four excerpts illustrate the target voice, depth, and abstraction level for system-feature documentation. Each shows how to describe a process with enough detail to be useful, without slipping into implementation.

---

## Example 1: A Process Introduction That Establishes Context Without Over-Explaining

**Source:** "Invoice Reconciliation" feature document, Introduction section

> Invoice Reconciliation matches incoming carrier invoices against the usage
> records the system has already processed. It identifies discrepancies —
> missing charges, duplicate entries, and rate mismatches — so that the billing
> team can resolve them before payment.
>
> The process runs daily, triggered by the arrival of new invoice files from
> the carrier SFTP drop. It reads usage records from the rating engine's
> output store and produces a reconciliation report for each invoice. Unmatched
> items are flagged for manual review.
>
> - **Carrier SFTP** — delivers raw invoice files in CSV format
> - **Rating Engine** — provides the system's own usage records for comparison
> - **Billing Portal** — displays reconciliation reports and accepts resolutions

**What this shows:**

Three short paragraphs: what, how it fits, and who it talks to. The bullet list names the external actors and their roles without explaining protocols, authentication, or file formats. The reader now knows what this feature does, when it runs, and what it touches — enough context to understand the process sections that follow.

**What an agent typically writes instead:**

> The Invoice Reconciliation module is implemented in the `reconciliation-service` Spring Boot application. It is triggered by a cron job configured with `@Scheduled(cron = "0 0 6 * * *")` that polls the SFTP server at `sftp.carrier.example.com` using JSch. Invoice files are downloaded to a temporary directory and parsed using the `CsvInvoiceParser` class.

The agent version explains the technology stack instead of the business purpose. A reader learns about Spring Boot and JSch but not what reconciliation achieves or why it matters.

---

## Example 2: A Decision Point With Clear Conditions and Paths

**Source:** "Order Fulfilment" feature document, Validation step

> ### Validation
>
> Each incoming order is validated before entering the fulfilment pipeline.
> Validation checks the order against the current product catalogue and the
> customer's account status.
>
> - If the order references a product that has been withdrawn, the order is
>   rejected with status INVALID and the customer is notified.
> - If the customer's account is suspended, the order is held with status
>   PENDING_REVIEW. It remains in this state until an operator either releases
>   or cancels it.
> - If both checks pass, the order moves to ACCEPTED and proceeds to
>   allocation.
>
> Orders that fail validation are not retried automatically. The customer must
> submit a new order after the underlying issue is resolved.

**What this shows:**

Three clear branches, each stating the condition and the outcome (including the resulting status). The final sentence covers what does *not* happen — no automatic retry — which is a fact the reader needs. There is no mention of which service performs the validation, what the API call looks like, or how the product catalogue is queried.

---

## Example 3: A Multi-Step Process With Intermediate State Changes

**Source:** "Claim Processing" feature document, Assessment section

> ### Initial Triage
>
> When a new claim arrives, the system assigns it a category based on the
> claim type and reported amount. Claims below the automatic threshold are
> routed directly to Auto-Assessment. Claims above the threshold, or those
> involving specific claim types (vehicle total loss, liability disputes), are
> routed to Manual Review.
>
> ### Auto-Assessment
>
> The system evaluates the claim against the policy terms and coverage limits.
> It calculates the eligible payout by applying the deductible, co-payment
> percentage, and any applicable caps. If the calculated payout is within the
> automatic approval limit, the claim moves to APPROVED and a payment
> instruction is generated. If the payout exceeds the limit, the claim is
> escalated to Manual Review.
>
> ### Manual Review
>
> An adjuster reviews the claim, the supporting documents, and the
> auto-assessment results (if any). The adjuster can approve, adjust the
> payout amount, request additional documentation, or deny the claim. Each
> action updates the claim status accordingly: APPROVED, ADJUSTED,
> PENDING_DOCUMENTS, or DENIED.

**What this shows:**

Three steps in execution order. Each states what enters the step, what happens, and what state the claim is in when it leaves. The routing logic in Triage is specific (threshold, named claim types) without stating the threshold value or the configuration key. Auto-Assessment describes the calculation in business terms (deductible, co-payment, caps) without formulas. Manual Review lists the possible actions and their corresponding statuses as a closed set.

**What an agent typically writes instead:**

> The `ClaimTriageService.categorize()` method checks if `claim.getAmount() < config.getAutoThreshold()` and if the claim type is not in the `MANUAL_REVIEW_TYPES` set. If both conditions are true, it sets `claim.setRoute(Route.AUTO)` and persists the claim. Otherwise, it sets `claim.setRoute(Route.MANUAL)`. The auto-assessment is performed by `AutoAssessor.assess(claim)` which loads the policy from the `policy_master` table and calculates the payout using `PayoutCalculator.calculate(policy, claim)`.

The agent version names classes, methods, configuration keys, and table names. The actual business logic — what the triage decides and why — is harder to extract from the implementation detail.

---

## Example 4: Failure Behaviour Described Concisely

**Source:** "Payment Processing" feature document, Failure Modes section

> ### Payment Gateway Timeout
>
> If the payment gateway does not respond within the configured timeout, the
> payment is marked as UNCERTAIN. The system schedules a status check to query
> the gateway for the transaction outcome. If the gateway confirms the payment
> succeeded, the status is updated to COMPLETED. If the gateway confirms
> failure or the status check itself times out after three attempts, the
> payment moves to FAILED and the order is released for re-payment.
>
> ### Insufficient Funds
>
> The gateway returns a decline. The payment is marked DECLINED and the
> customer is notified with the option to retry with a different payment
> method. The order remains reserved for 30 minutes before being released.

**What this shows:**

Two failure scenarios, each described as: trigger → system response → resolution. The timeout scenario includes a recovery flow (status check, three attempts) stated as behavioural fact without mentioning the scheduler, retry interval, or HTTP client configuration. The insufficient funds scenario is two sentences because that is all it needs.

---

## Key Patterns Across All Examples

1. Each process step states its trigger, action, and outcome
2. Decision points name their conditions and all resulting paths
3. State changes are explicit — the entity name and new status are stated
4. External systems are named; internal implementation is not
5. Failure and edge cases are proportional — one sentence if simple, a subsection if genuinely complex
6. The reader can follow the full lifecycle without consulting the source code

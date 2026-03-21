# Curated Examples

These four excerpts are taken verbatim from a real system overview. Each illustrates something that prose rules alone cannot fully convey. Study the voice, the sentence rhythm, and — most importantly — what is *absent*.

---

## Example 1: A Processing Rule Without Implementation Detail

**Source:** "Duplicate Event Filtering" section

> Both Network Attach and Data Traffic events may be filtered out early due to
> event duplication. Events are ignored if the previous event in the same
> category fulfills these criteria:
>
> - Identical country code (after MCC + MNC mapping)
> - Processed less than 24 hours ago
> - Status is COMPLETED (or not FAILED for unverified events)
>
> The typical source of duplicate events are Network Attach events being sent
> once or twice for 3G nodes (SGSN and VLR) and once for 4G nodes (MME). As
> 3G attach events are sent without waiting for a response, these are considered
> unverified (and more likely to be ignored). On a failed attach, the device is
> also likely to retry later with the same or another operator.

**What this shows:**

The criteria list states the *conditions* without explaining how they are evaluated. There is no mention of a database query, a timestamp comparison method, or an EventStatus enum. The second paragraph gives just enough context (why 3G events are special) to make the rule interpretable — without explaining the code that implements it.

**What an agent typically writes instead:**

> The system queries the `roaming_notification` table for the most recent event with the same MSISDN and country code. If an event is found with `processed_at` within the last 86400 seconds and status `COMPLETED` (or not `FAILED` for unverified events), the new event is marked `IGNORED`. The EventDeduplicationService handles this check before persisting the new event.

The agent version names the table, the column, the time constant, and the service class. None of this helps the reader understand the business rule — it only documents the implementation.

---

## Example 2: A Processing Sequence That Names External Systems Without Explaining Their Contracts

**Source:** "Country Verification" section

> For unverified (3G) **Network Attach Events**, the system performs a location
> verification check after successful subscriber lookup:
>
> 1. Query Core (via SIS/ETOPS) for the subscriber's current location
> 2. Map the returned MCC to a country code using the operator database
> 3. Compare the actual location with the event's reported country code
> 4. If there is a mismatch, the event is marked as FAILED and processing stops.
>
> This verification is required, as 3G nodes (SGSN and VLR) send network attach
> events without waiting for a successful (or failed) response.

**What this shows:**

Step 1 names the external system (SIS/ETOPS) and the action (query for current location) without explaining the HTTP call, the endpoint, or the response format. Step 2 names the mechanism (operator database) without naming the table or the lookup method. The justification for *why* verification is needed is present — as a single closing sentence, not a paragraph — because it's necessary for the reader to understand when this step applies.

**What an agent typically writes instead:**

> The system sends an HTTP GET request to the SIS/ETOPS location API endpoint `/api/v1/subscriber/{imsi}/location`. The response contains a JSON object with an `mcc` field. This MCC is passed to `CountryCodeResolver.resolve(mcc)` which looks up the country code in the `country_operator` database table. If the resolved country code doesn't match `event.getCountryCode()`, the event status is set to `FAILED` and the event is saved.

The agent version explains the HTTP contract, the JSON structure, the class name, and the method. The behavioral fact — "verify the location matches" — is buried.

---

## Example 3: A Complex Priority Rule as a Simple Ordered List

**Source:** "Message Priorities" section

> Messages are ordered by the following priority:
>
> 1. **FUP Status** - FUP (Fair Usage Policy) messages take priority over non-FUP messages
> 2. **Variant** - Messages matching the subscriber's roaming variant are preferred in this order:
>    - `RLH_PERM_ROAM` (highest priority variant)
>    - `EU_PERM_ROAM`
>    - `RLH_EXT`
>    - `RLH`
>    - `NULL` (i.e. default, lowest priority variant)
> 3. **Customer Type** - Exact matches have higher priority
> 4. **Subscription Type** - Exact matches have higher priority

**What this shows:**

A four-level priority system is conveyed entirely as an ordered list. The sub-list for Variant ordering makes the priority explicit without introducing a "score" or "weight" concept. Items 3 and 4 are stated as a single-clause fact; there is no prose explaining what "exact match" means because it is self-evident in context.

**What an agent typically writes instead:**

> The system uses a multi-criteria sorting algorithm to select the best matching message. First, FUP messages are ranked higher than non-FUP messages. Then, among messages with the same FUP status, those with a variant matching the subscriber's portfolio are preferred, using a priority order defined in the `MessageVariantPriority` enum: RLH_PERM_ROAM > EU_PERM_ROAM > RLH_EXT > RLH > NULL. If multiple messages still remain tied, customer type exact matches are preferred over None, and similarly for subscription type.

The agent version explains the algorithm narrative ("multi-criteria sorting", "ranked", "still remain tied") and names an enum class. The list format in the correct version is more readable and more precise.

---

## Example 4: A Short, Complete Section With No Over-Explanation

**Source:** "Returning to Home Network" section

> When a subscriber returns to their home country (i.e. no longer roaming), the
> following occurs:
>
> - The subscriber location record is deleted
> - All per-message-type timestamps are cleared
> - The next roaming event will trigger a fresh set of messages
>
> Duplicate "return home" events within the same session are ignored.

**What this shows:**

Three behavioral facts as bullets. No explanation of how the deletion works, which table is affected beyond what's already established, or what "per-message-type timestamps" look like in storage. The edge case (duplicate return-home events) is handled in a single sentence at the end — not a separate section, not a note, just a sentence.

**What an agent typically writes instead:**

> When the system detects a return-home event (data traffic event with the home MCC), it calls `SubscriberLocationService.clearLocation(msisdn)` which deletes the `subscriber_location` record and resets the `welcome_sent_at`, `data_sent_at`, `info_sent_at`, and `marketing_sent_at` columns to null. The `subscriber_location_history` record is kept for future revisit suppression. If a duplicate return-home event arrives, the system detects that no `subscriber_location` record exists and silently ignores it.

The agent version names the service, the method, four column names, and explains implementation details of the history table behavior. The correct version states the observable outcome only.

---

## Key Pattern Across All Examples

In every example, the correct version:
1. States what happens, not how it happens
2. Names external systems and operationally significant concepts, but not internal implementation names
3. Trusts the reader to infer implementation details they don't need
4. Handles edge cases with one sentence or clause, not a sub-section
5. Uses present tense, third person, no hedging

The agent version in each case is not wrong — it's just at the wrong level of abstraction.

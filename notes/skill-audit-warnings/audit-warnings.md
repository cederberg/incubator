---
drafted: 2026-05-21
updated: 2026-05-31
status: active
---

# Skill Warning Notes

## Audit Source

`npx skills` renders **Security Risk Assessments** from remote audit data. It
does not run local repository checks.

The cached `skills` package calls:

```text
https://add-skill.vercel.sh/audit?source=<owner>/<repo>&skills=<skill>[,<skill>...]
```

E.g, for a skill in this repository:

```bash
curl -sS 'https://add-skill.vercel.sh/audit?source=cederberg/incubator&skills=what-we-forgot'
```

## Cache Behavior

Audit results are cached remotely for weeks. A query on 2026-05-31 still
returned analysis timestamps from 2026-05-14 and 2026-05-20 after the latest
repository push.

No cache invalidation endpoint is known.

## Provider Mapping

- **Gen** — `ath`, shown on `skills.sh` as **Gen Agent Trust Hub**
- **Socket** — Socket alert count
- **Snyk** — Snyk risk label

The audit API returns provider fields and timestamps. It does not include the
full rationale. Previously noted provider detail pages returned broken or
unhelpful pages and have been removed from this note.

## Findings On 2026-05-31

### `what-we-forgot`

Cached API result:

- **Gen** — safe, analyzed 2026-05-14
- **Socket** — critical, 1 alert, score 90, analyzed 2026-05-14
- **Snyk** — low, analyzed 2026-05-14

The Socket alert is stale. The skill no longer asks the agent to resume work
autonomously. It now reviews project instructions and the current conversation,
then presents one checklist to the user.

### `investigate`

Cached API result:

- **Gen** — safe, analyzed 2026-05-14
- **Socket** — safe, 0 alerts, score 90, analyzed 2026-05-14
- **Snyk** — high, analyzed 2026-05-14

Known rationale:

- **W007** — The skill requires appending raw log lines, command output, and
  stack traces verbatim to a log file. Snyk treats this as possible secret
  reproduction.
- **W011** — The skill asks researchers to ingest user-provided URLs and
  supporting material. Snyk treats this as indirect prompt-injection exposure.

### `review-doc`

Cached API result:

- **Gen** — safe, analyzed 2026-05-14
- **Socket** — safe, 0 alerts, score 90, analyzed 2026-05-14
- **Snyk** — high, analyzed 2026-05-14

Known rationale:

The skill tells the agent to quote sub-agent findings verbatim. Snyk treats this
as possible reproduction of secrets from reviewed documents.

### `review-instructions`

Cached API result:

- **Gen** — safe, analyzed 2026-05-14
- **Socket** — safe, 0 alerts, score 90, analyzed 2026-05-14
- **Snyk** — high, analyzed 2026-05-14

Known rationale:

The skill launches a sub-agent to read user-provided files, then tells the main
agent to quote sub-agent text verbatim. Snyk treats this as possible secret
exfiltration.

### `review-session`

Cached API result:

- **Gen** — safe, analyzed 2026-05-20
- **Socket** — safe, 0 alerts, score 90, analyzed 2026-05-20
- **Snyk** — high, analyzed 2026-05-20

Known rationale:

The skill reads raw session transcripts and asks for direct quotes in the
report. Snyk treats this as possible reproduction of secrets from logs.

## Interpretation

These warnings are prompt-risk heuristics. They do not indicate npm dependency
vulnerabilities or malicious code in this repository.

The common pattern is verbatim reproduction of potentially sensitive material:
documents, raw logs, stack traces, command output, or session transcripts.

Mitigations should focus on explicit redaction and authorization rules, not
dependency updates.

## Actions

- [x] Modify `what-we-forgot` to present a checklist instead of resuming work.
- [ ] Re-check the audit API after the remote cache refreshes.
- [ ] Modify `investigate` with redaction and summarization rules.
- [ ] Modify `review-doc` with redaction and summarization rules.
- [ ] Modify `review-instructions` with redaction and summarization rules.
- [ ] Modify `review-session` with redaction and summarization rules.
- [ ] Re-check all flagged skills after mitigation changes.

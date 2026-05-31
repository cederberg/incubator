---
name: what-we-forgot
description: >
  Scans the current conversation from the beginning for missed instructions,
  unresolved work items, and forgotten ideas.
disable-model-invocation: true
allowed-tools: Read
---

- Re-scan the current conversation and initial instructions from the beginning
  for missed instructions and open threads.
- Include instructions that were missed, ignored, or only partly followed.
- Include unresolved work items, decisions, questions, and forgotten ideas.
- Build one unified numbered checklist with all findings.
- Exclude items that are completed or superseded.

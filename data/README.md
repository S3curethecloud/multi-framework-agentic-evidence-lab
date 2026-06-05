# Mock SOC 2 Evidence Dataset

**Status:** Phase 2 / Mock Dataset

This directory contains mock SOC 2-style policies, evidence, logs, and tickets for the Multi-Framework Agentic Evidence Lab.

The dataset is intentionally small, local, and read-only. It is designed for RAG, tool-calling, structured-output, human-review, and traceability exercises across LangChain, LangGraph, Strands, and ADK.

## Dataset boundary

- Mock evidence only.
- No customer data.
- No secrets or credentials.
- No live backend integration.
- No production control evidence.
- No SOC 2 certification claim.
- No assertion of production operating effectiveness.

## Required folders

```text
data/
  policies/
  evidence/
  logs/
  tickets/
```

## Intentional evidence gaps

The dataset includes deliberate deficiencies so the agent can identify incomplete or stale evidence:

- privileged access review is missing a reviewer identity;
- access review evidence contains stale review timing;
- MFA evidence conflicts with an IAM export for break-glass and contractor accounts;
- terminated-user removal evidence lacks complete closure proof;
- production deploy approval lacks a complete secondary approval chain;
- incident response policy exists, but no incident exercise evidence is included in Phase 2.

These gaps are meant to exercise retrieval, sufficiency scoring, confidence handling, and human-review routing.

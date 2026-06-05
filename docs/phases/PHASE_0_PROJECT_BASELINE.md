# Phase 0 - Project Baseline / Governance Boundary

**Status:** Implementation In Progress

## Goal

Create the repository baseline for a phase-gated, portfolio-grade comparison lab across LangChain, LangGraph, Strands, and ADK.

## Scope

Phase 0 may create:

- project README;
- agent instructions;
- architecture notes;
- governance notes;
- evaluation rubric;
- runbook;
- phase tracker;
- empty framework directories;
- empty shared/data/results directories;
- verification script.

## Non-scope

Phase 0 must not implement framework-specific agents.

Phase 0 must not add real customer evidence, credentials, production integrations, live backend calls, token issuance, authorization behavior, runtime session creation, provider mutation, Kubernetes mutation, production enforcement, or SOC 2 certification claims.

## Phase 0 verification command

```bash
python tools/verify_phase_0.py
```

## Expected verification output

The verification printout must show:

- all required baseline files present;
- all required directories present;
- forbidden claims absent;
- framework implementation files absent;
- phase tracker present;
- pass/fail summary.

## Evidence

Phase 0 evidence is recorded after the verification printout is clean and reviewed.

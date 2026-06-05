# Phase 0 - Project Baseline / Governance Boundary

**Status:** Evidence Recorded

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

## Verification command

```bash
python tools/verify_phase_0.py
```

## Verification result

Phase 0 verification passed after correcting the initial false-positive forbidden-claim scanner.

The scanner now checks positive unsafe claim patterns while allowing negative boundary wording such as statements that the lab must not claim certification or enforcement.

## Evidence

- Verification printout: `docs/verification/PHASE_0_VERIFICATION_PRINTOUT.txt`
- Required baseline files present: true
- Required directories present: true
- Forbidden positive-claim scan passed: true
- Framework implementation files absent before scoped phases: true

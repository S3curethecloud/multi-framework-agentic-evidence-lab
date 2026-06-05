# Phase 7 - Evaluation Harness / Comparison Matrix

**Status:** Phase 7 / Evidence Recorded

## Goal

Run a shared comparison harness across all four completed framework implementations and produce portfolio-ready comparison evidence.

## Scope

Phase 7 is evaluation-only. It does not add new agent implementations.

Phase 7 consumes existing Phase 3 through Phase 6 artifacts:

- `results/reports/langchain_report.json`
- `results/reports/langgraph_report.json`
- `results/reports/strands_report.json`
- `results/reports/adk_report.json`
- `results/traces/langchain_trace.json`
- `results/traces/langgraph_trace.json`
- `results/traces/strands_trace.json`
- `results/traces/adk_trace.json`

## Added artifacts

- `tools/run_framework_comparison.py`
- `tools/verify_phase_7.py`
- `results/framework_scores.json`
- `results/comparison_matrix.md`
- `results/executive_summary.md`
- `docs/verification/PHASE_7_VERIFICATION_PRINTOUT.txt`

## Evaluation dimensions

The comparison uses the shared rubric categories:

- setup speed
- RAG quality
- tool ergonomics
- state handling
- human review
- structured output
- observability
- failure handling
- portability
- production fit
- governance fit

## Claim boundary

This phase compares deterministic local lab implementations only.

It does not claim SOC 2 certification, independent audit completion, production operating effectiveness, live enforcement, authorization behavior, token issuance, runtime session creation, production deployment, or production control operation.

## Exit criteria

- [x] All four framework report artifacts exist
- [x] All four framework trace artifacts exist
- [x] Every framework has ten benchmark reports
- [x] Every framework has ten trace envelopes
- [x] Every report validates against the shared `AgentReport` schema
- [x] Every trace validates against the shared `TraceEnvelope` schema
- [x] `results/framework_scores.json` generated
- [x] `results/comparison_matrix.md` generated
- [x] `results/executive_summary.md` generated
- [x] Forbidden positive-claim scan passes
- [x] Phase 7 verification passes

## Evidence

- Phase 7 verification printout: `docs/verification/PHASE_7_VERIFICATION_PRINTOUT.txt`
- Framework scores: `results/framework_scores.json`
- Comparison matrix: `results/comparison_matrix.md`
- Executive summary: `results/executive_summary.md`

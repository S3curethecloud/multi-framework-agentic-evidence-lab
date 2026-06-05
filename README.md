# Multi-Framework Agentic Evidence Lab

**Status:** Phase 0 / Project Baseline

This repository compares LangChain, LangGraph, Strands, and ADK by implementing the same governed RAG evidence-review agent across all four frameworks.

The lab uses a mock SOC 2-style evidence dataset to evaluate framework support for:

- retrieval-augmented generation;
- tool calling;
- structured JSON output;
- stateful orchestration;
- human-review routing;
- observability;
- failure handling;
- framework comparison;
- governance-oriented AI architecture.

## Lab thesis

A controlled implementation of the same governed evidence-review workflow across four agent frameworks can show which framework best supports observable, human-reviewable, production-style agent workflows.

## Canonical workflow

```text
classify_question
  -> retrieve_evidence
  -> evaluate_evidence
  -> route_by_confidence
       -> human_review when confidence is below threshold
       -> generate_report when confidence is sufficient
  -> persist_trace
```

## Fair-comparison invariants

Every framework implementation must use the same:

| Invariant | Decision |
|---|---|
| Language | Python |
| Dataset | Mock SOC 2-style evidence folder |
| Workflow | classify -> retrieve -> evaluate -> human review -> report |
| Tools | search_evidence, summarize_document, score_evidence, generate_report |
| Output schema | Shared Pydantic / JSON schema |
| Benchmark questions | Shared question set |
| Trace envelope | Shared trace schema |
| Metrics | Shared scoring rubric |

## Phase model

Work proceeds through explicit phase gates. Each phase must end with a verification printout before the next phase begins.

| Phase | Name | Status |
|---|---|---|
| Phase 0 | Project Baseline / Governance Boundary | In progress |
| Phase 1 | Shared Foundation / Schemas / Tracing | Not started |
| Phase 2 | Mock SOC 2 Evidence Dataset | Not started |
| Phase 3 | LangChain Baseline Agent | Not started |
| Phase 4 | LangGraph Governed Workflow | Not started |
| Phase 5 | Strands Implementation | Not started |
| Phase 6 | ADK Implementation | Not started |
| Phase 7 | Evaluation Harness / Comparison Matrix | Not started |
| Phase 8 | Portfolio Packaging / Final README / Resume Bullets | Not started |

## Governance boundary

This repository is a learning and portfolio lab. It uses mock evidence only.

It does not claim SOC 2 certification, independent audit completion, production operating effectiveness, live enforcement, runtime authorization, token issuance, production deployment, or production control operation.

## Verification rule

Before moving from one phase to the next, run the phase verification printout and inspect:

- expected files;
- forbidden claims;
- missing phase artifacts;
- inconsistent status values;
- TODOs that block the next phase;
- framework parity issues.

## Current checkpoint

Phase 0 creates the baseline repository shape and governance boundary documents only. No framework implementation is added in Phase 0.

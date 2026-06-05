# Multi-Framework Agentic Evidence Lab

**Status:** Phase 8 / Evidence Recorded

This repository is a portfolio-grade comparison lab for agentic AI frameworks. It implements the same governed evidence-review workflow across LangChain, LangGraph, Strands, and ADK-style implementations, then evaluates each implementation with a shared dataset, schema, trace envelope, benchmark set, and scoring rubric.

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

## What this project demonstrates

- Shared schemas and typed report contracts
- Mock evidence ingestion and retrieval
- Tool-shaped agent workflows
- Deterministic structured outputs
- Human-review routing based on confidence and evidence gaps
- Trace logging for tool calls, workflow events, and review checkpoints
- Cross-framework benchmark execution
- Framework scoring and comparison artifacts
- Portfolio packaging and resume-ready project evidence

## Implemented frameworks

| Framework track | Implementation path | Report artifact | Trace artifact |
|---|---|---|---|
| LangChain baseline | `langchain_lab/` | `results/reports/langchain_report.json` | `results/traces/langchain_trace.json` |
| LangGraph governed workflow | `langgraph_lab/` | `results/reports/langgraph_report.json` | `results/traces/langgraph_trace.json` |
| Strands-style workflow | `strands_lab/` | `results/reports/strands_report.json` | `results/traces/strands_trace.json` |
| ADK-style workflow | `adk_lab/` | `results/reports/adk_report.json` | `results/traces/adk_trace.json` |

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

Every framework implementation uses the same:

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

## Results and portfolio artifacts

| Artifact | Purpose |
|---|---|
| `results/framework_scores.json` | Machine-readable framework score summary |
| `results/comparison_matrix.md` | Rubric-based comparison matrix |
| `results/executive_summary.md` | Executive summary of comparison findings |
| `results/portfolio_summary.md` | Recruiter/hiring-manager oriented project summary |
| `results/resume_bullets.md` | Resume bullet options based on completed implementation |
| `results/project_closure_report.md` | Final phase-gated project closure record |

## Run locally

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run each benchmark:

```bash
python -m langchain_lab.run_benchmark
python -m langgraph_lab.run_benchmark
python -m strands_lab.run_benchmark
python -m adk_lab.run_benchmark
```

Run comparison and final verification:

```bash
python tools/run_framework_comparison.py
python tools/verify_phase_8.py | tee docs/verification/PHASE_8_VERIFICATION_PRINTOUT.txt
```

## Phase model

Work proceeds through explicit phase gates. Each phase ends with a verification printout before the next phase begins.

| Phase | Name | Status |
|---|---|---|
| Phase 0 | Project Baseline / Governance Boundary | Closed |
| Phase 1 | Shared Foundation / Schemas / Tracing | Closed |
| Phase 2 | Mock SOC 2 Evidence Dataset | Closed |
| Phase 3 | LangChain Baseline Agent | Closed |
| Phase 4 | LangGraph Governed Workflow | Closed |
| Phase 5 | Strands Implementation | Closed |
| Phase 6 | ADK Implementation | Closed |
| Phase 7 | Evaluation Harness / Comparison Matrix | Closed |
| Phase 8 | Portfolio Packaging / Final README / Resume Bullets | Closed |

## Governance boundary

This repository is a learning and portfolio lab. It uses mock evidence only.

It does not claim SOC 2 certification, independent audit completion, production operating effectiveness, live enforcement, runtime authorization, token issuance, production deployment, or production control operation.

## Current checkpoint

Phase 8 packages the completed lab for portfolio review. All planned phases are complete and evidence has been recorded through phase verification printouts.

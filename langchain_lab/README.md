# LangChain Baseline Agent

**Status:** Phase 3 / LangChain Baseline Agent

This directory contains the first framework implementation for the lab.

The Phase 3 baseline is intentionally deterministic and local. It uses the
shared evidence loader, lexical retrieval, schema validation, and trace recorder
so it can run without API keys, live backends, production systems, or external
model calls.

## What it demonstrates

- Local evidence retrieval
- Tool-shaped workflow boundaries
- Structured `AgentReport` output
- Tool-call trace logging
- Confidence scoring
- Human-review routing
- Benchmark execution across the shared question set

## Files

| File | Purpose |
|---|---|
| `tools.py` | Tool-shaped functions for search, summarization, scoring, and report generation markers. |
| `agent.py` | Baseline agent orchestration and structured output generation. |
| `run_benchmark.py` | Runs all shared benchmark questions and writes reports/traces. |

## Run one question

```bash
python3 -m langchain_lab.agent --question "Is the evidence sufficient for access control?"
```

## Run the benchmark

```bash
python3 -m langchain_lab.run_benchmark
```

Outputs:

- `results/reports/langchain_report.json`
- `results/traces/langchain_trace.json`

## Boundary

This phase does not add LangGraph, Strands, or ADK implementations. It does not
claim SOC 2 certification, production operating effectiveness, live enforcement,
token issuance, authorization behavior, runtime sessions, provider mutation,
Kubernetes mutation, or SENTINEL bypass.

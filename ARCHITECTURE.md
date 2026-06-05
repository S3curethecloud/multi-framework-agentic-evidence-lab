# Architecture

## Purpose

This lab compares four agent frameworks by building the same governed evidence-review workflow across each implementation.

The architecture is intentionally split into shared, framework-specific, and results layers.

## Repository layers

```text
shared/          common schemas, document loading, retrieval, tracing, benchmark questions, evaluation
langchain_lab/   LangChain baseline implementation
langgraph_lab/   LangGraph stateful workflow implementation
strands_lab/     Strands implementation
adk_lab/         ADK implementation
data/            mock SOC 2-style evidence dataset
results/         reports, traces, screenshots, and framework comparison output
tools/           verification and local utility scripts
```

## Shared workflow contract

All frameworks must implement the same conceptual workflow:

```text
question
  -> classify_question
  -> search_evidence
  -> summarize_document
  -> score_evidence
  -> route_by_confidence
  -> optional_human_review
  -> generate_report
  -> write_trace
```

## Shared tool contract

Each framework implementation must expose equivalent tool behavior:

| Tool | Purpose |
|---|---|
| `search_evidence` | Retrieve relevant mock evidence records. |
| `summarize_document` | Summarize retrieved evidence without inventing facts. |
| `score_evidence` | Score sufficiency, risk, and confidence. |
| `generate_report` | Produce the shared JSON output schema. |

## Shared output contract

Every implementation must return the same report fields:

- question;
- answer;
- control_area;
- evidence_ids;
- evidence_summary;
- gaps;
- risk_level;
- confidence;
- human_review_required;
- recommended_next_action;
- tool_calls;
- failure_modes;
- framework.

## Comparison principle

Framework-specific code may differ, but dataset, schema, questions, trace envelope, and scoring rubric must remain shared. This keeps the lab a controlled engineering evaluation instead of four unrelated tutorials.

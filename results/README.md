# Results Artifacts

**Status:** Phase 8 / Evidence Recorded

This directory contains report, trace, comparison, and portfolio packaging artifacts for the completed lab.

## Framework reports

```text
results/reports/langchain_report.json
results/reports/langgraph_report.json
results/reports/strands_report.json
results/reports/adk_report.json
```

Each report contains ten structured `AgentReport` records using the shared schema.

## Framework traces

```text
results/traces/langchain_trace.json
results/traces/langgraph_trace.json
results/traces/strands_trace.json
results/traces/adk_trace.json
```

Each trace file contains ten `TraceEnvelope` records using the shared trace contract.

## Comparison artifacts

```text
results/framework_scores.json
results/comparison_matrix.md
results/executive_summary.md
```

These files compare the four framework implementations using the shared evaluation rubric.

## Portfolio artifacts

```text
results/portfolio_summary.md
results/resume_bullets.md
results/project_closure_report.md
```

These files package the completed lab for recruiter, hiring-manager, and portfolio review.

## Boundary

All result artifacts use mock evidence and deterministic local execution. They are not production operating evidence, an audit report, a certification claim, or proof of live enforcement.

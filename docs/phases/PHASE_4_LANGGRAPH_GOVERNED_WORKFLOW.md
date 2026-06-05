# Phase 4 - LangGraph Governed Workflow

**Status:** Evidence Recorded

## Goal

Implement an explicit governed workflow that demonstrates stateful orchestration, confidence routing, and human-review checkpoint behavior using the same dataset, schemas, tools, and benchmark questions as earlier phases.

## Scope

Phase 4 is limited to a local deterministic LangGraph-style implementation:

- explicit graph state;
- named graph nodes;
- confidence and gap routing;
- simulated human-review checkpoint;
- structured `AgentReport` output with `framework: langgraph`;
- trace output with node and route events;
- benchmark execution across the shared question set.

## Non-scope

Phase 4 does not add:

- Strands implementation;
- ADK implementation;
- live model/provider calls;
- production backend connection;
- token issuance;
- authorization behavior;
- runtime session creation;
- Kubernetes or provider mutation;
- live enforcement;
- SOC 2 certification claim;
- production operating-effectiveness claim.

## Workflow

```text
START
  -> load_corpus
  -> classify_question
  -> retrieve_evidence
  -> evaluate_evidence
  -> route_by_confidence
      -> human_review when confidence is low, gaps exist, or sufficiency is requested
      -> generate_report when confidence is sufficient and no gaps are detected
  -> generate_report
  -> END
```

## Files added

- `langgraph_lab/graph.py`
- `langgraph_lab/run_benchmark.py`
- `results/reports/langgraph_report.json`
- `results/traces/langgraph_trace.json`
- `tools/verify_phase_4.py`
- `docs/verification/PHASE_4_VERIFICATION_PRINTOUT.txt`

## Exit criteria

- [x] LangGraph-style workflow can run without API keys
- [x] Explicit graph state is present
- [x] Named graph nodes are present
- [x] Confidence routing is present
- [x] Simulated human-review checkpoint is present
- [x] Output validates against shared schema
- [x] Report contains framework value `langgraph`
- [x] Trace contains graph node and route events
- [x] No Strands or ADK implementation leakage is present
- [x] Forbidden positive-claim scan passes

## Evidence

- Phase 4 verification printout: `docs/verification/PHASE_4_VERIFICATION_PRINTOUT.txt`
- LangGraph report artifact: `results/reports/langgraph_report.json`
- LangGraph trace artifact: `results/traces/langgraph_trace.json`

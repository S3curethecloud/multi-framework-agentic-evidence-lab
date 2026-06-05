# LangGraph Lab

**Status:** Phase 4 / Evidence Recorded

This directory contains the governed workflow implementation for the Multi-Framework Agentic Evidence Lab.

The Phase 4 implementation is local and deterministic. It models LangGraph-style concepts without requiring API keys:

- explicit graph state;
- named workflow nodes;
- confidence-based routing;
- simulated human-review checkpoint;
- structured `AgentReport` output;
- trace events for node entry, routing, review, and report generation.

## Run

```bash
python3 -m langgraph_lab.run_benchmark
python3 tools/verify_phase_4.py | tee docs/verification/PHASE_4_VERIFICATION_PRINTOUT.txt
```

## Boundary

The workflow uses mock evidence only. It does not claim SOC 2 certification, production operating effectiveness, live enforcement, authorization, token issuance, or runtime control authority.

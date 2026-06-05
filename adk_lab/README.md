# ADK Lab

**Status:** Phase 6 / Evidence Recorded

This directory contains the local deterministic ADK-style implementation of the governed evidence-review workflow.

The implementation models ADK-style concepts without requiring API keys or live Google Cloud resources:

- explicit agent instructions;
- session state;
- registered tools;
- deterministic planner steps;
- human-review routing policy;
- shared `AgentReport` output;
- shared trace envelopes.

## Run

```bash
python3 -m adk_lab.run_benchmark
python3 tools/verify_phase_6.py
```

## Boundary

This lab uses mock evidence only. It does not create live agents, connect to cloud services, issue tokens, grant authorization, create runtime sessions, mutate infrastructure, claim SOC 2 certification, or prove production operating effectiveness.

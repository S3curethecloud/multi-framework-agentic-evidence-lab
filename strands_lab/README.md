# Strands Lab

**Status:** Phase 5 / Evidence Recorded

This directory contains the Phase 5 Strands-style implementation of the governed evidence-review workflow.

The implementation is local and deterministic. It models Strands-style agent ergonomics through:

- explicit agent instructions;
- a registered tool catalog;
- tool dispatch events;
- local evidence retrieval;
- structured `AgentReport` output;
- traceable human-review guardrail routing.

## Boundary

This phase does not call AWS services, create cloud resources, invoke production systems, issue credentials, grant authorization, create runtime sessions, or claim SOC 2 certification.

## Run

```bash
python3 -m strands_lab.run_benchmark
python3 tools/verify_phase_5.py | tee docs/verification/PHASE_5_VERIFICATION_PRINTOUT.txt
```

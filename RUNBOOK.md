# Runbook

**Status:** Phase 8 / Evidence Recorded

This runbook explains how to run the completed Multi-Framework Agentic Evidence Lab locally.

## 1. Prepare Python environment

Use a local virtual environment. Do not install dependencies into the system Python environment.

```bash
cd ~/multi-framework-agentic-evidence-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Run framework benchmarks

```bash
python -m langchain_lab.run_benchmark
python -m langgraph_lab.run_benchmark
python -m strands_lab.run_benchmark
python -m adk_lab.run_benchmark
```

Expected framework artifacts:

```text
results/reports/langchain_report.json
results/reports/langgraph_report.json
results/reports/strands_report.json
results/reports/adk_report.json
results/traces/langchain_trace.json
results/traces/langgraph_trace.json
results/traces/strands_trace.json
results/traces/adk_trace.json
```

## 3. Run comparison harness

```bash
python tools/run_framework_comparison.py
```

Expected comparison artifacts:

```text
results/framework_scores.json
results/comparison_matrix.md
results/executive_summary.md
```

## 4. Run final verification

```bash
python tools/verify_phase_8.py | tee docs/verification/PHASE_8_VERIFICATION_PRINTOUT.txt
```

Expected result:

```text
SUMMARY
RESULT: PASS
```

## 5. Review portfolio artifacts

```text
results/portfolio_summary.md
results/resume_bullets.md
results/project_closure_report.md
```

## Claim boundary

This is a deterministic portfolio lab using mock evidence. It does not claim SOC 2 certification, independent audit completion, production operating effectiveness, live enforcement, authorization behavior, token issuance, runtime session creation, production deployment, or production control operation.

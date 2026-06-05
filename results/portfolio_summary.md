# Portfolio Summary

**Project:** Multi-Framework Agentic Evidence Lab
**Status:** Complete through Phase 8 / Evidence Recorded

## One-line summary

Implemented and compared the same governed RAG evidence-review workflow across LangChain, LangGraph, Strands-style, and ADK-style agent frameworks using shared schemas, mock SOC 2-style evidence, structured outputs, human-review routing, traces, and a scoring matrix.

## Why this project exists

The project closes a hands-on implementation proof gap for roles requiring agent-framework experience. It turns AI trust, governance, and evidence architecture into a working multi-framework engineering artifact.

## Core capabilities demonstrated

- RAG over a controlled evidence corpus
- Tool-shaped agent workflows
- Structured JSON output validation
- Human-review routing
- Evidence sufficiency scoring
- Evidence-gap detection
- Trace envelope generation
- Deterministic benchmark execution
- Cross-framework comparison
- Portfolio-safe governance boundary language

## Framework coverage

| Track | Demonstrated capability |
|---|---|
| LangChain baseline | Fast baseline RAG, tool calls, structured output |
| LangGraph governed workflow | Explicit state, routing, human-review checkpoint, traceable branches |
| Strands-style workflow | Registered tools, autonomous-agent style dispatch, guardrail routing |
| ADK-style workflow | Session state, planner steps, app-oriented agent workflow |

## Key artifacts

| Artifact | Purpose |
|---|---|
| `shared/schemas.py` | Shared structured output and trace contracts |
| `shared/retrieval.py` | Shared retrieval helper for fair comparison |
| `data/` | Mock SOC 2-style evidence corpus |
| `results/reports/*.json` | Per-framework structured outputs |
| `results/traces/*.json` | Per-framework trace envelopes |
| `results/comparison_matrix.md` | Human-readable comparison matrix |
| `results/framework_scores.json` | Machine-readable framework scores |
| `results/executive_summary.md` | Executive interpretation |

## Practical conclusion

The strongest governed workflow fit in the current lab is LangGraph because it makes state transitions, confidence routing, and human-review checkpoints explicit.

LangChain is strongest as a baseline implementation track. Strands-style and ADK-style implementations demonstrate how equivalent tool and workflow behavior can be modeled with registered tool dispatch and session/planner concepts.

## Claim boundary

This is a deterministic portfolio lab using mock evidence. It does not claim SOC 2 certification, independent audit completion, production operating effectiveness, live enforcement, authorization behavior, token issuance, runtime session creation, production deployment, or production control operation.

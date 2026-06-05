# Framework Comparison Matrix

**Status:** Phase 7 / Evidence Recorded  
**Scope:** Deterministic local comparison of this repository's four framework implementations.  
**Boundary:** This matrix compares lab artifacts only. It does not claim SOC 2 certification, production operating effectiveness, live enforcement, runtime authorization, token issuance, or production control operation.

## Summary ranking

Ranked frameworks by total rubric score:

langgraph, adk, strands, langchain

## Artifact metrics

| Framework | Total score | Average score | Reports | Traces | Avg trace events | Avg tool calls | Human review rate |
|---|---|---|---|---|---|---|---|
| langchain | 45 | 4.09 | 10 | 10 | 7 | 7 | 0.5 |
| langgraph | 51 | 4.64 | 10 | 10 | 18.5 | 7.5 | 0.5 |
| strands | 47 | 4.27 | 10 | 10 | 17 | 9 | 0.8 |
| adk | 50 | 4.55 | 10 | 10 | 26 | 10 | 0.8 |

## Rubric score matrix

| Category | LangChain | LangGraph | Strands | ADK |
|---|---|---|---|---|
| setup_speed | 5 | 4 | 4 | 4 |
| rag_quality | 4 | 4 | 4 | 4 |
| tool_ergonomics | 4 | 4 | 5 | 4 |
| state_handling | 3 | 5 | 4 | 5 |
| human_review | 3 | 5 | 4 | 5 |
| structured_output | 5 | 5 | 5 | 5 |
| observability | 4 | 5 | 5 | 5 |
| failure_handling | 4 | 5 | 4 | 4 |
| portability | 5 | 4 | 4 | 4 |
| production_fit | 4 | 5 | 4 | 5 |
| governance_fit | 4 | 5 | 4 | 5 |

## Interpretation

- **LangChain** is the fastest baseline path and the easiest implementation to explain as a simple RAG/tool workflow.
- **LangGraph** is the strongest governed orchestration fit in this lab because state, routing, and simulated human review are explicit graph concepts.
- **Strands** is strongest for registered-tool and dispatch-style observability in this deterministic implementation.
- **ADK** is strongest alongside LangGraph for session-state visibility, planner-step traceability, and production-style workflow organization.

## Best-fit recommendations

| Use case | Best fit from lab evidence | Why |
|---|---|---|
| Fast prototype | LangChain | Lowest-complexity baseline implementation. |
| Governed workflow | LangGraph | Explicit state, node routing, and review checkpoint. |
| Tool-dispatch comparison | Strands | Strong registered-tool trace pattern. |
| Session/planner workflow | ADK | Explicit session state and planned tool execution. |
| Evidence-grade audit trail | LangGraph or ADK | Richest state and routing traces. |

## Evidence files consumed

- `results/reports/langchain_report.json`
- `results/reports/langgraph_report.json`
- `results/reports/strands_report.json`
- `results/reports/adk_report.json`
- `results/traces/langchain_trace.json`
- `results/traces/langgraph_trace.json`
- `results/traces/strands_trace.json`
- `results/traces/adk_trace.json`

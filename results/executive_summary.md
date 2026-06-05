# Executive Summary

**Status:** Phase 7 / Evidence Recorded

The Multi-Framework Agentic Evidence Lab now has four completed deterministic implementations of the same governed evidence-review workflow:

1. LangChain baseline agent
2. LangGraph governed workflow
3. Strands-style tool-dispatch agent
4. ADK-style session/planner agent

The comparison uses the same mock SOC 2-style dataset, benchmark questions, structured output schema, report format, and trace envelope for all four frameworks.

## Primary conclusion

The strongest governed workflow fit in this lab is **langgraph**, based on the current scoring model and artifact evidence.

LangGraph and ADK provide the strongest governance posture because their implementations make state, routing, review checkpoints, and traceability more explicit than the baseline workflow.

## Practical interpretation

- Use **LangChain** to demonstrate baseline RAG, tool calling, and structured outputs quickly.
- Use **LangGraph** to demonstrate stateful orchestration, branching, and human-review workflows.
- Use **Strands** to demonstrate registered tools, autonomous-agent style dispatch, and traceable tool execution.
- Use **ADK** to demonstrate app/session-oriented agent design, planner-step observability, and enterprise workflow structure.

## Portfolio value

This project now shows hands-on implementation across all four requested agent-framework patterns. It demonstrates:

- RAG over a controlled evidence corpus;
- structured JSON output;
- tool calling;
- human-review routing;
- trace logging;
- confidence and evidence-gap scoring;
- framework comparison using a shared benchmark harness.

## Claim boundary

This is a portfolio and readiness lab using mock evidence. It does not claim SOC 2 certification, independent audit completion, production operating effectiveness, live enforcement, authorization behavior, token issuance, runtime session creation, production deployment, or production control operation.

# Evaluation Rubric

Each framework receives a 1-5 score plus written justification. The written justification is more important than the numeric score.

| Category | What to measure |
|---|---|
| Setup speed | Time to first working agent. |
| RAG quality | Retrieval relevance and citation quality. |
| Tool ergonomics | How cleanly tools are defined and invoked. |
| State handling | Whether state is inspectable and controllable. |
| Human review | Whether approval gates are natural or awkward. |
| Structured output | Schema reliability and validation behavior. |
| Observability | Tool calls, latency, errors, branches, and decisions. |
| Failure handling | Retries, fallbacks, and incomplete-evidence handling. |
| Portability | Ease of switching model or provider. |
| Production fit | Testing, deployment, maintainability, and operational clarity. |
| Governance fit | Ability to prove what happened and why. |

## Benchmark question set

The shared benchmark question set will be finalized in Phase 1 and used unchanged across all four framework implementations.

Baseline questions:

1. Is the evidence sufficient for access control?
2. Which SOC 2 control area does this evidence support?
3. What evidence is missing?
4. Does this require human reviewer approval?
5. Generate an auditor-safe summary.
6. Identify conflicting or stale evidence.
7. What is the confidence score and why?
8. Which evidence item creates the highest risk?
9. Is the terminated user removal evidence complete?
10. Is the production deploy approval evidence sufficient?

## Scoring rule

A framework score is invalid unless the implementation uses the shared dataset, shared schema, shared question set, and shared trace envelope.

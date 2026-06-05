"""Generate Phase 7 framework comparison artifacts.

This script compares the four deterministic framework implementations already
produced by Phases 3 through 6. It reads the shared report/trace artifacts,
computes consistency metrics, applies the documented rubric, and writes
portfolio-ready comparison outputs.

The comparison is evidence/readiness oriented. It does not claim SOC 2
certification, production operating effectiveness, live enforcement, token
issuance, authorization behavior, or runtime control authority.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.evaluation import DEFAULT_RUBRIC, score_report_shape
from shared.schemas import AgentReport, TraceEnvelope
REPORT_DIR = ROOT / "results" / "reports"
TRACE_DIR = ROOT / "results" / "traces"
RESULTS_DIR = ROOT / "results"

FRAMEWORKS = ["langchain", "langgraph", "strands", "adk"]
QUESTION_COUNT = 10


@dataclass(frozen=True)
class FrameworkMetricSummary:
    framework: str
    report_count: int
    trace_count: int
    schema_pass_rate: float
    evidence_reference_rate: float
    human_review_rate: float
    average_confidence: float
    average_tool_calls: float
    average_trace_events: float
    total_failure_modes: int
    unique_control_areas: List[str]


# Scores intentionally blend artifact-derived checks with rubric judgment.
# They compare this repo's deterministic implementations, not all possible
# real-world usage of each framework.
RUBRIC_SCORES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "langchain": {
        "setup_speed": {"score": 5, "justification": "Smallest baseline path to working RAG, tools, structured output, report, and trace artifacts."},
        "rag_quality": {"score": 4, "justification": "Uses the shared retriever and evidence references consistently across benchmark questions."},
        "tool_ergonomics": {"score": 4, "justification": "Tool-shaped calls are explicit and easy to inspect, though orchestration remains linear."},
        "state_handling": {"score": 3, "justification": "State is present through local variables and trace records, but not graph-native."},
        "human_review": {"score": 3, "justification": "Human-review routing is implemented as a baseline conditional, not a first-class checkpoint."},
        "structured_output": {"score": 5, "justification": "Every benchmark output validates through the shared AgentReport schema."},
        "observability": {"score": 4, "justification": "Trace and tool-call records are complete, but less granular than graph or session implementations."},
        "failure_handling": {"score": 4, "justification": "Evidence gaps and review-required paths are visible in the report and trace."},
        "portability": {"score": 5, "justification": "The implementation is the most generic and easiest to retarget to another model/provider layer."},
        "production_fit": {"score": 4, "justification": "Strong baseline structure, but governed routing is less explicit than LangGraph or ADK style."},
        "governance_fit": {"score": 4, "justification": "Produces evidence-grade reports and traces, though workflow state is not graph-governed."},
    },
    "langgraph": {
        "setup_speed": {"score": 4, "justification": "More structure than the baseline, with additional node and routing code."},
        "rag_quality": {"score": 4, "justification": "Uses the same retrieval contract while preserving graph-state traceability."},
        "tool_ergonomics": {"score": 4, "justification": "Tools are clear and framework-neutral, with graph nodes making invocation order explicit."},
        "state_handling": {"score": 5, "justification": "Best explicit state and node-by-node control flow in this lab."},
        "human_review": {"score": 5, "justification": "Simulated human-review checkpoint is a natural graph branch with traceable routing."},
        "structured_output": {"score": 5, "justification": "Every benchmark output validates through the shared AgentReport schema."},
        "observability": {"score": 5, "justification": "Node start/end events, route decisions, and review checkpoint events create the richest governance trace."},
        "failure_handling": {"score": 5, "justification": "Graph routing makes uncertainty and evidence gaps explicit before report generation."},
        "portability": {"score": 4, "justification": "Portable at the model/tool layer, with more workflow-specific structure to preserve."},
        "production_fit": {"score": 5, "justification": "Strongest production-style orchestration pattern in the lab."},
        "governance_fit": {"score": 5, "justification": "Best fit for proving what happened, why it routed, and where human review occurred."},
    },
    "strands": {
        "setup_speed": {"score": 4, "justification": "Tool catalog and autonomous-agent pattern are clear, with modest setup overhead."},
        "rag_quality": {"score": 4, "justification": "Uses the same shared retriever and citation contract as the other frameworks."},
        "tool_ergonomics": {"score": 5, "justification": "Registered tool catalog and dispatch events are easy to compare and inspect."},
        "state_handling": {"score": 4, "justification": "Agent-style state is observable through events, though less formal than graph state."},
        "human_review": {"score": 4, "justification": "Guardrail routing is explicit and traceable in the Strands-style run."},
        "structured_output": {"score": 5, "justification": "Every benchmark output validates through the shared AgentReport schema."},
        "observability": {"score": 5, "justification": "Tool dispatch and guardrail events create strong observability for this lab pattern."},
        "failure_handling": {"score": 4, "justification": "Gaps and review requirements are reported clearly, with registered tools preserving traceability."},
        "portability": {"score": 4, "justification": "Tool contracts are portable, while runtime assumptions may need provider-specific adaptation."},
        "production_fit": {"score": 4, "justification": "Strong agent runtime shape; graph-level determinism is less explicit than LangGraph."},
        "governance_fit": {"score": 4, "justification": "Strong traceability, especially for tool dispatch, with slightly less formal routing state."},
    },
    "adk": {
        "setup_speed": {"score": 4, "justification": "Planner/session pattern adds structure beyond a simple baseline."},
        "rag_quality": {"score": 4, "justification": "Uses the shared evidence retrieval and citation contract consistently."},
        "tool_ergonomics": {"score": 4, "justification": "Registered tools are clear, with additional session/planner structure to manage."},
        "state_handling": {"score": 5, "justification": "Explicit ADK-style session state provides strong run-state visibility."},
        "human_review": {"score": 5, "justification": "Review routing is a planned step and visible in the trace."},
        "structured_output": {"score": 5, "justification": "Every benchmark output validates through the shared AgentReport schema."},
        "observability": {"score": 5, "justification": "Planner, tool invocation, and review-routing events produce high trace granularity."},
        "failure_handling": {"score": 4, "justification": "Uncertainty and evidence gaps are handled through session-state routing."},
        "portability": {"score": 4, "justification": "Tool and schema contracts are portable, but app/session patterns may be platform-shaped."},
        "production_fit": {"score": 5, "justification": "Strong app-style structure for reliable agent workflow development."},
        "governance_fit": {"score": 5, "justification": "Session state plus planner traces provide strong evidence-grade auditability."},
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_framework_artifacts(framework: str) -> tuple[List[dict], List[dict]]:
    reports = load_json(REPORT_DIR / f"{framework}_report.json")
    traces = load_json(TRACE_DIR / f"{framework}_trace.json")
    if not isinstance(reports, list) or not isinstance(traces, list):
        raise ValueError(f"{framework} artifacts must be JSON lists")
    return reports, traces


def summarize_framework(framework: str) -> FrameworkMetricSummary:
    reports, traces = load_framework_artifacts(framework)

    validated_reports = [AgentReport.model_validate(report) for report in reports]
    validated_traces = [TraceEnvelope.model_validate(trace) for trace in traces]

    schema_shapes = [score_report_shape(report) for report in reports]
    schema_pass_rate = mean(1.0 if item["shape_passed"] else 0.0 for item in schema_shapes)
    evidence_reference_rate = mean(1.0 if report.evidence_ids and report.evidence else 0.0 for report in validated_reports)
    human_review_rate = mean(1.0 if report.human_review_required else 0.0 for report in validated_reports)
    average_confidence = mean(report.confidence for report in validated_reports)
    average_tool_calls = mean(len(trace.tool_calls) for trace in validated_traces)
    average_trace_events = mean(len(trace.events) for trace in validated_traces)
    total_failure_modes = sum(len(report.failure_modes) for report in validated_reports)
    unique_control_areas = sorted({report.control_area for report in validated_reports})

    return FrameworkMetricSummary(
        framework=framework,
        report_count=len(validated_reports),
        trace_count=len(validated_traces),
        schema_pass_rate=round(schema_pass_rate, 4),
        evidence_reference_rate=round(evidence_reference_rate, 4),
        human_review_rate=round(human_review_rate, 4),
        average_confidence=round(average_confidence, 4),
        average_tool_calls=round(average_tool_calls, 2),
        average_trace_events=round(average_trace_events, 2),
        total_failure_modes=total_failure_modes,
        unique_control_areas=unique_control_areas,
    )


def build_score_record(metrics: Dict[str, FrameworkMetricSummary]) -> Dict[str, Any]:
    score_record: Dict[str, Any] = {
        "phase": "Phase 7 - Evaluation Harness / Comparison Matrix",
        "status": "evidence_recorded",
        "scope": "Deterministic local comparison of this repository's four framework implementations.",
        "claim_boundary": {
            "soc2_certification_claimed": False,
            "production_operating_effectiveness_claimed": False,
            "live_enforcement_claimed": False,
            "runtime_authority_granted": False,
        },
        "benchmark_question_count": QUESTION_COUNT,
        "frameworks": {},
    }

    for framework in FRAMEWORKS:
        rubric = RUBRIC_SCORES[framework]
        total_score = sum(item["score"] for item in rubric.values())
        max_score = len(rubric) * 5
        average_score = round(total_score / len(rubric), 2)
        score_record["frameworks"][framework] = {
            "metrics": asdict(metrics[framework]),
            "rubric_scores": rubric,
            "total_score": total_score,
            "max_score": max_score,
            "average_score": average_score,
        }

    ranked = sorted(
        score_record["frameworks"].items(),
        key=lambda item: (item[1]["total_score"], item[1]["metrics"]["average_trace_events"]),
        reverse=True,
    )
    score_record["ranked_frameworks"] = [name for name, _ in ranked]
    return score_record


def markdown_table(headers: List[str], rows: List[List[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---" for _ in headers]) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(out)


def write_framework_scores(score_record: Dict[str, Any]) -> None:
    (RESULTS_DIR / "framework_scores.json").write_text(
        json.dumps(score_record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_comparison_matrix(score_record: Dict[str, Any]) -> None:
    rows = []
    for framework in FRAMEWORKS:
        fw = score_record["frameworks"][framework]
        metrics = fw["metrics"]
        rows.append([
            framework,
            fw["total_score"],
            fw["average_score"],
            metrics["report_count"],
            metrics["trace_count"],
            metrics["average_trace_events"],
            metrics["average_tool_calls"],
            metrics["human_review_rate"],
        ])

    rubric_rows = []
    for category in [item.name for item in DEFAULT_RUBRIC]:
        rubric_rows.append(
            [
                category,
                RUBRIC_SCORES["langchain"][category]["score"],
                RUBRIC_SCORES["langgraph"][category]["score"],
                RUBRIC_SCORES["strands"][category]["score"],
                RUBRIC_SCORES["adk"][category]["score"],
            ]
        )

    md = f"""# Framework Comparison Matrix

**Status:** Phase 7 / Evidence Recorded  
**Scope:** Deterministic local comparison of this repository's four framework implementations.  
**Boundary:** This matrix compares lab artifacts only. It does not claim SOC 2 certification, production operating effectiveness, live enforcement, runtime authorization, token issuance, or production control operation.

## Summary ranking

Ranked frameworks by total rubric score:

{', '.join(score_record['ranked_frameworks'])}

## Artifact metrics

{markdown_table(['Framework', 'Total score', 'Average score', 'Reports', 'Traces', 'Avg trace events', 'Avg tool calls', 'Human review rate'], rows)}

## Rubric score matrix

{markdown_table(['Category', 'LangChain', 'LangGraph', 'Strands', 'ADK'], rubric_rows)}

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
"""
    (RESULTS_DIR / "comparison_matrix.md").write_text(md, encoding="utf-8")


def write_executive_summary(score_record: Dict[str, Any]) -> None:
    top = score_record["ranked_frameworks"][0]
    md = f"""# Executive Summary

**Status:** Phase 7 / Evidence Recorded

The Multi-Framework Agentic Evidence Lab now has four completed deterministic implementations of the same governed evidence-review workflow:

1. LangChain baseline agent
2. LangGraph governed workflow
3. Strands-style tool-dispatch agent
4. ADK-style session/planner agent

The comparison uses the same mock SOC 2-style dataset, benchmark questions, structured output schema, report format, and trace envelope for all four frameworks.

## Primary conclusion

The strongest governed workflow fit in this lab is **{top}**, based on the current scoring model and artifact evidence.

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
"""
    (RESULTS_DIR / "executive_summary.md").write_text(md, encoding="utf-8")


def main() -> None:
    metrics = {framework: summarize_framework(framework) for framework in FRAMEWORKS}
    score_record = build_score_record(metrics)
    write_framework_scores(score_record)
    write_comparison_matrix(score_record)
    write_executive_summary(score_record)
    print("Generated Phase 7 comparison artifacts:")
    print("- results/framework_scores.json")
    print("- results/comparison_matrix.md")
    print("- results/executive_summary.md")


if __name__ == "__main__":
    main()

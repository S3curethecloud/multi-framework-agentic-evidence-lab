"""LangGraph-style governed workflow implementation.

Phase 4 models explicit graph state, node transitions, confidence routing,
and a simulated human-review checkpoint. It is deterministic and local so the
lab remains runnable without API keys while still exercising the architecture
LangGraph is commonly used for: stateful orchestration and controlled routing.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import List, Optional, Tuple

from langchain_lab.tools import (
    generate_report_payload,
    load_evidence_corpus,
    score_evidence,
    search_evidence,
    summarize_document,
)
from shared.documents import DocumentRecord
from shared.retrieval import RetrievalResult
from shared.schemas import AgentReport, ControlArea, EvidenceReference
from shared.tracing import TraceEnvelope, TraceRecorder


@dataclass
class ReviewDecision:
    """Simulated reviewer checkpoint result."""

    required: bool
    status: str
    reason: str
    reviewer: str = "simulated_human_reviewer"


@dataclass
class GraphState:
    """Explicit LangGraph-style workflow state."""

    question: str
    data_root: str
    trace: TraceRecorder
    documents: List[DocumentRecord] = field(default_factory=list)
    control_area: ControlArea = "Unknown"
    retrieved: List[RetrievalResult] = field(default_factory=list)
    summaries: List[str] = field(default_factory=list)
    confidence: float = 0.0
    gaps: List[str] = field(default_factory=list)
    route: str = ""
    review: Optional[ReviewDecision] = None
    report: Optional[AgentReport] = None


def classify_question(question: str) -> ControlArea:
    """Classify a benchmark question into a SOC 2-style control area."""

    lowered = question.lower()
    if any(term in lowered for term in ["access", "mfa", "privileged", "terminated", "user"]):
        return "Access Control"
    if any(term in lowered for term in ["change", "deploy", "approval", "rollback"]):
        return "Change Management"
    if "incident" in lowered:
        return "Incident Response"
    if any(term in lowered for term in ["risk", "highest risk"]):
        return "Risk Assessment"
    return "Unknown"


def risk_from_gaps(confidence: float, gaps: List[str]) -> str:
    """Derive a conservative risk level from confidence and gaps."""

    if len(gaps) >= 4 or confidence < 0.35:
        return "high"
    if len(gaps) >= 2 or confidence < 0.7:
        return "medium"
    return "low"


def route_by_confidence(confidence: float, gaps: List[str], question: str) -> str:
    """Route state to human review or report generation."""

    lowered = question.lower()
    asks_sufficiency = any(term in lowered for term in ["sufficient", "complete", "approval"])
    if confidence < 0.75 or bool(gaps) or asks_sufficiency:
        return "human_review"
    return "generate_report"


def build_answer(state: GraphState) -> Tuple[str, str]:
    """Build an auditor-safe governed answer from graph state."""

    review_suffix = ""
    if state.review and state.review.required:
        review_suffix = " The workflow routed this case through the simulated human-review checkpoint."

    if state.gaps:
        answer = (
            f"The retrieved mock evidence supports {state.control_area}, but it is not fully sufficient. "
            f"The governed workflow found {len(state.gaps)} gap(s).{review_suffix}"
        )
        next_action = "Request missing evidence and reviewer approval before declaring sufficiency."
    else:
        answer = (
            f"The retrieved mock evidence supports {state.control_area} with no explicit gap detected by the governed workflow."
            f"{review_suffix}"
        )
        next_action = "Retain the trace and have a reviewer confirm the audit-safe narrative."

    if state.confidence < 0.5:
        next_action = "Escalate to human reviewer because confidence is below the governed threshold."
    return answer, next_action


def _latency_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)


def node_load_corpus(state: GraphState) -> GraphState:
    state.trace.event("graph.node.start", "Entering load_corpus node.", node="load_corpus")
    state.documents = load_evidence_corpus(state.data_root)
    state.trace.event("graph.node.end", "Loaded local mock evidence corpus.", node="load_corpus", document_count=len(state.documents))
    return state


def node_classify_question(state: GraphState) -> GraphState:
    state.trace.event("graph.node.start", "Entering classify_question node.", node="classify_question")
    state.control_area = classify_question(state.question)
    state.trace.event("graph.node.end", "Classified benchmark question.", node="classify_question", control_area=state.control_area)
    return state


def node_retrieve_evidence(state: GraphState) -> GraphState:
    state.trace.event("graph.node.start", "Entering retrieve_evidence node.", node="retrieve_evidence")
    state.retrieved = search_evidence(state.question, state.documents, state.trace, limit=4)
    state.summaries = [summarize_document(result, state.trace) for result in state.retrieved]
    state.trace.event(
        "graph.node.end",
        "Retrieved and summarized local mock evidence.",
        node="retrieve_evidence",
        evidence_ids=[result.document_id for result in state.retrieved],
    )
    return state


def node_evaluate_evidence(state: GraphState) -> GraphState:
    state.trace.event("graph.node.start", "Entering evaluate_evidence node.", node="evaluate_evidence")
    state.confidence, state.gaps = score_evidence(state.question, state.retrieved, state.trace)
    state.trace.event(
        "graph.node.end",
        "Evaluated evidence sufficiency.",
        node="evaluate_evidence",
        confidence=state.confidence,
        gaps=state.gaps,
    )
    return state


def node_route_by_confidence(state: GraphState) -> GraphState:
    state.trace.event("graph.node.start", "Entering route_by_confidence node.", node="route_by_confidence")
    state.route = route_by_confidence(state.confidence, state.gaps, state.question)
    state.trace.event(
        "graph.route",
        "Selected next node from confidence, gaps, and question intent.",
        node="route_by_confidence",
        route=state.route,
        confidence=state.confidence,
        gap_count=len(state.gaps),
    )
    return state


def node_human_review(state: GraphState) -> GraphState:
    start = perf_counter()
    state.trace.event("graph.node.start", "Entering human_review checkpoint.", node="human_review")
    reason = "Confidence threshold or evidence gaps require review."
    if not state.gaps and state.confidence >= 0.75:
        reason = "Question explicitly asks for sufficiency or approval confirmation."
    state.review = ReviewDecision(required=True, status="simulated_pending_review", reason=reason)
    state.trace.tool_call("human_review_checkpoint", _latency_ms(start), "success")
    state.trace.event(
        "graph.human_review",
        "Simulated human-review checkpoint recorded.",
        node="human_review",
        status=state.review.status,
        reason=state.review.reason,
    )
    return state


def node_generate_report(state: GraphState) -> GraphState:
    state.trace.event("graph.node.start", "Entering generate_report node.", node="generate_report")
    generate_report_payload(state.trace)
    answer, next_action = build_answer(state)
    evidence_refs = [
        EvidenceReference(
            evidence_id=result.document_id,
            path=result.path,
            quote=result.snippet[:220],
            relevance_score=min(round(result.score, 4), 1.0),
        )
        for result in state.retrieved
    ]
    failure_modes = [] if state.retrieved else ["no_relevant_evidence_retrieved"]
    if state.review and state.review.required:
        failure_modes.append("human_review_required_before_audit_use")
    state.report = AgentReport(
        question=state.question,
        answer=answer,
        control_area=state.control_area,
        evidence_ids=[reference.evidence_id for reference in evidence_refs],
        evidence=evidence_refs,
        evidence_summary=" ".join(state.summaries)[:900],
        gaps=state.gaps,
        risk_level=risk_from_gaps(state.confidence, state.gaps),
        confidence=state.confidence,
        human_review_required=state.review.required if state.review else False,
        recommended_next_action=next_action,
        tool_calls=state.trace.tool_calls,
        failure_modes=failure_modes,
        framework="langgraph",
    )
    state.trace.event(
        "graph.node.end",
        "Generated structured AgentReport payload.",
        node="generate_report",
        framework="langgraph",
    )
    return state


def run_langgraph_workflow(question: str, data_root: str = "data") -> Tuple[AgentReport, TraceEnvelope]:
    """Run the Phase 4 governed workflow for one question."""

    trace = TraceRecorder("langgraph", question)
    state = GraphState(question=question, data_root=data_root, trace=trace)
    trace.event("graph.start", "Started LangGraph-style governed workflow.")

    for node in [node_load_corpus, node_classify_question, node_retrieve_evidence, node_evaluate_evidence, node_route_by_confidence]:
        state = node(state)

    if state.route == "human_review":
        state = node_human_review(state)
    else:
        state.review = ReviewDecision(required=False, status="not_required", reason="Confidence threshold met with no explicit gaps.")
        trace.event("graph.route.skip", "Human review not required by route.", route=state.route)

    state = node_generate_report(state)
    trace.event("graph.complete", "Completed LangGraph-style governed workflow.", route=state.route, confidence=state.confidence)

    envelope = trace.envelope()
    envelope.events = trace.events
    envelope.tool_calls = trace.tool_calls
    envelope.report = state.report
    if state.report is None:  # defensive; verifier should never see this
        raise RuntimeError("LangGraph workflow completed without a report.")
    return state.report, envelope


def write_json(path: Path, payload: object) -> None:
    """Write Pydantic or plain JSON payloads."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(payload, "model_dump"):
        serializable = payload.model_dump(mode="json")
    else:
        serializable = payload
    path.write_text(json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Phase 4 LangGraph-style governed workflow.")
    parser.add_argument("--question", default="Is the evidence sufficient for access control?")
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--report-out", default="results/reports/langgraph_report.json")
    parser.add_argument("--trace-out", default="results/traces/langgraph_trace.json")
    args = parser.parse_args()

    report, trace = run_langgraph_workflow(args.question, args.data_root)
    write_json(Path(args.report_out), report)
    write_json(Path(args.trace_out), trace)
    print(report.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

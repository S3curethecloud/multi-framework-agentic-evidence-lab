"""Strands-style implementation for the governed evidence lab.

This phase models the ergonomics of an autonomous-agent SDK with explicit
agent instructions, a tool registry, local deterministic tool execution, and
structured output validation. It intentionally avoids API keys, network calls,
live AWS resources, runtime mutation, authorization, or enforcement behavior.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Callable, Dict, List, Tuple

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


@dataclass(frozen=True)
class StrandsTool:
    """Tool descriptor used by the local Strands-style agent runtime."""

    name: str
    description: str
    handler: Callable[..., object]


@dataclass
class StrandsRunContext:
    """Mutable run context shared across Strands-style tool invocations."""

    question: str
    data_root: str
    trace: TraceRecorder
    documents: List[DocumentRecord] = field(default_factory=list)
    retrieved: List[RetrievalResult] = field(default_factory=list)
    summaries: List[str] = field(default_factory=list)
    control_area: ControlArea = "Unknown"
    confidence: float = 0.0
    gaps: List[str] = field(default_factory=list)
    review_required: bool = False


class LocalStrandsAgent:
    """Small deterministic agent runtime with Strands-like tool registration."""

    def __init__(self, instructions: str, tools: List[StrandsTool]) -> None:
        self.instructions = instructions
        self.tools: Dict[str, StrandsTool] = {tool.name: tool for tool in tools}

    def invoke_tool(self, name: str, context: StrandsRunContext) -> object:
        """Invoke one registered tool by name and record agent-level events."""

        if name not in self.tools:
            raise KeyError(f"Unknown Strands tool: {name}")
        context.trace.event(
            "strands.tool.dispatch",
            "Dispatching registered Strands-style tool.",
            tool=name,
        )
        return self.tools[name].handler(context)

    def run(self, context: StrandsRunContext) -> Tuple[AgentReport, TraceEnvelope]:
        """Execute the local Strands-style plan."""

        context.trace.event(
            "strands.agent.start",
            "Started local Strands-style autonomous-agent workflow.",
            instruction_summary=self.instructions[:140],
            registered_tools=sorted(self.tools),
        )
        for tool_name in [
            "load_evidence_corpus",
            "classify_question",
            "search_evidence",
            "summarize_document",
            "score_evidence",
            "generate_report",
        ]:
            self.invoke_tool(tool_name, context)

        report = build_report(context)
        context.trace.event(
            "strands.agent.complete",
            "Completed local Strands-style workflow.",
            confidence=context.confidence,
            human_review_required=context.review_required,
        )
        envelope = context.trace.envelope()
        envelope.events = context.trace.events
        envelope.tool_calls = context.trace.tool_calls
        envelope.report = report
        return report, envelope


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
    """Derive a conservative risk level from confidence and gap count."""

    if len(gaps) >= 4 or confidence < 0.35:
        return "high"
    if len(gaps) >= 2 or confidence < 0.7:
        return "medium"
    return "low"


def review_required(confidence: float, gaps: List[str], question: str) -> bool:
    """Simulate a Strands guardrail that routes uncertainty to review."""

    lowered = question.lower()
    asks_sufficiency = any(term in lowered for term in ["sufficient", "complete", "approval"])
    asks_risk = any(term in lowered for term in ["highest risk", "missing", "conflicting", "stale"])
    return confidence < 0.75 or bool(gaps) or asks_sufficiency or asks_risk


def build_answer(context: StrandsRunContext) -> Tuple[str, str]:
    """Build an auditor-safe answer and recommended next action."""

    if context.gaps:
        answer = (
            f"The Strands-style agent retrieved mock evidence for {context.control_area}, "
            f"but found {len(context.gaps)} gap(s). The safe output is review-required, not audit-ready."
        )
        next_action = "Request missing evidence, then rerun the benchmark and retain the trace."
    else:
        answer = (
            f"The Strands-style agent retrieved mock evidence for {context.control_area} "
            "without detecting an explicit gap in the local dataset."
        )
        next_action = "Have a reviewer confirm the evidence narrative before portfolio use."

    if context.review_required:
        next_action = "Route to simulated human review before using the result in an audit narrative."
    return answer, next_action


def _latency_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)


def tool_load_evidence_corpus(context: StrandsRunContext) -> List[DocumentRecord]:
    start = perf_counter()
    context.documents = load_evidence_corpus(context.data_root)
    context.trace.tool_call("load_evidence_corpus", _latency_ms(start), "success")
    context.trace.event(
        "strands.tool.load_evidence_corpus",
        "Loaded local mock evidence corpus.",
        document_count=len(context.documents),
    )
    return context.documents


def tool_classify_question(context: StrandsRunContext) -> ControlArea:
    start = perf_counter()
    context.control_area = classify_question(context.question)
    context.trace.tool_call("classify_question", _latency_ms(start), "success")
    context.trace.event(
        "strands.tool.classify_question",
        "Classified benchmark question.",
        control_area=context.control_area,
    )
    return context.control_area


def tool_search_evidence(context: StrandsRunContext) -> List[RetrievalResult]:
    context.retrieved = search_evidence(context.question, context.documents, context.trace, limit=4)
    context.trace.event(
        "strands.tool.search_evidence.result",
        "Stored retrieval results in Strands run context.",
        evidence_ids=[result.document_id for result in context.retrieved],
    )
    return context.retrieved


def tool_summarize_document(context: StrandsRunContext) -> List[str]:
    context.summaries = [summarize_document(result, context.trace) for result in context.retrieved]
    context.trace.event(
        "strands.tool.summarize_document.result",
        "Summarized retrieved evidence snippets.",
        summary_count=len(context.summaries),
    )
    return context.summaries


def tool_score_evidence(context: StrandsRunContext) -> Tuple[float, List[str]]:
    context.confidence, context.gaps = score_evidence(context.question, context.retrieved, context.trace)
    context.review_required = review_required(context.confidence, context.gaps, context.question)
    context.trace.event(
        "strands.guardrail.review_route",
        "Applied Strands-style review guardrail.",
        confidence=context.confidence,
        gaps=context.gaps,
        human_review_required=context.review_required,
    )
    return context.confidence, context.gaps


def tool_generate_report(context: StrandsRunContext) -> None:
    generate_report_payload(context.trace)
    context.trace.event(
        "strands.tool.generate_report.result",
        "Prepared structured report generation marker.",
        framework="strands",
    )


def build_report(context: StrandsRunContext) -> AgentReport:
    """Create the shared AgentReport object from Strands run context."""

    answer, next_action = build_answer(context)
    evidence_refs = [
        EvidenceReference(
            evidence_id=result.document_id,
            path=result.path,
            quote=result.snippet[:220],
            relevance_score=min(round(result.score, 4), 1.0),
        )
        for result in context.retrieved
    ]
    failure_modes: List[str] = [] if context.retrieved else ["no_relevant_evidence_retrieved"]
    if context.review_required:
        failure_modes.append("human_review_required_before_audit_use")

    return AgentReport(
        question=context.question,
        answer=answer,
        control_area=context.control_area,
        evidence_ids=[reference.evidence_id for reference in evidence_refs],
        evidence=evidence_refs,
        evidence_summary=" ".join(context.summaries)[:900],
        gaps=context.gaps,
        risk_level=risk_from_gaps(context.confidence, context.gaps),
        confidence=context.confidence,
        human_review_required=context.review_required,
        recommended_next_action=next_action,
        tool_calls=context.trace.tool_calls,
        failure_modes=failure_modes,
        framework="strands",
    )


def build_strands_agent() -> LocalStrandsAgent:
    """Create the local deterministic Strands-style agent."""

    instructions = (
        "Evaluate mock SOC 2-style evidence using registered tools, preserve read-only boundaries, "
        "return structured AgentReport output, and route uncertainty to human review."
    )
    return LocalStrandsAgent(
        instructions=instructions,
        tools=[
            StrandsTool("load_evidence_corpus", "Load local mock evidence documents.", tool_load_evidence_corpus),
            StrandsTool("classify_question", "Classify the benchmark question.", tool_classify_question),
            StrandsTool("search_evidence", "Retrieve relevant mock evidence.", tool_search_evidence),
            StrandsTool("summarize_document", "Summarize retrieved evidence snippets.", tool_summarize_document),
            StrandsTool("score_evidence", "Score evidence sufficiency and identify gaps.", tool_score_evidence),
            StrandsTool("generate_report", "Emit structured report generation marker.", tool_generate_report),
        ],
    )


def run_strands_workflow(question: str, data_root: str = "data") -> Tuple[AgentReport, TraceEnvelope]:
    """Run the Phase 5 Strands-style implementation for one question."""

    trace = TraceRecorder("strands", question)
    context = StrandsRunContext(question=question, data_root=data_root, trace=trace)
    agent = build_strands_agent()
    return agent.run(context)


def write_json(path: str | Path, payload: object) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Phase 5 Strands-style agent for one question.")
    parser.add_argument("question", nargs="?", default="Is the evidence sufficient for access control?")
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--report-out", default="results/reports/strands_single_report.json")
    parser.add_argument("--trace-out", default="results/traces/strands_single_trace.json")
    args = parser.parse_args()

    report, trace = run_strands_workflow(args.question, data_root=args.data_root)
    write_json(args.report_out, report.model_dump(mode="json"))
    write_json(args.trace_out, trace.model_dump(mode="json"))
    print(f"Wrote report to {args.report_out}")
    print(f"Wrote trace to {args.trace_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

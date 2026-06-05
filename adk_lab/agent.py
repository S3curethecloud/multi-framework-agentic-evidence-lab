"""ADK-style implementation for the governed evidence lab.

This phase models Google ADK-style agent development with explicit session
state, instruction-driven planning, registered tools, deterministic local tool
execution, and structured output validation. It intentionally avoids API keys,
network calls, live Google Cloud resources, runtime mutation, authorization, or
enforcement behavior.
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
class AdkTool:
    """Tool descriptor for the local ADK-style agent runtime."""

    name: str
    description: str
    handler: Callable[["AdkSession"], object]


@dataclass
class AdkSession:
    """Mutable ADK-style session state shared across planner steps."""

    question: str
    data_root: str
    trace: TraceRecorder
    documents: List[DocumentRecord] = field(default_factory=list)
    retrieved: List[RetrievalResult] = field(default_factory=list)
    summaries: List[str] = field(default_factory=list)
    control_area: ControlArea = "Unknown"
    confidence: float = 0.0
    gaps: List[str] = field(default_factory=list)
    human_review_required: bool = False
    review_reason: str = ""


class LocalAdkAgent:
    """Small deterministic ADK-style agent with a declarative tool plan."""

    def __init__(self, name: str, instruction: str, tools: List[AdkTool]) -> None:
        self.name = name
        self.instruction = instruction
        self.tools: Dict[str, AdkTool] = {tool.name: tool for tool in tools}
        self.plan = [
            "load_evidence_corpus",
            "classify_question",
            "search_evidence",
            "summarize_document",
            "score_evidence",
            "route_human_review",
            "generate_report",
        ]

    def invoke_tool(self, tool_name: str, session: AdkSession) -> object:
        """Invoke a registered tool and emit ADK-style trace events."""

        if tool_name not in self.tools:
            raise KeyError(f"Unknown ADK tool: {tool_name}")
        session.trace.event(
            "adk.tool.invoke",
            "Invoking ADK-style registered tool.",
            agent=self.name,
            tool=tool_name,
        )
        return self.tools[tool_name].handler(session)

    def run(self, session: AdkSession) -> Tuple[AgentReport, TraceEnvelope]:
        """Execute the deterministic ADK-style plan."""

        session.trace.event(
            "adk.agent.start",
            "Started local ADK-style evidence-review workflow.",
            agent=self.name,
            instruction_summary=self.instruction[:160],
            plan=self.plan,
        )
        for step_number, tool_name in enumerate(self.plan, start=1):
            session.trace.event(
                "adk.planner.step",
                "Executing ADK-style planner step.",
                agent=self.name,
                step_number=step_number,
                tool=tool_name,
            )
            self.invoke_tool(tool_name, session)

        report = build_report(session)
        session.trace.event(
            "adk.agent.complete",
            "Completed local ADK-style workflow.",
            agent=self.name,
            confidence=session.confidence,
            human_review_required=session.human_review_required,
        )
        envelope = session.trace.envelope()
        envelope.events = session.trace.events
        envelope.tool_calls = session.trace.tool_calls
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


def should_route_to_review(confidence: float, gaps: List[str], question: str) -> Tuple[bool, str]:
    """Apply an ADK-style review policy for uncertain outputs."""

    lowered = question.lower()
    asks_sufficiency = any(term in lowered for term in ["sufficient", "complete", "approval"])
    asks_gap_review = any(term in lowered for term in ["missing", "conflicting", "stale", "highest risk"])
    if confidence < 0.75:
        return True, "Confidence is below the ADK review threshold."
    if gaps:
        return True, "Evidence gaps require simulated human review."
    if asks_sufficiency or asks_gap_review:
        return True, "Question asks for sufficiency, approval, gap, or risk judgment."
    return False, "No ADK review trigger matched."


def build_answer(session: AdkSession) -> Tuple[str, str]:
    """Build an auditor-safe answer and recommended next action."""

    review_suffix = ""
    if session.human_review_required:
        review_suffix = " The ADK-style workflow routed the output to simulated human review."

    if session.gaps:
        answer = (
            f"The ADK-style agent retrieved mock evidence for {session.control_area}, "
            f"but identified {len(session.gaps)} gap(s).{review_suffix}"
        )
        next_action = "Request missing evidence and reviewer confirmation before relying on the result."
    else:
        answer = (
            f"The ADK-style agent retrieved mock evidence for {session.control_area} "
            f"without detecting an explicit gap in the local benchmark corpus.{review_suffix}"
        )
        next_action = "Retain the trace and have a reviewer confirm the evidence narrative."

    if session.human_review_required:
        next_action = "Complete simulated human review before using this result in a portfolio narrative."
    return answer, next_action


def _latency_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)


def tool_load_evidence_corpus(session: AdkSession) -> List[DocumentRecord]:
    start = perf_counter()
    session.documents = load_evidence_corpus(session.data_root)
    session.trace.tool_call("load_evidence_corpus", _latency_ms(start), "success")
    session.trace.event(
        "adk.tool.load_evidence_corpus",
        "Loaded local mock evidence corpus.",
        document_count=len(session.documents),
    )
    return session.documents


def tool_classify_question(session: AdkSession) -> ControlArea:
    start = perf_counter()
    session.control_area = classify_question(session.question)
    session.trace.tool_call("classify_question", _latency_ms(start), "success")
    session.trace.event(
        "adk.tool.classify_question",
        "Classified benchmark question.",
        control_area=session.control_area,
    )
    return session.control_area


def tool_search_evidence(session: AdkSession) -> List[RetrievalResult]:
    session.retrieved = search_evidence(session.question, session.documents, session.trace, limit=4)
    session.trace.event(
        "adk.tool.search_evidence.result",
        "Stored retrieval results in ADK session state.",
        evidence_ids=[result.document_id for result in session.retrieved],
    )
    return session.retrieved


def tool_summarize_document(session: AdkSession) -> List[str]:
    session.summaries = [summarize_document(result, session.trace) for result in session.retrieved]
    session.trace.event(
        "adk.tool.summarize_document.result",
        "Summarized retrieved evidence snippets.",
        summary_count=len(session.summaries),
    )
    return session.summaries


def tool_score_evidence(session: AdkSession) -> Tuple[float, List[str]]:
    session.confidence, session.gaps = score_evidence(session.question, session.retrieved, session.trace)
    session.trace.event(
        "adk.tool.score_evidence.result",
        "Scored evidence sufficiency.",
        confidence=session.confidence,
        gaps=session.gaps,
    )
    return session.confidence, session.gaps


def tool_route_human_review(session: AdkSession) -> Tuple[bool, str]:
    start = perf_counter()
    session.human_review_required, session.review_reason = should_route_to_review(
        session.confidence,
        session.gaps,
        session.question,
    )
    session.trace.tool_call("human_review_checkpoint", _latency_ms(start), "success")
    session.trace.event(
        "adk.review.route",
        "Applied ADK-style human-review routing policy.",
        human_review_required=session.human_review_required,
        reason=session.review_reason,
        confidence=session.confidence,
        gap_count=len(session.gaps),
    )
    return session.human_review_required, session.review_reason


def tool_generate_report(session: AdkSession) -> None:
    generate_report_payload(session.trace)
    session.trace.event(
        "adk.tool.generate_report.result",
        "Prepared structured report generation marker.",
        framework="adk",
    )


def build_report(session: AdkSession) -> AgentReport:
    """Create the shared AgentReport object from ADK session state."""

    answer, next_action = build_answer(session)
    evidence_refs = [
        EvidenceReference(
            evidence_id=result.document_id,
            path=result.path,
            quote=result.snippet[:220],
            relevance_score=min(round(result.score, 4), 1.0),
        )
        for result in session.retrieved
    ]
    failure_modes: List[str] = [] if session.retrieved else ["no_relevant_evidence_retrieved"]
    if session.human_review_required:
        failure_modes.append("human_review_required_before_audit_use")

    return AgentReport(
        question=session.question,
        answer=answer,
        control_area=session.control_area,
        evidence_ids=[reference.evidence_id for reference in evidence_refs],
        evidence=evidence_refs,
        evidence_summary=" ".join(session.summaries)[:900],
        gaps=session.gaps,
        risk_level=risk_from_gaps(session.confidence, session.gaps),
        confidence=session.confidence,
        human_review_required=session.human_review_required,
        recommended_next_action=next_action,
        tool_calls=session.trace.tool_calls,
        failure_modes=failure_modes,
        framework="adk",
    )


def build_adk_agent() -> LocalAdkAgent:
    """Create the local deterministic ADK-style agent."""

    instruction = (
        "Evaluate mock SOC 2-style evidence using registered tools, maintain explicit session state, "
        "return structured AgentReport output, and route uncertainty to human review."
    )
    return LocalAdkAgent(
        name="local_adk_evidence_reviewer",
        instruction=instruction,
        tools=[
            AdkTool("load_evidence_corpus", "Load local mock evidence documents.", tool_load_evidence_corpus),
            AdkTool("classify_question", "Classify the benchmark question.", tool_classify_question),
            AdkTool("search_evidence", "Retrieve relevant mock evidence.", tool_search_evidence),
            AdkTool("summarize_document", "Summarize retrieved evidence snippets.", tool_summarize_document),
            AdkTool("score_evidence", "Score evidence sufficiency and identify gaps.", tool_score_evidence),
            AdkTool("route_human_review", "Apply human-review routing policy.", tool_route_human_review),
            AdkTool("generate_report", "Emit structured report generation marker.", tool_generate_report),
        ],
    )


def run_adk_workflow(question: str, data_root: str = "data") -> Tuple[AgentReport, TraceEnvelope]:
    """Run the Phase 6 ADK-style implementation for one question."""

    trace = TraceRecorder("adk", question)
    session = AdkSession(question=question, data_root=data_root, trace=trace)
    agent = build_adk_agent()
    return agent.run(session)


def write_json(path: str | Path, payload: object) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Phase 6 ADK-style agent for one question.")
    parser.add_argument("question", nargs="?", default="Is the evidence sufficient for access control?")
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--report-out", default="results/reports/adk_single_report.json")
    parser.add_argument("--trace-out", default="results/traces/adk_single_trace.json")
    args = parser.parse_args()

    report, trace = run_adk_workflow(args.question, data_root=args.data_root)
    write_json(args.report_out, report.model_dump(mode="json"))
    write_json(args.trace_out, trace.model_dump(mode="json"))
    print(f"Wrote report to {args.report_out}")
    print(f"Wrote trace to {args.trace_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

"""LangChain baseline agent implementation.

This phase implements the baseline workflow with local, deterministic tools so
it can be verified without API keys. The code is intentionally LangChain-shaped:
load corpus -> invoke tools -> validate structured output -> persist trace.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple

try:
    from shared.schemas import AgentReport, ControlArea, EvidenceReference
    from shared.tracing import TraceRecorder
except ImportError:  # pragma: no cover
    from schemas import AgentReport, ControlArea, EvidenceReference
    from tracing import TraceRecorder

try:
    from .tools import (
        generate_report_payload,
        load_evidence_corpus,
        score_evidence,
        search_evidence,
        summarize_document,
    )
except ImportError:  # pragma: no cover - direct script execution
    from tools import (
        generate_report_payload,
        load_evidence_corpus,
        score_evidence,
        search_evidence,
        summarize_document,
    )


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


def human_review_required(confidence: float, gaps: List[str], question: str) -> bool:
    """Route uncertain or explicitly sufficiency-oriented cases to review."""

    lowered = question.lower()
    asks_sufficiency = any(term in lowered for term in ["sufficient", "complete", "approval"])
    return confidence < 0.75 or bool(gaps) or asks_sufficiency


def build_answer(question: str, control_area: ControlArea, confidence: float, gaps: List[str]) -> Tuple[str, str]:
    """Build an auditor-safe answer and next action."""

    if gaps:
        answer = (
            f"The retrieved mock evidence supports {control_area}, but it is not fully sufficient. "
            f"The baseline found {len(gaps)} gap(s), so the safe conclusion is to require human review."
        )
        next_action = "Request missing evidence and reviewer approval before declaring sufficiency."
    else:
        answer = (
            f"The retrieved mock evidence supports {control_area} with no explicit gap detected by the baseline. "
            "A human reviewer should still confirm before using this in an audit narrative."
        )
        next_action = "Have a reviewer confirm evidence sufficiency and retain the trace."

    if confidence < 0.5:
        next_action = "Escalate to human reviewer because confidence is below the baseline threshold."
    return answer, next_action


def run_langchain_baseline(question: str, data_root: str = "data") -> Tuple[AgentReport, object]:
    """Run the Phase 3 LangChain baseline workflow for one question."""

    trace = TraceRecorder("langchain", question)
    trace.event("run.start", "Started LangChain baseline workflow.")

    documents = load_evidence_corpus(data_root)
    trace.event("corpus.loaded", "Loaded local mock evidence corpus.", document_count=len(documents))

    control_area = classify_question(question)
    trace.event("question.classified", "Classified benchmark question.", control_area=control_area)

    results = search_evidence(question, documents, trace, limit=4)
    summaries = [summarize_document(result, trace) for result in results]
    confidence, gaps = score_evidence(question, results, trace)
    generate_report_payload(trace)

    answer, next_action = build_answer(question, control_area, confidence, gaps)
    evidence_refs = [
        EvidenceReference(
            evidence_id=result.document_id,
            path=result.path,
            quote=result.snippet[:220],
            relevance_score=min(round(result.score, 4), 1.0),
        )
        for result in results
    ]
    report = AgentReport(
        question=question,
        answer=answer,
        control_area=control_area,
        evidence_ids=[reference.evidence_id for reference in evidence_refs],
        evidence=evidence_refs,
        evidence_summary=" ".join(summaries)[:900],
        gaps=gaps,
        risk_level=risk_from_gaps(confidence, gaps),
        confidence=confidence,
        human_review_required=human_review_required(confidence, gaps, question),
        recommended_next_action=next_action,
        tool_calls=trace.tool_calls,
        failure_modes=[] if results else ["no_relevant_evidence_retrieved"],
        framework="langchain",
    )
    envelope = trace.envelope()
    envelope.report = report
    trace.event("run.complete", "Completed LangChain baseline workflow.", confidence=confidence)
    envelope.events = trace.events
    envelope.tool_calls = trace.tool_calls
    return report, envelope


def write_json(path: Path, payload: object) -> None:
    """Write Pydantic or plain JSON payloads."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(payload, "model_dump"):
        serializable = payload.model_dump(mode="json")
    else:
        serializable = payload
    path.write_text(json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Phase 3 LangChain baseline agent.")
    parser.add_argument("--question", default="Is the evidence sufficient for access control?")
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--report-out", default="results/reports/langchain_report.json")
    parser.add_argument("--trace-out", default="results/traces/langchain_trace.json")
    args = parser.parse_args()

    report, trace = run_langchain_baseline(args.question, args.data_root)
    write_json(Path(args.report_out), report)
    write_json(Path(args.trace_out), trace)
    print(report.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

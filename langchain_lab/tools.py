"""Tool-shaped helpers for the LangChain baseline phase.

The functions in this module are deliberately local and deterministic. They
model the tool boundaries that a LangChain agent would use while avoiding API
keys, network calls, live systems, or production evidence mutation.
"""

from __future__ import annotations

from time import perf_counter
from typing import Iterable, List, Tuple

try:
    from shared.documents import DocumentRecord, load_documents
    from shared.retrieval import RetrievalResult, search_documents
    from shared.tracing import TraceRecorder
except ImportError:  # pragma: no cover - direct execution convenience
    from documents import DocumentRecord, load_documents
    from retrieval import RetrievalResult, search_documents
    from tracing import TraceRecorder


def _latency_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)


def load_evidence_corpus(data_root: str = "data") -> List[DocumentRecord]:
    """Load the local mock evidence corpus."""

    return load_documents(data_root)


def search_evidence(
    question: str,
    documents: Iterable[DocumentRecord],
    trace: TraceRecorder,
    limit: int = 4,
) -> List[RetrievalResult]:
    """Tool: search local mock evidence for relevant material."""

    start = perf_counter()
    try:
        results = search_documents(question, documents, limit=limit)
        trace.tool_call("search_evidence", _latency_ms(start), "success")
        trace.event(
            "tool.search_evidence",
            "Retrieved local mock evidence.",
            result_count=len(results),
            evidence_ids=[result.document_id for result in results],
        )
        return results
    except Exception as exc:  # pragma: no cover - defensive trace path
        trace.tool_call("search_evidence", _latency_ms(start), "error", str(exc))
        trace.event("tool.search_evidence.error", str(exc))
        return []


def summarize_document(result: RetrievalResult, trace: TraceRecorder) -> str:
    """Tool: summarize one retrieved document snippet."""

    start = perf_counter()
    snippet = " ".join(result.snippet.replace("\n", " ").split())
    summary = snippet[:280]
    if len(snippet) > 280:
        summary = f"{summary}..."
    trace.tool_call("summarize_document", _latency_ms(start), "success")
    return summary


def score_evidence(question: str, results: List[RetrievalResult], trace: TraceRecorder) -> Tuple[float, List[str]]:
    """Tool: score evidence sufficiency and produce explicit gaps."""

    start = perf_counter()
    question_lower = question.lower()
    joined = "\n".join(result.snippet.lower() for result in results)
    gaps: List[str] = []

    if not results:
        gaps.append("No relevant evidence was retrieved from the mock dataset.")

    if "access" in question_lower or "mfa" in question_lower or "terminated" in question_lower:
        if "missing" in joined or "absent" in joined or "open" in joined:
            gaps.append("Access-control evidence contains missing, absent, or open items.")
        if "reviewer identity" in joined or "reviewer sign-off" in joined:
            gaps.append("Reviewer identity or reviewer sign-off is missing.")
        if "privileged group removal" in joined and "pending" in joined:
            gaps.append("Privileged access removal is pending confirmation.")
        if "conflicts" in joined or "conflict" in joined:
            gaps.append("MFA evidence conflicts with IAM export details.")
        if "contractor" in joined and "expiration date" in joined:
            gaps.append("Contractor account evidence is missing an expiration date.")

    if "change" in question_lower or "deploy" in question_lower or "approval" in question_lower:
        if "secondary approval" in joined and ("not recorded" in joined or "open question" in joined or "must be checked" in joined):
            gaps.append("Secondary approval status remains ambiguous.")
        if "rollback" not in joined:
            gaps.append("Rollback evidence was not retrieved.")

    if "incident" in question_lower:
        if "tabletop" in joined and "does not include" in joined:
            gaps.append("Incident-response tabletop exercise evidence is missing from the Phase 2 dataset.")
        elif "incident" in question_lower:
            gaps.append("No incident execution or tabletop exercise evidence was retrieved.")

    deduped_gaps = list(dict.fromkeys(gaps))
    top_score = max((result.score for result in results), default=0.0)
    confidence = min(0.92, 0.35 + min(top_score, 1.0) * 0.35 + max(0, len(results) - 1) * 0.05)
    confidence -= min(len(deduped_gaps) * 0.08, 0.35)
    confidence = max(0.05, round(confidence, 4))
    trace.tool_call("score_evidence", _latency_ms(start), "success")
    trace.event(
        "tool.score_evidence",
        "Scored evidence sufficiency.",
        confidence=confidence,
        gaps=deduped_gaps,
    )
    return confidence, deduped_gaps


def generate_report_payload(trace: TraceRecorder) -> None:
    """Tool marker for report generation.

    The actual schema object is created in ``agent.py`` so every framework can
    use the same shared Pydantic contract.
    """

    start = perf_counter()
    trace.tool_call("generate_report", _latency_ms(start), "success")
    trace.event("tool.generate_report", "Generated structured AgentReport payload.")

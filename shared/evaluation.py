"""Shared evaluation helpers for framework comparison."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class RubricCategory:
    """One evaluation dimension for the framework comparison matrix."""

    name: str
    question: str
    min_score: int = 1
    max_score: int = 5


DEFAULT_RUBRIC: List[RubricCategory] = [
    RubricCategory("setup_speed", "How fast is time to first working agent?"),
    RubricCategory("rag_quality", "How relevant are retrieved evidence and citations?"),
    RubricCategory("tool_ergonomics", "How cleanly are tools defined and invoked?"),
    RubricCategory("state_handling", "Is workflow state inspectable and controllable?"),
    RubricCategory("human_review", "Are approval gates natural and testable?"),
    RubricCategory("structured_output", "Is schema validation reliable?"),
    RubricCategory("observability", "Are tool calls, latency, branches, and failures traceable?"),
    RubricCategory("failure_handling", "Are retries, fallbacks, and uncertainty handled clearly?"),
    RubricCategory("portability", "Can the model or provider be switched cleanly?"),
    RubricCategory("production_fit", "Is the implementation maintainable and deployable?"),
    RubricCategory("governance_fit", "Can the run prove what happened and why?"),
]

REQUIRED_REPORT_KEYS = {
    "question",
    "answer",
    "control_area",
    "evidence_ids",
    "evidence_summary",
    "gaps",
    "risk_level",
    "confidence",
    "human_review_required",
    "recommended_next_action",
    "tool_calls",
    "failure_modes",
    "framework",
}


def missing_report_keys(report: Dict[str, Any]) -> List[str]:
    """Return required schema keys absent from a report-like dictionary."""

    return sorted(REQUIRED_REPORT_KEYS.difference(report.keys()))


def score_report_shape(report: Dict[str, Any]) -> Dict[str, Any]:
    """Perform lightweight schema-shape checks without requiring model imports."""

    missing = missing_report_keys(report)
    confidence = report.get("confidence")
    confidence_valid = isinstance(confidence, (float, int)) and 0 <= confidence <= 1
    return {
        "missing_keys": missing,
        "confidence_valid": confidence_valid,
        "shape_passed": not missing and confidence_valid,
    }

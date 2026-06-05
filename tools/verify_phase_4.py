"""Phase 4 verification for the LangGraph governed workflow."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "langgraph_lab/README.md",
    "langgraph_lab/graph.py",
    "langgraph_lab/run_benchmark.py",
    "docs/phases/PHASE_4_LANGGRAPH_GOVERNED_WORKFLOW.md",
    "docs/verification/PHASE_4_VERIFICATION_PRINTOUT.txt",
    "results/reports/langgraph_report.json",
    "results/traces/langgraph_trace.json",
    "tools/verify_phase_4.py",
]

SYNTAX_FILES = [
    "langgraph_lab/graph.py",
    "langgraph_lab/run_benchmark.py",
    "tools/verify_phase_4.py",
]

FORBIDDEN_POSITIVE_PATTERNS = [
    "soc 2 certified: true",
    "soc2 certified: true",
    "soc2_certified: true",
    "soc_2_certified: true",
    "type 2 certified: true",
    "independent audit completed: true",
    "production operating effectiveness proven: true",
    "live enforcement active: true",
    "production enforcement active: true",
    "tokens issued: true",
    "authorization granted: true",
    "runtime sessions created: true",
    "kubernetes mutation enabled: true",
    "provider mutation enabled: true",
    "sentinel bypass: true",
]

FUTURE_IMPLEMENTATION_GUARDS = [
    "strands_lab/agent.py",
    "strands_lab/run_benchmark.py",
    "adk_lab/agent.py",
    "adk_lab/run_benchmark.py",
]

REQUIRED_GRAPH_MARKERS = [
    "class GraphState",
    "def node_classify_question",
    "def node_retrieve_evidence",
    "def node_evaluate_evidence",
    "def node_route_by_confidence",
    "def node_human_review",
    "def node_generate_report",
    "def run_langgraph_workflow",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


EXCLUDED_SCAN_PARTS = {".git", "__pycache__", "verification"}


def all_project_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json"}:
            continue
        if any(part in EXCLUDED_SCAN_PARTS for part in path.parts):
            continue
        if path.name.startswith("verify_phase_"):
            continue
        yield path


def scan_forbidden_patterns(patterns: List[str]) -> List[str]:
    failures: List[str] = []
    for pattern in patterns:
        matches = []
        for path in all_project_files():
            try:
                content = read_text(path).lower()
            except UnicodeDecodeError:
                continue
            if pattern in content:
                matches.append(str(path.relative_to(ROOT)))
        if matches:
            failures.append(f"Forbidden positive claim found: {pattern} in {matches}")
    return failures


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    failures: List[str] = []
    lines: List[str] = []
    lines.append("PHASE 4 VERIFICATION PRINTOUT")
    lines.append("Project: Multi-Framework Agentic Evidence Lab")
    lines.append("Expected status: Phase 4 / LangGraph Governed Workflow")
    lines.append("")

    lines.append("REQUIRED FILES")
    for file_path in REQUIRED_FILES:
        path = ROOT / file_path
        if path.exists():
            lines.append(f"PASS file {file_path}")
        else:
            lines.append(f"FAIL missing file {file_path}")
            failures.append(f"Missing file: {file_path}")
    lines.append("")

    lines.append("PYTHON SYNTAX")
    for file_path in SYNTAX_FILES:
        path = ROOT / file_path
        try:
            ast.parse(read_text(path))
            lines.append(f"PASS syntax {file_path}")
        except Exception as exc:
            lines.append(f"FAIL syntax {file_path}: {exc}")
            failures.append(f"Syntax failed: {file_path}: {exc}")
    lines.append("")

    lines.append("GRAPH MARKERS")
    graph_text = read_text(ROOT / "langgraph_lab/graph.py") if (ROOT / "langgraph_lab/graph.py").exists() else ""
    for marker in REQUIRED_GRAPH_MARKERS:
        if marker in graph_text:
            lines.append(f"PASS graph marker {marker}")
        else:
            lines.append(f"FAIL missing graph marker {marker}")
            failures.append(f"Missing graph marker: {marker}")
    lines.append("")

    lines.append("LANGGRAPH REPORT ARTIFACT")
    try:
        reports = load_json("results/reports/langgraph_report.json")
        if isinstance(reports, list) and len(reports) == 10:
            lines.append("PASS langgraph report count 10")
        else:
            lines.append(f"FAIL langgraph report count {len(reports) if isinstance(reports, list) else 'not-list'}")
            failures.append("LangGraph report artifact must contain 10 reports")
        framework_values = {report.get("framework") for report in reports if isinstance(report, dict)}
        if framework_values == {"langgraph"}:
            lines.append("PASS all reports framework langgraph")
        else:
            lines.append(f"FAIL unexpected report framework values {sorted(framework_values)}")
            failures.append("Report framework values must all be langgraph")
        human_review_count = sum(1 for report in reports if report.get("human_review_required") is True)
        if human_review_count >= 1:
            lines.append(f"PASS human-review reports present {human_review_count}")
        else:
            lines.append("FAIL no human-review reports present")
            failures.append("At least one LangGraph report must require human review")
        required_tools = {"search_evidence", "summarize_document", "score_evidence", "generate_report"}
        observed_tools = set()
        for report in reports:
            for call in report.get("tool_calls", []):
                observed_tools.add(call.get("tool"))
        missing_tools = sorted(required_tools - observed_tools)
        if not missing_tools:
            lines.append("PASS required tools observed in reports")
        else:
            lines.append(f"FAIL missing tools {missing_tools}")
            failures.append(f"Missing required tools: {missing_tools}")
        if "human_review_checkpoint" in observed_tools:
            lines.append("PASS human_review_checkpoint tool observed")
        else:
            lines.append("FAIL human_review_checkpoint tool missing")
            failures.append("human_review_checkpoint tool must be observed")
    except Exception as exc:
        lines.append(f"FAIL could not inspect report artifact: {exc}")
        failures.append(f"Report inspection failed: {exc}")
    lines.append("")

    lines.append("LANGGRAPH TRACE ARTIFACT")
    try:
        traces = load_json("results/traces/langgraph_trace.json")
        if isinstance(traces, list) and len(traces) == 10:
            lines.append("PASS langgraph trace count 10")
        else:
            lines.append(f"FAIL langgraph trace count {len(traces) if isinstance(traces, list) else 'not-list'}")
            failures.append("LangGraph trace artifact must contain 10 traces")
        event_types = set()
        for trace in traces:
            for event in trace.get("events", []):
                event_types.add(event.get("event_type"))
        for required_event in ["graph.start", "graph.node.start", "graph.node.end", "graph.route", "graph.human_review", "graph.complete"]:
            if required_event in event_types:
                lines.append(f"PASS trace event {required_event}")
            else:
                lines.append(f"FAIL missing trace event {required_event}")
                failures.append(f"Missing trace event: {required_event}")
    except Exception as exc:
        lines.append(f"FAIL could not inspect trace artifact: {exc}")
        failures.append(f"Trace inspection failed: {exc}")
    lines.append("")

    lines.append("FUTURE FRAMEWORK GUARD")
    for file_path in FUTURE_IMPLEMENTATION_GUARDS:
        if (ROOT / file_path).exists():
            lines.append(f"FAIL future implementation present too early: {file_path}")
            failures.append(f"Future implementation present too early: {file_path}")
        else:
            lines.append(f"PASS future implementation not present yet: {file_path}")
    lines.append("")

    lines.append("FORBIDDEN POSITIVE CLAIM SCAN")
    forbidden_failures = scan_forbidden_patterns(FORBIDDEN_POSITIVE_PATTERNS)
    if forbidden_failures:
        for failure in forbidden_failures:
            lines.append(f"FAIL {failure}")
        failures.extend(forbidden_failures)
    else:
        lines.append("PASS no unsafe positive claim patterns found")
    lines.append("")

    lines.append("SUMMARY")
    if failures:
        for failure in failures:
            lines.append(f"ERROR {failure}")
        lines.append("RESULT: FAIL")
    else:
        lines.append("RESULT: PASS")

    print("\n".join(lines))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

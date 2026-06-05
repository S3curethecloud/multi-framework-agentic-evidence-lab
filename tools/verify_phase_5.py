"""Phase 5 verification for the Strands-style implementation."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "strands_lab/README.md",
    "strands_lab/agent.py",
    "strands_lab/run_benchmark.py",
    "docs/phases/PHASE_5_STRANDS_IMPLEMENTATION.md",
    "docs/verification/PHASE_5_VERIFICATION_PRINTOUT.txt",
    "results/reports/langchain_report.json",
    "results/traces/langchain_trace.json",
    "results/reports/langgraph_report.json",
    "results/traces/langgraph_trace.json",
    "results/reports/strands_report.json",
    "results/traces/strands_trace.json",
    "tools/verify_phase_5.py",
]

SYNTAX_FILES = [
    "strands_lab/agent.py",
    "strands_lab/run_benchmark.py",
    "tools/verify_phase_5.py",
]

REQUIRED_AGENT_MARKERS = [
    "class StrandsTool",
    "class StrandsRunContext",
    "class LocalStrandsAgent",
    "def build_strands_agent",
    "def run_strands_workflow",
    "def tool_search_evidence",
    "def tool_score_evidence",
    "def tool_generate_report",
]

REQUIRED_TOOL_NAMES = {
    "search_evidence",
    "summarize_document",
    "score_evidence",
    "generate_report",
}

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
    "adk_lab/agent.py",
    "adk_lab/run_benchmark.py",
]

EXCLUDED_SCAN_PARTS = {".git", "__pycache__", "verification"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    lines.append("PHASE 5 VERIFICATION PRINTOUT")
    lines.append("Project: Multi-Framework Agentic Evidence Lab")
    lines.append("Expected status: Phase 5 / Strands Implementation")
    lines.append("")

    lines.append("REQUIRED FILES")
    for file_path in REQUIRED_FILES:
        path = ROOT / file_path
        if path.exists():
            lines.append(f"PASS file {file_path}")
        else:
            lines.append(f"FAIL missing file {file_path}")
            failures.append(f"Missing required file: {file_path}")
    lines.append("")

    lines.append("PYTHON SYNTAX")
    for file_path in SYNTAX_FILES:
        path = ROOT / file_path
        try:
            ast.parse(read_text(path), filename=str(path))
            lines.append(f"PASS syntax {file_path}")
        except Exception as exc:
            lines.append(f"FAIL syntax {file_path}: {exc}")
            failures.append(f"Syntax failure: {file_path}: {exc}")
    lines.append("")

    lines.append("STRANDS IMPLEMENTATION MARKERS")
    agent_text = read_text(ROOT / "strands_lab/agent.py") if (ROOT / "strands_lab/agent.py").exists() else ""
    for marker in REQUIRED_AGENT_MARKERS:
        if marker in agent_text:
            lines.append(f"PASS marker {marker}")
        else:
            lines.append(f"FAIL missing marker {marker}")
            failures.append(f"Missing Strands marker: {marker}")
    lines.append("")

    lines.append("REPORT ARTIFACT")
    try:
        reports = load_json("results/reports/strands_report.json")
        if len(reports) == 10:
            lines.append("PASS strands report count 10")
        else:
            lines.append(f"FAIL strands report count {len(reports)}")
            failures.append("Strands report must contain 10 benchmark reports")
        frameworks = {report.get("framework") for report in reports}
        if frameworks == {"strands"}:
            lines.append("PASS report framework strands")
        else:
            lines.append(f"FAIL report framework values {sorted(frameworks)}")
            failures.append("All Strands reports must have framework=strands")
        for index, report in enumerate(reports):
            tool_names = {call.get("tool") for call in report.get("tool_calls", [])}
            missing_tools = sorted(REQUIRED_TOOL_NAMES.difference(tool_names))
            if missing_tools:
                failures.append(f"Report {index} missing required tool calls: {missing_tools}")
        if not any("Report " in failure for failure in failures):
            lines.append("PASS required tool calls present in all reports")
    except Exception as exc:
        lines.append(f"FAIL strands report artifact: {exc}")
        failures.append(f"Strands report artifact failure: {exc}")
    lines.append("")

    lines.append("TRACE ARTIFACT")
    try:
        traces = load_json("results/traces/strands_trace.json")
        if len(traces) == 10:
            lines.append("PASS strands trace count 10")
        else:
            lines.append(f"FAIL strands trace count {len(traces)}")
            failures.append("Strands trace must contain 10 benchmark traces")
        trace_frameworks = {trace.get("framework") for trace in traces}
        if trace_frameworks == {"strands"}:
            lines.append("PASS trace framework strands")
        else:
            lines.append(f"FAIL trace framework values {sorted(trace_frameworks)}")
            failures.append("All Strands traces must have framework=strands")
        dispatch_found = any(
            any(event.get("event_type") == "strands.tool.dispatch" for event in trace.get("events", []))
            for trace in traces
        )
        guardrail_found = any(
            any(event.get("event_type") == "strands.guardrail.review_route" for event in trace.get("events", []))
            for trace in traces
        )
        if dispatch_found:
            lines.append("PASS Strands tool dispatch events present")
        else:
            lines.append("FAIL missing Strands tool dispatch events")
            failures.append("Missing strands.tool.dispatch trace events")
        if guardrail_found:
            lines.append("PASS Strands review guardrail events present")
        else:
            lines.append("FAIL missing Strands review guardrail events")
            failures.append("Missing strands.guardrail.review_route trace events")
    except Exception as exc:
        lines.append(f"FAIL strands trace artifact: {exc}")
        failures.append(f"Strands trace artifact failure: {exc}")
    lines.append("")

    lines.append("PRIOR FRAMEWORK ARTIFACTS")
    for artifact in [
        "results/reports/langchain_report.json",
        "results/traces/langchain_trace.json",
        "results/reports/langgraph_report.json",
        "results/traces/langgraph_trace.json",
    ]:
        if (ROOT / artifact).exists():
            lines.append(f"PASS prior artifact present {artifact}")
        else:
            lines.append(f"FAIL missing prior artifact {artifact}")
            failures.append(f"Missing prior framework artifact: {artifact}")
    lines.append("")

    lines.append("FUTURE IMPLEMENTATION GUARD")
    for file_path in FUTURE_IMPLEMENTATION_GUARDS:
        path = ROOT / file_path
        if path.exists():
            lines.append(f"FAIL future implementation present too early: {file_path}")
            failures.append(f"Future implementation present too early: {file_path}")
        else:
            lines.append(f"PASS implementation not present yet: {file_path}")
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

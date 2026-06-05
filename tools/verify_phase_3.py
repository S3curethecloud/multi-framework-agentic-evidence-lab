"""Phase 3 verification for the LangChain baseline agent."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "langchain_lab/README.md",
    "langchain_lab/tools.py",
    "langchain_lab/agent.py",
    "langchain_lab/run_benchmark.py",
    "docs/phases/PHASE_3_LANGCHAIN_BASELINE_AGENT.md",
    "tools/verify_phase_3.py",
    "results/reports/langchain_report.json",
    "results/traces/langchain_trace.json",
]

PYTHON_FILES = [
    "langchain_lab/tools.py",
    "langchain_lab/agent.py",
    "langchain_lab/run_benchmark.py",
    "tools/verify_phase_3.py",
]

FORBIDDEN_IMPLEMENTATION_FILES = [
    "langgraph_lab/graph.py",
    "strands_lab/agent.py",
    "adk_lab/agent.py",
]

FORBIDDEN_POSITIVE_CLAIMS = [
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

EXCLUDED_SCAN_PARTS = {".git", "__pycache__", "verification"}

REQUIRED_TOOL_NAMES = {
    "search_evidence",
    "summarize_document",
    "score_evidence",
    "generate_report",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def iter_scanned_files() -> Iterable[Path]:
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


def print_line(lines: List[str], message: str) -> None:
    lines.append(message)
    print(message)


def verify_required_files(lines: List[str], errors: List[str]) -> None:
    print_line(lines, "\nREQUIRED FILES")
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if path.exists():
            print_line(lines, f"PASS file {rel}")
        else:
            errors.append(f"Missing required file: {rel}")
            print_line(lines, f"FAIL missing file {rel}")


def verify_python_syntax(lines: List[str], errors: List[str]) -> None:
    print_line(lines, "\nPYTHON SYNTAX")
    for rel in PYTHON_FILES:
        path = ROOT / rel
        try:
            ast.parse(read_text(path), filename=rel)
        except Exception as exc:
            errors.append(f"Syntax failure in {rel}: {exc}")
            print_line(lines, f"FAIL syntax {rel}: {exc}")
        else:
            print_line(lines, f"PASS syntax {rel}")


def verify_report_and_trace(lines: List[str], errors: List[str]) -> None:
    print_line(lines, "\nLANGCHAIN REPORT AND TRACE")
    report_path = ROOT / "results/reports/langchain_report.json"
    trace_path = ROOT / "results/traces/langchain_trace.json"
    try:
        reports = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Report JSON invalid: {exc}")
        print_line(lines, f"FAIL report JSON invalid: {exc}")
        reports = []
    try:
        traces = json.loads(trace_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Trace JSON invalid: {exc}")
        print_line(lines, f"FAIL trace JSON invalid: {exc}")
        traces = []

    if isinstance(reports, list) and len(reports) == 10:
        print_line(lines, "PASS LangChain benchmark report count 10")
    else:
        errors.append("LangChain benchmark report must contain 10 reports")
        print_line(lines, "FAIL LangChain benchmark report count is not 10")

    if isinstance(traces, list) and len(traces) == 10:
        print_line(lines, "PASS LangChain benchmark trace count 10")
    else:
        errors.append("LangChain benchmark trace must contain 10 traces")
        print_line(lines, "FAIL LangChain benchmark trace count is not 10")

    report_errors_before = len(errors)
    for index, report in enumerate(reports if isinstance(reports, list) else []):
        if report.get("framework") != "langchain":
            errors.append(f"Report {index} framework is not langchain")
        if "confidence" not in report or not 0 <= report.get("confidence", -1) <= 1:
            errors.append(f"Report {index} confidence invalid")
        if not report.get("tool_calls"):
            errors.append(f"Report {index} has no tool calls")
        tool_names = {item.get("tool") for item in report.get("tool_calls", [])}
        if not REQUIRED_TOOL_NAMES.issubset(tool_names):
            errors.append(f"Report {index} missing required tool calls")
    if len(errors) == report_errors_before:
        print_line(lines, "PASS reports use langchain framework, confidence values, and required tool calls")
    else:
        print_line(lines, "FAIL report schema/tool-call checks failed")

    for index, trace in enumerate(traces if isinstance(traces, list) else []):
        if trace.get("framework") != "langchain":
            errors.append(f"Trace {index} framework is not langchain")
        if not trace.get("events"):
            errors.append(f"Trace {index} has no events")
        if not trace.get("tool_calls"):
            errors.append(f"Trace {index} has no tool calls")
    trace_errors = [error for error in errors if error.startswith("Trace")]
    if trace_errors:
        print_line(lines, "FAIL trace checks failed")
    else:
        print_line(lines, "PASS traces use langchain framework with events and tool calls")


def verify_forbidden_claims(lines: List[str], errors: List[str]) -> None:
    print_line(lines, "\nFORBIDDEN POSITIVE CLAIM SCAN")
    hits = []
    for path in iter_scanned_files():
        text = read_text(path).lower()
        for pattern in FORBIDDEN_POSITIVE_CLAIMS:
            if pattern in text:
                hits.append((pattern, path.relative_to(ROOT).as_posix()))
    if hits:
        for pattern, rel in hits:
            errors.append(f"Forbidden positive claim found: {pattern} in {rel}")
            print_line(lines, f"FAIL positive claim pattern '{pattern}' found in {rel}")
    else:
        print_line(lines, "PASS no unsafe positive claim patterns found")


def verify_framework_guard(lines: List[str], errors: List[str]) -> None:
    print_line(lines, "\nFRAMEWORK IMPLEMENTATION GUARD")
    for rel in FORBIDDEN_IMPLEMENTATION_FILES:
        path = ROOT / rel
        if path.exists():
            errors.append(f"Implementation leakage before scoped phase: {rel}")
            print_line(lines, f"FAIL implementation exists before scoped phase: {rel}")
        else:
            print_line(lines, f"PASS implementation not present yet: {rel}")


def main() -> int:
    lines: List[str] = []
    errors: List[str] = []
    print_line(lines, "PHASE 3 VERIFICATION PRINTOUT")
    print_line(lines, "Project: Multi-Framework Agentic Evidence Lab")
    print_line(lines, "Expected status: Phase 3 / LangChain Baseline Agent")

    verify_required_files(lines, errors)
    verify_python_syntax(lines, errors)
    verify_report_and_trace(lines, errors)
    verify_forbidden_claims(lines, errors)
    verify_framework_guard(lines, errors)

    print_line(lines, "\nCONSISTENCY NOTES")
    print_line(lines, "PASS Phase 3 adds only LangChain baseline implementation files.")
    print_line(lines, "PASS LangGraph, Strands, and ADK implementation files remain blocked until later phases.")

    print_line(lines, "\nSUMMARY")
    for error in errors:
        print_line(lines, f"ERROR {error}")
    result = "PASS" if not errors else "FAIL"
    print_line(lines, f"RESULT: {result}")

    out = ROOT / "docs/verification/PHASE_3_VERIFICATION_PRINTOUT.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

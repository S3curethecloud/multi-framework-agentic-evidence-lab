#!/usr/bin/env python3
"""Phase 8 verifier for portfolio packaging and final closure."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "RUNBOOK.md",
    "results/README.md",
    "docs/phases/PHASE_TRACKER.md",
    "docs/phases/PHASE_8_PORTFOLIO_PACKAGING_FINAL_README.md",
    "results/portfolio_summary.md",
    "results/resume_bullets.md",
    "results/project_closure_report.md",
    "results/framework_scores.json",
    "results/comparison_matrix.md",
    "results/executive_summary.md",
    "tools/verify_phase_8.py",
]

FRAMEWORKS = ["langchain", "langgraph", "strands", "adk"]

EXPECTED_PHASE_DOCS = [
    "docs/phases/PHASE_0_PROJECT_BASELINE.md",
    "docs/phases/PHASE_1_SHARED_FOUNDATION.md",
    "docs/phases/PHASE_2_MOCK_SOC2_EVIDENCE_DATASET.md",
    "docs/phases/PHASE_3_LANGCHAIN_BASELINE_AGENT.md",
    "docs/phases/PHASE_4_LANGGRAPH_GOVERNED_WORKFLOW.md",
    "docs/phases/PHASE_5_STRANDS_IMPLEMENTATION.md",
    "docs/phases/PHASE_6_ADK_IMPLEMENTATION.md",
    "docs/phases/PHASE_7_EVALUATION_HARNESS_COMPARISON_MATRIX.md",
    "docs/phases/PHASE_8_PORTFOLIO_PACKAGING_FINAL_README.md",
]

EXPECTED_VERIFICATION_FILES = [
    f"docs/verification/PHASE_{idx}_VERIFICATION_PRINTOUT.txt" for idx in range(0, 9)
]

UNSAFE_PATTERNS = [
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

SCAN_SUFFIXES = {".md", ".json", ".txt", ".py"}
SKIP_PARTS = {".git", ".venv", "__pycache__"}
SKIP_FILES = {
    "tools/verify_phase_0.py",
    "tools/verify_phase_1.py",
    "tools/verify_phase_2.py",
    "tools/verify_phase_3.py",
    "tools/verify_phase_4.py",
    "tools/verify_phase_5.py",
    "tools/verify_phase_6.py",
    "tools/verify_phase_7.py",
    "tools/verify_phase_8.py",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def record(lines: list[str], ok: bool, message: str, errors: list[str]) -> None:
    lines.append(("PASS " if ok else "FAIL ") + message)
    if not ok:
        errors.append(message)


def read_json(path: str):
    with (ROOT / path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def scan_for_unsafe_positive_claims() -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = rel(path)
        if relative in SKIP_FILES:
            continue
        if relative.startswith("docs/verification/"):
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for pattern in UNSAFE_PATTERNS:
            if pattern in text:
                findings.append((relative, pattern))
    return findings


def main() -> int:
    lines: list[str] = []
    errors: list[str] = []

    lines.append("PHASE 8 VERIFICATION PRINTOUT")
    lines.append("Project: Multi-Framework Agentic Evidence Lab")
    lines.append("Expected status: Phase 8 / Portfolio Packaging / Final README / Resume Bullets")
    lines.append("")

    lines.append("REQUIRED FILES")
    for file_path in REQUIRED_FILES:
        record(lines, (ROOT / file_path).is_file(), f"file {file_path}", errors)

    lines.append("")
    lines.append("PHASE DOCUMENTS")
    for file_path in EXPECTED_PHASE_DOCS:
        record(lines, (ROOT / file_path).is_file(), f"phase document {file_path}", errors)

    lines.append("")
    lines.append("VERIFICATION PRINTOUTS")
    for file_path in EXPECTED_VERIFICATION_FILES:
        record(lines, (ROOT / file_path).is_file(), f"verification printout {file_path}", errors)

    lines.append("")
    lines.append("FRAMEWORK ARTIFACTS")
    for framework in FRAMEWORKS:
        report_path = f"results/reports/{framework}_report.json"
        trace_path = f"results/traces/{framework}_trace.json"
        record(lines, (ROOT / report_path).is_file(), f"report {report_path}", errors)
        record(lines, (ROOT / trace_path).is_file(), f"trace {trace_path}", errors)
        if (ROOT / report_path).is_file():
            try:
                report_data = read_json(report_path)
                record(lines, len(report_data) == 10, f"{framework} report count 10", errors)
            except Exception as exc:
                record(lines, False, f"{framework} report JSON readable: {exc}", errors)
        if (ROOT / trace_path).is_file():
            try:
                trace_data = read_json(trace_path)
                record(lines, len(trace_data) == 10, f"{framework} trace count 10", errors)
            except Exception as exc:
                record(lines, False, f"{framework} trace JSON readable: {exc}", errors)

    lines.append("")
    lines.append("COMPARISON ARTIFACTS")
    try:
        scores = read_json("results/framework_scores.json")
        score_frameworks = set(scores.get("framework_scores", {}).keys())
        if not score_frameworks:
            score_frameworks = set(scores.get("frameworks", {}).keys())
        record(lines, score_frameworks == set(FRAMEWORKS), "framework_scores contains all four frameworks", errors)
    except Exception as exc:
        record(lines, False, f"framework_scores readable: {exc}", errors)

    comparison_text = (ROOT / "results/comparison_matrix.md").read_text(encoding="utf-8") if (ROOT / "results/comparison_matrix.md").exists() else ""
    for framework in FRAMEWORKS:
        record(lines, framework in comparison_text.lower(), f"comparison matrix mentions {framework}", errors)

    lines.append("")
    lines.append("PORTFOLIO ARTIFACTS")
    portfolio_text = (ROOT / "results/portfolio_summary.md").read_text(encoding="utf-8")
    resume_text = (ROOT / "results/resume_bullets.md").read_text(encoding="utf-8")
    closure_text = (ROOT / "results/project_closure_report.md").read_text(encoding="utf-8")
    record(lines, "portfolio-grade" in portfolio_text.lower() or "portfolio" in portfolio_text.lower(), "portfolio summary includes portfolio positioning", errors)
    record(lines, "resume" in resume_text.lower(), "resume bullets file includes resume positioning", errors)
    record(lines, "phase 0 through phase 8" in closure_text.lower(), "closure report records planned phase range", errors)

    lines.append("")
    lines.append("CLAIM BOUNDARY")
    unsafe_findings = scan_for_unsafe_positive_claims()
    if unsafe_findings:
        for file_path, pattern in unsafe_findings:
            record(lines, False, f"unsafe positive claim in {file_path}: {pattern}", errors)
    else:
        record(lines, True, "unsafe positive-claim scan clean", errors)

    lines.append("")
    lines.append("SUMMARY")
    if errors:
        for error in errors:
            lines.append(f"ERROR {error}")
        lines.append("RESULT: FAIL")
        print("\n".join(lines))
        return 1

    lines.append("RESULT: PASS")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())

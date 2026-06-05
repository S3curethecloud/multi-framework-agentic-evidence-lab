"""Verify Phase 7 comparison and evaluation artifacts."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.schemas import AgentReport, TraceEnvelope
FRAMEWORKS = ["langchain", "langgraph", "strands", "adk"]
QUESTION_COUNT = 10

REQUIRED_FILES = [
    "tools/run_framework_comparison.py",
    "tools/verify_phase_7.py",
    "docs/phases/PHASE_7_EVALUATION_HARNESS_COMPARISON_MATRIX.md",
    "results/framework_scores.json",
    "results/comparison_matrix.md",
    "results/executive_summary.md",
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def scan_text_files() -> List[Path]:
    files: List[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".txt", ".json"}:
            continue
        relative_parts = path.relative_to(ROOT).parts
        if relative_parts[0] == "tools" and path.name.startswith("verify_phase_"):
            continue
        if relative_parts[:2] == ("docs", "verification"):
            continue
        files.append(path)
    return files


def main() -> int:
    errors: List[str] = []
    print("PHASE 7 VERIFICATION PRINTOUT")
    print("Project: Multi-Framework Agentic Evidence Lab")
    print("Expected status: Phase 7 / Evaluation Harness")
    print()

    print("REQUIRED FILES")
    for item in REQUIRED_FILES:
        path = ROOT / item
        if path.exists():
            print(f"PASS file {item}")
        else:
            print(f"FAIL file {item}")
            errors.append(f"Missing required file: {item}")
    print()

    print("PYTHON SYNTAX")
    for item in ["tools/run_framework_comparison.py", "tools/verify_phase_7.py"]:
        path = ROOT / item
        if not path.exists():
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"))
            print(f"PASS syntax {item}")
        except SyntaxError as exc:
            print(f"FAIL syntax {item}: {exc}")
            errors.append(f"Syntax error in {item}: {exc}")
    print()

    print("FRAMEWORK ARTIFACT PARITY")
    for framework in FRAMEWORKS:
        report_path = ROOT / "results" / "reports" / f"{framework}_report.json"
        trace_path = ROOT / "results" / "traces" / f"{framework}_trace.json"
        if not report_path.exists():
            print(f"FAIL missing report {rel(report_path)}")
            errors.append(f"Missing report for {framework}")
            continue
        if not trace_path.exists():
            print(f"FAIL missing trace {rel(trace_path)}")
            errors.append(f"Missing trace for {framework}")
            continue

        reports = load_json(report_path)
        traces = load_json(trace_path)
        if len(reports) == QUESTION_COUNT:
            print(f"PASS {framework} report count {QUESTION_COUNT}")
        else:
            print(f"FAIL {framework} report count {len(reports)}")
            errors.append(f"Unexpected report count for {framework}")
        if len(traces) == QUESTION_COUNT:
            print(f"PASS {framework} trace count {QUESTION_COUNT}")
        else:
            print(f"FAIL {framework} trace count {len(traces)}")
            errors.append(f"Unexpected trace count for {framework}")

        for idx, report in enumerate(reports):
            try:
                parsed = AgentReport.model_validate(report)
                if parsed.framework != framework:
                    errors.append(f"Report {idx} framework mismatch for {framework}")
            except Exception as exc:  # noqa: BLE001 - verification should report all validation errors
                errors.append(f"Report {idx} validation failed for {framework}: {exc}")
        for idx, trace in enumerate(traces):
            try:
                parsed = TraceEnvelope.model_validate(trace)
                if parsed.framework != framework:
                    errors.append(f"Trace {idx} framework mismatch for {framework}")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Trace {idx} validation failed for {framework}: {exc}")
    print()

    print("COMPARISON OUTPUTS")
    scores = load_json(ROOT / "results" / "framework_scores.json") if (ROOT / "results" / "framework_scores.json").exists() else {}
    frameworks = scores.get("frameworks", {}) if isinstance(scores, dict) else {}
    ranked = scores.get("ranked_frameworks", []) if isinstance(scores, dict) else []
    for framework in FRAMEWORKS:
        if framework in frameworks:
            print(f"PASS score record {framework}")
        else:
            print(f"FAIL score record {framework}")
            errors.append(f"Missing score record for {framework}")
    if sorted(ranked) == sorted(FRAMEWORKS):
        print("PASS ranked framework list contains all frameworks")
    else:
        print("FAIL ranked framework list incomplete")
        errors.append("Ranked framework list incomplete")

    comparison = ROOT / "results" / "comparison_matrix.md"
    executive = ROOT / "results" / "executive_summary.md"
    if comparison.exists() and "Rubric score matrix" in comparison.read_text(encoding="utf-8"):
        print("PASS comparison matrix contains rubric section")
    else:
        print("FAIL comparison matrix missing rubric section")
        errors.append("Comparison matrix missing rubric section")
    if executive.exists() and "Primary conclusion" in executive.read_text(encoding="utf-8"):
        print("PASS executive summary contains primary conclusion")
    else:
        print("FAIL executive summary missing primary conclusion")
        errors.append("Executive summary missing primary conclusion")
    print()

    print("FORBIDDEN POSITIVE CLAIM SCAN")
    text_files = scan_text_files()
    for pattern in FORBIDDEN_POSITIVE_CLAIMS:
        hits = []
        for path in text_files:
            content = path.read_text(encoding="utf-8", errors="ignore").lower()
            if pattern in content:
                hits.append(rel(path))
        if hits:
            print(f"FAIL positive claim pattern '{pattern}' found in {hits}")
            errors.append(f"Forbidden positive claim found: {pattern}")
        else:
            print(f"PASS positive claim absent: {pattern}")
    print()

    print("IMPLEMENTATION SCOPE GUARD")
    expected_impls = [
        "langchain_lab/agent.py",
        "langgraph_lab/graph.py",
        "strands_lab/agent.py",
        "adk_lab/agent.py",
    ]
    for item in expected_impls:
        if (ROOT / item).exists():
            print(f"PASS existing implementation retained: {item}")
        else:
            print(f"FAIL missing implementation: {item}")
            errors.append(f"Missing existing implementation: {item}")
    print()

    print("SUMMARY")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

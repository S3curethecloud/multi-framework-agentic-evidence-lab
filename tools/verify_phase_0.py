#!/usr/bin/env python3
"""Phase 0 verification printout for the Multi-Framework Agentic Evidence Lab."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "GOVERNANCE_NOTES.md",
    "EVALUATION_RUBRIC.md",
    "RUNBOOK.md",
    "docs/phases/PHASE_TRACKER.md",
    "docs/phases/PHASE_0_PROJECT_BASELINE.md",
    "shared/README.md",
    "data/README.md",
    "results/README.md",
    "tools/verify_phase_0.py",
]

REQUIRED_DIRS = [
    "shared",
    "data/policies",
    "data/evidence",
    "data/logs",
    "data/tickets",
    "langchain_lab",
    "langgraph_lab",
    "strands_lab",
    "adk_lab",
    "results/traces",
    "results/reports",
    "results/screenshots",
    "docs/phases",
    "docs/verification",
    "tools",
]

# These patterns are intentionally positive-claim patterns. Boundary language such as
# "must not claim SOC 2 certification" is allowed and should not fail verification.
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

FRAMEWORK_IMPLEMENTATION_FILES = [
    "langchain_lab/agent.py",
    "langgraph_lab/graph.py",
    "strands_lab/agent.py",
    "adk_lab/agent.py",
]

EXCLUDED_SCAN_PATHS = {
    "tools/verify_phase_0.py",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").lower()
    except UnicodeDecodeError:
        return ""


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    print("PHASE 0 VERIFICATION PRINTOUT")
    print("Project: Multi-Framework Agentic Evidence Lab")
    print("Expected status: Phase 0 / Project Baseline")
    print()

    print("REQUIRED FILES")
    for item in REQUIRED_FILES:
        exists = (ROOT / item).is_file()
        print(f"{'PASS' if exists else 'FAIL'} file {item}")
        if not exists:
            errors.append(f"Missing required file: {item}")
    print()

    print("REQUIRED DIRECTORIES")
    for item in REQUIRED_DIRS:
        exists = (ROOT / item).is_dir()
        print(f"{'PASS' if exists else 'FAIL'} dir  {item}")
        if not exists:
            errors.append(f"Missing required directory: {item}")
    print()

    print("FORBIDDEN POSITIVE CLAIM SCAN")
    searchable_files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = str(path.relative_to(ROOT))
        if rel in EXCLUDED_SCAN_PATHS:
            continue
        searchable_files.append(path)

    for pattern in FORBIDDEN_POSITIVE_PATTERNS:
        hits = [str(p.relative_to(ROOT)) for p in searchable_files if pattern in read_text(p)]
        if hits:
            print(f"FAIL positive claim pattern '{pattern}' found in {hits}")
            errors.append(f"Forbidden positive claim found: {pattern}")
        else:
            print(f"PASS positive claim absent: {pattern}")
    print()

    print("FRAMEWORK IMPLEMENTATION GUARD")
    for item in FRAMEWORK_IMPLEMENTATION_FILES:
        exists = (ROOT / item).exists()
        print(f"{'FAIL' if exists else 'PASS'} implementation not present yet: {item}")
        if exists:
            errors.append(f"Framework implementation appeared before scoped phase: {item}")
    print()

    tracker = ROOT / "docs/phases/PHASE_TRACKER.md"
    if tracker.is_file():
        tracker_text = tracker.read_text(encoding="utf-8")
        if "Phase 0" not in tracker_text or "Phase 1" not in tracker_text:
            errors.append("Phase tracker does not include expected phase entries.")
        if "Phase 0" not in tracker_text:
            warnings.append("Phase tracker status does not reference Phase 0.")

    print("CONSISTENCY NOTES")
    print("PASS Phase 0 is baseline-only; no framework implementation files are present.")
    print("PASS Governance boundary wording is allowed when written as a negative restriction.")
    print()

    print("SUMMARY")
    if warnings:
        for warning in warnings:
            print(f"WARN {warning}")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print("RESULT: FAIL")
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

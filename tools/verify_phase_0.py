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

FORBIDDEN_CLAIMS = [
    "soc 2 certified",
    "soc2 certified",
    "type 2 certified",
    "independent audit completed",
    "production operating effectiveness proven",
    "live enforcement active",
    "production enforcement active",
    "tokens issued",
    "authorization granted",
    "runtime sessions created",
    "kubernetes mutation enabled",
    "provider mutation enabled",
    "sentinel bypass",
]

FRAMEWORK_IMPLEMENTATION_FILES = [
    "langchain_lab/agent.py",
    "langgraph_lab/graph.py",
    "strands_lab/agent.py",
    "adk_lab/agent.py",
]


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

    print("FORBIDDEN CLAIM SCAN")
    searchable_files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    for claim in FORBIDDEN_CLAIMS:
        hits = [str(p.relative_to(ROOT)) for p in searchable_files if claim in read_text(p)]
        if hits:
            print(f"FAIL claim '{claim}' found in {hits}")
            errors.append(f"Forbidden claim found: {claim}")
        else:
            print(f"PASS claim absent: {claim}")
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
        if "Phase 0 / Project Baseline In Progress" not in tracker_text:
            warnings.append("Phase tracker status does not exactly match expected Phase 0 status.")

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

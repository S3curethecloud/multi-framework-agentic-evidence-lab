#!/usr/bin/env python3
"""Verify Phase 1 shared foundation consistency."""

from __future__ import annotations

import ast
import py_compile
import re
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "requirements.txt",
    "shared/__init__.py",
    "shared/schemas.py",
    "shared/documents.py",
    "shared/retrieval.py",
    "shared/sample_questions.py",
    "shared/evaluation.py",
    "shared/tracing.py",
    "docs/phases/PHASE_1_SHARED_FOUNDATION.md",
    "tools/verify_phase_1.py",
]

REQUIRED_SCHEMA_MARKERS = [
    "class ToolCallRecord",
    "class EvidenceReference",
    "class AgentReport",
    "class TraceEvent",
    "class TraceEnvelope",
]

FRAMEWORK_IMPLEMENTATION_FILES = [
    "langchain_lab/agent.py",
    "langgraph_lab/graph.py",
    "strands_lab/agent.py",
    "adk_lab/agent.py",
]

FORBIDDEN_POSITIVE_CLAIM_PATTERNS = [
    re.compile(r"soc\s*2\s+certified\s*:\s*true", re.IGNORECASE),
    re.compile(r"soc2[_\s-]*certified\s*:\s*true", re.IGNORECASE),
    re.compile(r"type\s*2\s+certified\s*:\s*true", re.IGNORECASE),
    re.compile(r"independent\s+audit\s+completed\s*:\s*true", re.IGNORECASE),
    re.compile(r"production\s+operating\s+effectiveness\s+proven\s*:\s*true", re.IGNORECASE),
    re.compile(r"live\s+enforcement\s+active\s*:\s*true", re.IGNORECASE),
    re.compile(r"production\s+enforcement\s+active\s*:\s*true", re.IGNORECASE),
    re.compile(r"tokens\s+issued\s*:\s*true", re.IGNORECASE),
    re.compile(r"authorization\s+granted\s*:\s*true", re.IGNORECASE),
    re.compile(r"runtime\s+sessions\s+created\s*:\s*true", re.IGNORECASE),
    re.compile(r"kubernetes\s+mutation\s+enabled\s*:\s*true", re.IGNORECASE),
    re.compile(r"provider\s+mutation\s+enabled\s*:\s*true", re.IGNORECASE),
    re.compile(r"sentinel\s+bypass\s*:\s*true", re.IGNORECASE),
]

SCAN_SUFFIXES = {".md", ".py", ".json", ".txt"}
EXCLUDED_SCAN_PARTS = {".git", "__pycache__", "verification"}


def report(line: str) -> None:
    print(line)


def collect_text_files() -> List[Path]:
    files: List[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if any(part in EXCLUDED_SCAN_PARTS for part in path.parts):
            continue
        if path.name.startswith("verify_phase_"):
            continue
        files.append(path)
    return files


def count_benchmark_questions() -> int:
    source = (ROOT / "shared/sample_questions.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "BENCHMARK_QUESTIONS":
                    if isinstance(node.value, ast.List):
                        return len(node.value.elts)
    return 0


def main() -> int:
    errors: List[str] = []

    report("PHASE 1 VERIFICATION PRINTOUT")
    report("Project: Multi-Framework Agentic Evidence Lab")
    report("Expected status: Phase 1 / Shared Foundation")
    report("")

    report("REQUIRED FILES")
    for relpath in REQUIRED_FILES:
        path = ROOT / relpath
        if path.exists():
            report(f"PASS file {relpath}")
        else:
            report(f"FAIL missing file {relpath}")
            errors.append(f"Missing file: {relpath}")
    report("")

    report("PYTHON SYNTAX")
    for relpath in [p for p in REQUIRED_FILES if p.endswith(".py")]:
        path = ROOT / relpath
        try:
            py_compile.compile(str(path), doraise=True)
            report(f"PASS syntax {relpath}")
        except py_compile.PyCompileError as exc:
            report(f"FAIL syntax {relpath}: {exc.msg}")
            errors.append(f"Syntax failure: {relpath}")
    report("")

    report("SCHEMA MARKERS")
    schema_text = (ROOT / "shared/schemas.py").read_text(encoding="utf-8")
    for marker in REQUIRED_SCHEMA_MARKERS:
        if marker in schema_text:
            report(f"PASS schema marker {marker}")
        else:
            report(f"FAIL missing schema marker {marker}")
            errors.append(f"Missing schema marker: {marker}")
    report("")

    report("BENCHMARK QUESTION SET")
    question_count = count_benchmark_questions()
    if question_count >= 10:
        report(f"PASS benchmark questions count {question_count}")
    else:
        report(f"FAIL benchmark questions count {question_count}; expected at least 10")
        errors.append("Benchmark question count below 10")
    report("")

    report("FORBIDDEN POSITIVE CLAIM SCAN")
    scan_files = collect_text_files()
    for pattern in FORBIDDEN_POSITIVE_CLAIM_PATTERNS:
        matches = []
        for path in scan_files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if pattern.search(text):
                matches.append(path.relative_to(ROOT).as_posix())
        if matches:
            report(f"FAIL unsafe positive claim pattern found in {matches}")
            errors.append(f"Unsafe positive claim found in {matches}")
    if not any("Unsafe positive claim" in error for error in errors):
        report("PASS no unsafe positive claim patterns found")
    report("")

    report("FRAMEWORK IMPLEMENTATION GUARD")
    for relpath in FRAMEWORK_IMPLEMENTATION_FILES:
        if (ROOT / relpath).exists():
            report(f"FAIL framework implementation present before scoped phase: {relpath}")
            errors.append(f"Framework implementation present too early: {relpath}")
        else:
            report(f"PASS implementation not present yet: {relpath}")
    report("")

    report("SUMMARY")
    if errors:
        for error in errors:
            report(f"ERROR {error}")
        report("RESULT: FAIL")
        return 1
    report("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

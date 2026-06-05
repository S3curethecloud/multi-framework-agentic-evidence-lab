#!/usr/bin/env python3
"""Verify Phase 2 mock evidence dataset consistency."""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.documents import load_documents  # noqa: E402
from shared.retrieval import search_documents  # noqa: E402

REQUIRED_FILES = [
    "data/README.md",
    "data/policies/access_control_policy.md",
    "data/policies/change_management_policy.md",
    "data/policies/incident_response_policy.md",
    "data/evidence/mfa_rollout_evidence.md",
    "data/evidence/privileged_access_review.md",
    "data/evidence/terminated_user_access_removal.md",
    "data/evidence/production_deploy_approval.md",
    "data/logs/iam_sample_export.json",
    "data/logs/access_review_log.json",
    "data/logs/deployment_log.json",
    "data/tickets/jira_access_review_ticket.md",
    "data/tickets/change_approval_ticket.md",
    "docs/phases/PHASE_2_MOCK_SOC2_EVIDENCE_DATASET.md",
    "tools/verify_phase_2.py",
]

REQUIRED_IDENTIFIERS = [
    "POL-ACCESS-001",
    "POL-CHANGE-001",
    "POL-IR-001",
    "EV-ACCESS-MFA-001",
    "EV-ACCESS-PAR-001",
    "EV-ACCESS-TERM-001",
    "EV-CHANGE-DEPLOY-001",
    "LOG-IAM-001",
    "LOG-ACCESS-REVIEW-001",
    "LOG-DEPLOY-001",
    "SEC-2026-0412",
    "CHG-2026-0518",
]

REQUIRED_GAP_MARKERS = [
    "reviewer identity is missing",
    "approval timestamp is missing",
    "compensating control evidence missing",
    "contractor account is missing an expiration date",
    "Final privileged group removal confirmation is absent",
    "secondary approval was required",
    "tabletop exercise evidence",
]

FRAMEWORK_IMPLEMENTATION_FILES = [
    "langchain_lab/agent.py",
    "langgraph_lab/graph.py",
    "strands_lab/agent.py",
    "adk_lab/agent.py",
]

JSON_FILES = [
    "data/logs/iam_sample_export.json",
    "data/logs/access_review_log.json",
    "data/logs/deployment_log.json",
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


def all_dataset_text() -> str:
    parts: List[str] = []
    for relpath in REQUIRED_FILES:
        if not relpath.startswith("data/"):
            continue
        path = ROOT / relpath
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def main() -> int:
    errors: List[str] = []

    report("PHASE 2 VERIFICATION PRINTOUT")
    report("Project: Multi-Framework Agentic Evidence Lab")
    report("Expected status: Phase 2 / Mock SOC 2 Evidence Dataset")
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
    for relpath in ["tools/verify_phase_2.py"]:
        path = ROOT / relpath
        try:
            py_compile.compile(str(path), doraise=True)
            report(f"PASS syntax {relpath}")
        except py_compile.PyCompileError as exc:
            report(f"FAIL syntax {relpath}: {exc.msg}")
            errors.append(f"Syntax failure: {relpath}")
    report("")

    report("JSON VALIDITY")
    for relpath in JSON_FILES:
        try:
            json.loads((ROOT / relpath).read_text(encoding="utf-8"))
            report(f"PASS json {relpath}")
        except json.JSONDecodeError as exc:
            report(f"FAIL json {relpath}: {exc}")
            errors.append(f"Invalid JSON: {relpath}")
    report("")

    dataset_text = all_dataset_text()

    report("DATASET IDENTIFIERS")
    for marker in REQUIRED_IDENTIFIERS:
        if marker in dataset_text:
            report(f"PASS identifier {marker}")
        else:
            report(f"FAIL missing identifier {marker}")
            errors.append(f"Missing identifier: {marker}")
    report("")

    report("INTENTIONAL GAP MARKERS")
    lower_text = dataset_text.lower()
    for marker in REQUIRED_GAP_MARKERS:
        if marker.lower() in lower_text:
            report(f"PASS gap marker present: {marker}")
        else:
            report(f"FAIL missing gap marker: {marker}")
            errors.append(f"Missing gap marker: {marker}")
    report("")

    report("SHARED LOADER CHECK")
    documents = load_documents(ROOT / "data")
    if len(documents) >= 12:
        report(f"PASS loaded document count {len(documents)}")
    else:
        report(f"FAIL loaded document count {len(documents)}; expected at least 12")
        errors.append("Loaded document count below 12")
    kinds = {document.kind for document in documents}
    for required_kind in ["policy", "evidence", "log", "ticket"]:
        if required_kind in kinds:
            report(f"PASS document kind {required_kind}")
        else:
            report(f"FAIL missing document kind {required_kind}")
            errors.append(f"Missing document kind: {required_kind}")
    report("")

    report("RETRIEVAL SMOKE CHECK")
    access_results = search_documents("Is the evidence sufficient for access control?", documents, limit=5)
    access_paths = {result.path for result in access_results}
    if any("access" in path or "mfa" in path or "iam" in path for path in access_paths):
        report("PASS access-control retrieval returns relevant evidence")
    else:
        report(f"FAIL access-control retrieval paths {sorted(access_paths)}")
        errors.append("Access-control retrieval did not return expected evidence")

    change_results = search_documents("Is the production deploy approval evidence sufficient?", documents, limit=5)
    change_paths = {result.path for result in change_results}
    if any("deploy" in path or "change" in path for path in change_paths):
        report("PASS change-management retrieval returns relevant evidence")
    else:
        report(f"FAIL change-management retrieval paths {sorted(change_paths)}")
        errors.append("Change-management retrieval did not return expected evidence")
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

    report("CONSISTENCY NOTES")
    report("PASS Phase 2 is dataset-only; no framework implementation files are present.")
    report("PASS Dataset uses mock local evidence only.")
    report("PASS Intentional gaps are available for human-review routing tests.")
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

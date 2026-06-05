"""Framework-neutral document loading utilities.

The loader reads local mock evidence files only. It does not connect to live
systems, mutate source evidence, or claim production operating effectiveness.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Iterable, List

SUPPORTED_SUFFIXES = {".md", ".txt", ".json"}


@dataclass(frozen=True)
class DocumentRecord:
    """Loaded evidence document with stable metadata."""

    document_id: str
    path: str
    kind: str
    text: str


def infer_kind(path: Path) -> str:
    """Infer a high-level evidence kind from the path."""

    parts = set(path.parts)
    if "policies" in parts:
        return "policy"
    if "evidence" in parts:
        return "evidence"
    if "logs" in parts:
        return "log"
    if "tickets" in parts:
        return "ticket"
    return "unknown"


def stable_document_id(path: Path, root: Path) -> str:
    """Create a stable document id from a repository-relative path."""

    relative = path.relative_to(root).as_posix()
    digest = sha1(relative.encode("utf-8")).hexdigest()[:8]
    return f"doc-{digest}"


def iter_document_paths(root: Path) -> Iterable[Path]:
    """Yield supported evidence paths in deterministic order."""

    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path


def load_documents(data_root: str | Path = "data") -> List[DocumentRecord]:
    """Load all supported documents from the mock data directory."""

    root = Path(data_root).resolve()
    records: List[DocumentRecord] = []
    if not root.exists():
        return records

    for path in iter_document_paths(root):
        text = path.read_text(encoding="utf-8")
        records.append(
            DocumentRecord(
                document_id=stable_document_id(path, root),
                path=path.relative_to(root).as_posix(),
                kind=infer_kind(path),
                text=text,
            )
        )
    return records

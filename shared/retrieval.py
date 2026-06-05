"""Simple deterministic retrieval helpers for the shared lab baseline.

This module intentionally uses lexical scoring so every framework starts from
an inspectable, dependency-light retrieval baseline.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence

try:
    from .documents import DocumentRecord
except ImportError:  # pragma: no cover - useful for direct script execution
    from documents import DocumentRecord

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class RetrievalResult:
    """A ranked document result."""

    document_id: str
    path: str
    kind: str
    score: float
    snippet: str


def tokenize(text: str) -> List[str]:
    """Normalize text into lowercase lexical tokens."""

    return [token.lower() for token in TOKEN_RE.findall(text)]


def chunk_text(text: str, max_chars: int = 900) -> List[str]:
    """Split text into simple paragraph-aware chunks."""

    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: List[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = paragraph[:max_chars]
    if current:
        chunks.append(current)
    return chunks or [text[:max_chars]]


def score_document(query_tokens: Sequence[str], document_tokens: Sequence[str]) -> float:
    """Compute a small lexical relevance score."""

    if not query_tokens or not document_tokens:
        return 0.0
    doc_counts = {token: document_tokens.count(token) for token in set(document_tokens)}
    raw = sum(doc_counts.get(token, 0) for token in set(query_tokens))
    norm = math.sqrt(len(document_tokens)) or 1.0
    return round(raw / norm, 6)


def search_documents(
    question: str,
    documents: Iterable[DocumentRecord],
    limit: int = 4,
) -> List[RetrievalResult]:
    """Return deterministic top-k lexical results."""

    query_tokens = tokenize(question)
    results: List[RetrievalResult] = []
    for document in documents:
        chunks = chunk_text(document.text)
        best_chunk = chunks[0] if chunks else ""
        best_score = 0.0
        for chunk in chunks:
            score = score_document(query_tokens, tokenize(chunk))
            if score > best_score:
                best_score = score
                best_chunk = chunk
        if best_score > 0:
            results.append(
                RetrievalResult(
                    document_id=document.document_id,
                    path=document.path,
                    kind=document.kind,
                    score=best_score,
                    snippet=best_chunk[:500],
                )
            )
    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

"""Framework-neutral trace recorder."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, List, Optional
from uuid import uuid4

try:
    from .schemas import FrameworkName, ToolCallRecord, TraceEnvelope, TraceEvent
except ImportError:  # pragma: no cover
    from schemas import FrameworkName, ToolCallRecord, TraceEnvelope, TraceEvent


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


class TraceRecorder:
    """Small helper for consistent framework trace output."""

    def __init__(self, framework: FrameworkName, question: str) -> None:
        self.framework = framework
        self.question = question
        self.run_id = str(uuid4())
        self.started_at_utc = utc_now()
        self._start = perf_counter()
        self.events: List[TraceEvent] = []
        self.tool_calls: List[ToolCallRecord] = []

    def event(self, event_type: str, message: str = "", **data: Any) -> None:
        self.events.append(
            TraceEvent(
                event_type=event_type,
                timestamp_utc=utc_now(),
                framework=self.framework,
                message=message,
                data=dict(data),
            )
        )

    def tool_call(
        self,
        tool: str,
        latency_ms: int,
        status: str = "success",
        error: Optional[str] = None,
    ) -> None:
        self.tool_calls.append(
            ToolCallRecord(
                tool=tool,
                latency_ms=latency_ms,
                status=status,
                error=error,
            )
        )

    def elapsed_ms(self) -> int:
        return int((perf_counter() - self._start) * 1000)

    def envelope(self) -> TraceEnvelope:
        return TraceEnvelope(
            run_id=self.run_id,
            framework=self.framework,
            question=self.question,
            started_at_utc=self.started_at_utc,
            completed_at_utc=utc_now(),
            events=self.events,
            tool_calls=self.tool_calls,
        )

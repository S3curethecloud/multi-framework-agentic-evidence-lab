"""Shared schemas for the Multi-Framework Agentic Evidence Lab.

These models define the framework-neutral contract used by LangChain,
LangGraph, Strands, and ADK implementations. The schema is intentionally
read-only and evidence-oriented; it does not grant runtime authority.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

FrameworkName = Literal["langchain", "langgraph", "strands", "adk", "shared"]
RiskLevel = Literal["low", "medium", "high", "critical"]
ToolStatus = Literal["success", "error", "skipped"]
ControlArea = Literal[
    "Access Control",
    "Change Management",
    "Incident Response",
    "System Operations",
    "Risk Assessment",
    "Unknown",
]


class ToolCallRecord(BaseModel):
    """One tool invocation observed during an agent run."""

    model_config = ConfigDict(extra="forbid")

    tool: str = Field(min_length=1)
    latency_ms: int = Field(ge=0)
    status: ToolStatus
    error: Optional[str] = None


class EvidenceReference(BaseModel):
    """Evidence item used to support an answer."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1)
    path: str = Field(min_length=1)
    quote: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)


class AgentReport(BaseModel):
    """Required structured output produced by every framework implementation."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    control_area: ControlArea = "Unknown"
    evidence_ids: List[str] = Field(default_factory=list)
    evidence: List[EvidenceReference] = Field(default_factory=list)
    evidence_summary: str = ""
    gaps: List[str] = Field(default_factory=list)
    risk_level: RiskLevel = "medium"
    confidence: float = Field(ge=0.0, le=1.0)
    human_review_required: bool
    recommended_next_action: str = ""
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    failure_modes: List[str] = Field(default_factory=list)
    framework: FrameworkName

    @field_validator("confidence")
    @classmethod
    def normalize_confidence(cls, value: float) -> float:
        return round(float(value), 4)


class TraceEvent(BaseModel):
    """Framework-neutral trace event."""

    model_config = ConfigDict(extra="forbid")

    event_type: str = Field(min_length=1)
    timestamp_utc: str = Field(min_length=1)
    framework: FrameworkName
    message: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)


class TraceEnvelope(BaseModel):
    """Complete execution trace for one benchmark run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    framework: FrameworkName
    question: str = Field(min_length=1)
    started_at_utc: str = Field(min_length=1)
    completed_at_utc: Optional[str] = None
    events: List[TraceEvent] = Field(default_factory=list)
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    report: Optional[AgentReport] = None

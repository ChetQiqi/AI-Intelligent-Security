from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.stats import (
    CameraActivityResponse,
    PersonRankingResponse,
    StatsSummary,
    UnknownTrendResponse,
)


class AgentAnalyzeRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    days: int = Field(default=7, ge=1, le=30)


class AgentToolResult(BaseModel):
    name: str
    description: str
    data: dict[str, Any]


class AgentEvidence(BaseModel):
    recent_events: int
    recent_unknown_events: int
    top_camera_name: str | None
    top_camera_events: int
    top_camera_unknown_events: int
    top_camera_unknown_rate: float
    peak_unknown_date: str | None
    peak_unknown_count: int


class AgentAnomaly(BaseModel):
    rule_type: str
    risk_level: Literal["low", "medium", "high"]
    reason: str
    evidence: dict[str, Any]
    recommendation: str


class AgentAnalyzeResponse(BaseModel):
    question: str
    days: int
    risk_level: Literal["low", "medium", "high"]
    summary: StatsSummary
    unknown_trend: UnknownTrendResponse
    camera_activity: CameraActivityResponse
    person_ranking: PersonRankingResponse
    evidence: AgentEvidence
    anomalies: list[AgentAnomaly]
    knowledge_advice: str
    findings: list[str]
    recommendations: list[str]
    tool_results: list[AgentToolResult]
    report: str

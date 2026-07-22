from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Dimension(StrEnum):
    INFRASTRUCTURE = "INFRASTRUCTURE_DNA"
    IDENTITY = "IDENTITY_DNA"
    SOFTWARE = "SOFTWARE_DNA"
    API = "API_DNA"
    HISTORICAL = "HISTORICAL_DNA"
    TRUST = "TRUST_DNA"
    DEVELOPER = "DEVELOPER_ECOSYSTEM_DNA"


class Entity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_id: str
    entity_type: str
    value: str
    dimension: Dimension
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    observed_at: datetime = Field(default_factory=utcnow)
    source: str
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    model_config = ConfigDict(extra="forbid")
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float = Field(ge=0, le=1)
    source_diversity: int = 0
    temporal_validity: str = "unknown"
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    status: ClaimStatus = ClaimStatus.INFERRED
    reasoning: list[str] = Field(default_factory=list)


class ResolutionCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str
    entity_a: str
    entity_b: str
    status: ClaimStatus = ClaimStatus.INFERRED
    confidence: float = Field(ge=0, le=1)
    supporting: list[str] = Field(default_factory=list)
    against: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)

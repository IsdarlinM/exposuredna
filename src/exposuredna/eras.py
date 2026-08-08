from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.models import ClaimStatus

from .resolution import RelationshipType


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def _overlap(
    left_from: datetime,
    left_to: datetime | None,
    right_from: datetime,
    right_to: datetime | None,
) -> bool:
    maximum = datetime.max.replace(tzinfo=timezone.utc)
    return _aware(left_from) <= _aware(right_to or maximum) and _aware(right_from) <= _aware(left_to or maximum)


class OrganizationEra(BaseModel):
    model_config = ConfigDict(extra="forbid")

    era_id: str
    organization_id: str
    label: str
    valid_from: datetime
    valid_to: datetime | None = None
    status: ClaimStatus = ClaimStatus.OBSERVED
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_interval_and_status(self) -> "OrganizationEra":
        if self.valid_to is not None and _aware(self.valid_to) < _aware(self.valid_from):
            raise ValueError("valid_to must not precede valid_from")
        if self.status == ClaimStatus.VALIDATED:
            raise ValueError("organization-era modeling cannot create VALIDATED ownership")
        return self


class TemporalRelationshipClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationship_id: str
    subject_id: str
    object_id: str
    relationship_type: RelationshipType
    valid_from: datetime
    valid_to: datetime | None = None
    status: ClaimStatus = ClaimStatus.INFERRED
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    exclusive: bool = False

    @model_validator(mode="after")
    def validate_semantics(self) -> "TemporalRelationshipClaim":
        if self.valid_to is not None and _aware(self.valid_to) < _aware(self.valid_from):
            raise ValueError("valid_to must not precede valid_from")
        if self.status == ClaimStatus.VALIDATED:
            raise ValueError("temporal entity resolution cannot create VALIDATED ownership")
        return self


class TemporalRelationshipView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationship_id: str
    at: datetime
    active: bool
    status: ClaimStatus
    evidence_ids: list[str] = Field(default_factory=list)
    reason: str


class TemporalRelationshipConflict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    left_relationship_id: str
    right_relationship_id: str
    object_id: str
    status: ClaimStatus = ClaimStatus.UNKNOWN
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    reason: str

    @model_validator(mode="after")
    def conflict_is_uncertainty_only(self) -> "TemporalRelationshipConflict":
        if self.status != ClaimStatus.UNKNOWN:
            raise ValueError("temporal relationship conflicts must remain UNKNOWN")
        return self


def relationship_at(
    relationship: TemporalRelationshipClaim,
    at: datetime,
) -> TemporalRelationshipView:
    reference = _aware(at)
    active = _aware(relationship.valid_from) <= reference and (
        relationship.valid_to is None or reference <= _aware(relationship.valid_to)
    )
    if active:
        status = relationship.status
        reason = "The query time falls inside the relationship's evidenced validity interval."
    else:
        status = ClaimStatus.UNKNOWN
        reason = "Historical relationship evidence does not establish the relationship at the query time."
    return TemporalRelationshipView(
        relationship_id=relationship.relationship_id,
        at=reference,
        active=active,
        status=status,
        evidence_ids=relationship.evidence_ids,
        reason=reason,
    )


def detect_temporal_conflicts(
    relationships: Sequence[TemporalRelationshipClaim],
) -> list[TemporalRelationshipConflict]:
    """Detect overlapping explicitly-exclusive ownership/operation claims conservatively."""

    supported = {RelationshipType.OWNS, RelationshipType.OPERATES}
    conflicts: list[TemporalRelationshipConflict] = []
    ordered = sorted(relationships, key=lambda item: item.relationship_id)
    for index, left in enumerate(ordered):
        if not left.exclusive or left.relationship_type not in supported:
            continue
        for right in ordered[index + 1 :]:
            if (
                not right.exclusive
                or right.relationship_type != left.relationship_type
                or right.object_id != left.object_id
                or right.subject_id == left.subject_id
            ):
                continue
            if not _overlap(left.valid_from, left.valid_to, right.valid_from, right.valid_to):
                continue
            conflicts.append(
                TemporalRelationshipConflict(
                    left_relationship_id=left.relationship_id,
                    right_relationship_id=right.relationship_id,
                    object_id=left.object_id,
                    evidence_ids=sorted(set(left.evidence_ids + right.evidence_ids)),
                    counter_evidence_ids=sorted(
                        set(left.counter_evidence_ids + right.counter_evidence_ids)
                    ),
                    reason=(
                        "Two different subjects have overlapping explicitly-exclusive "
                        f"{left.relationship_type.value} claims; ownership/operation remains unresolved."
                    ),
                )
            )
    return conflicts

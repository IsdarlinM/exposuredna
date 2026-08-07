from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.models import ClaimStatus

from .resolution import RelationshipType


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SnapshotEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_id: str
    entity_type: str
    canonical_value: str
    status: ClaimStatus
    evidence_ids: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def evidence_semantics(self) -> "SnapshotEntity":
        if self.status in {ClaimStatus.OBSERVED, ClaimStatus.VALIDATED} and not self.evidence_ids:
            raise ValueError(f"{self.status} entities require evidence_ids")
        return self


class SnapshotRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    status: ClaimStatus
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def temporal_semantics(self) -> "SnapshotRelationship":
        if self.valid_from is not None and self.valid_from.tzinfo is None:
            raise ValueError("valid_from must be timezone-aware")
        if self.valid_to is not None and self.valid_to.tzinfo is None:
            raise ValueError("valid_to must be timezone-aware")
        if (
            self.valid_from is not None
            and self.valid_to is not None
            and self.valid_to <= self.valid_from
        ):
            raise ValueError("valid_to must be later than valid_from")
        return self


class OrganizationSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_id: str
    organization_id: str
    captured_at: datetime = Field(default_factory=utcnow)
    entities: list[SnapshotEntity] = Field(default_factory=list)
    relationships: list[SnapshotRelationship] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def snapshot_integrity(self) -> "OrganizationSnapshot":
        if self.captured_at.tzinfo is None:
            raise ValueError("captured_at must be timezone-aware")
        entity_ids = [item.entity_id for item in self.entities]
        relationship_ids = [item.relationship_id for item in self.relationships]
        if len(entity_ids) != len(set(entity_ids)):
            raise ValueError("snapshot entity IDs must be unique")
        if len(relationship_ids) != len(set(relationship_ids)):
            raise ValueError("snapshot relationship IDs must be unique")
        known_entities = set(entity_ids)
        for relationship in self.relationships:
            if relationship.source_entity_id not in known_entities:
                raise ValueError("relationship source is absent from snapshot entities")
            if relationship.target_entity_id not in known_entities:
                raise ValueError("relationship target is absent from snapshot entities")
        return self

    def content_sha256(self) -> str:
        payload = self.model_dump(mode="json", exclude={"snapshot_id"})
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class SnapshotChangeKind(StrEnum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    UNCHANGED = "UNCHANGED"


class SnapshotChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_type: str
    object_id: str
    change: SnapshotChangeKind
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    changed_fields: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class OrganizationSnapshotDiff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_id: str
    before_snapshot_id: str
    after_snapshot_id: str
    before_captured_at: datetime
    after_captured_at: datetime
    changes: list[SnapshotChange] = Field(default_factory=list)
    summary: dict[str, int] = Field(default_factory=dict)
    risk_score: None = None
    limitations: list[str] = Field(default_factory=list)


def _changed_fields(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    return sorted(
        key
        for key in set(before) | set(after)
        if before.get(key) != after.get(key)
    )


def _diff_objects(
    *,
    object_type: str,
    before: Sequence[BaseModel],
    after: Sequence[BaseModel],
    key: str,
) -> list[SnapshotChange]:
    before_map = {
        str(getattr(item, key)): item.model_dump(mode="json") for item in before
    }
    after_map = {
        str(getattr(item, key)): item.model_dump(mode="json") for item in after
    }
    changes: list[SnapshotChange] = []
    for object_id in sorted(set(before_map) | set(after_map)):
        old = before_map.get(object_id)
        new = after_map.get(object_id)
        if old is None:
            change = SnapshotChangeKind.ADDED
        elif new is None:
            change = SnapshotChangeKind.REMOVED
        elif old != new:
            change = SnapshotChangeKind.MODIFIED
        else:
            change = SnapshotChangeKind.UNCHANGED
        evidence = sorted(
            set((old or {}).get("evidence_ids", []))
            | set((new or {}).get("evidence_ids", []))
        )
        changes.append(
            SnapshotChange(
                object_type=object_type,
                object_id=object_id,
                change=change,
                before=old,
                after=new,
                changed_fields=(
                    [] if old is None or new is None else _changed_fields(old, new)
                ),
                evidence_ids=evidence,
                limitations=[
                    "A snapshot change is temporal evidence, not proof of ownership, exposure or vulnerability."
                ],
            )
        )
    return changes


def diff_snapshots(
    before: OrganizationSnapshot,
    after: OrganizationSnapshot,
    *,
    include_unchanged: bool = False,
) -> OrganizationSnapshotDiff:
    if before.organization_id != after.organization_id:
        raise ValueError("snapshots must describe the same organization")
    if after.captured_at < before.captured_at:
        raise ValueError("after snapshot must not predate before snapshot")

    changes = [
        *_diff_objects(
            object_type="entity",
            before=before.entities,
            after=after.entities,
            key="entity_id",
        ),
        *_diff_objects(
            object_type="relationship",
            before=before.relationships,
            after=after.relationships,
            key="relationship_id",
        ),
    ]
    if not include_unchanged:
        changes = [
            item for item in changes if item.change is not SnapshotChangeKind.UNCHANGED
        ]
    summary = {
        kind.value: sum(item.change is kind for item in changes)
        for kind in SnapshotChangeKind
    }
    return OrganizationSnapshotDiff(
        organization_id=before.organization_id,
        before_snapshot_id=before.snapshot_id,
        after_snapshot_id=after.snapshot_id,
        before_captured_at=before.captured_at,
        after_captured_at=after.captured_at,
        changes=changes,
        summary=summary,
        limitations=[
            "Snapshot completeness depends on source coverage and collection time.",
            "Removed evidence may represent missing collection rather than actual asset retirement.",
            "Historical ownership and acquisition relations do not establish current ownership."
        ],
    )


def acquisition_lineage(
    snapshots: Sequence[OrganizationSnapshot],
) -> list[SnapshotRelationship]:
    """Return temporally ordered acquisition/ownership history without current claims."""

    relationships = [
        relationship
        for snapshot in snapshots
        for relationship in snapshot.relationships
        if relationship.relationship_type
        in {
            RelationshipType.ACQUIRED,
            RelationshipType.FORMERLY_OWNED,
            RelationshipType.OWNS,
        }
    ]
    unique: dict[str, SnapshotRelationship] = {}
    for relationship in relationships:
        current = unique.get(relationship.relationship_id)
        if current is None or len(relationship.evidence_ids) > len(current.evidence_ids):
            unique[relationship.relationship_id] = relationship
    return sorted(
        unique.values(),
        key=lambda item: (
            item.valid_from or datetime.min.replace(tzinfo=timezone.utc),
            item.relationship_id,
        ),
    )

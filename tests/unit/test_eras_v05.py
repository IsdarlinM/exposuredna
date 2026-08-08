from __future__ import annotations

from datetime import datetime, timezone

from exposuredna.eras import (
    TemporalRelationshipClaim,
    detect_temporal_conflicts,
    relationship_at,
)
from exposuredna.resolution import RelationshipType
from sric.models import ClaimStatus

UTC = timezone.utc


def test_historical_relationship_does_not_propagate_to_future() -> None:
    relationship = TemporalRelationshipClaim(
        relationship_id="rel-1",
        subject_id="org-a",
        object_id="domain-1",
        relationship_type=RelationshipType.OWNS,
        valid_from=datetime(2021, 1, 1, tzinfo=UTC),
        valid_to=datetime(2023, 12, 31, tzinfo=UTC),
        status=ClaimStatus.INFERRED,
        evidence_ids=["ev-1"],
    )
    view = relationship_at(relationship, datetime(2026, 8, 8, tzinfo=UTC))
    assert view.active is False
    assert view.status is ClaimStatus.UNKNOWN


def test_overlapping_exclusive_ownership_is_unknown_conflict() -> None:
    left = TemporalRelationshipClaim(
        relationship_id="a",
        subject_id="org-a",
        object_id="asset-1",
        relationship_type=RelationshipType.OWNS,
        valid_from=datetime(2025, 1, 1, tzinfo=UTC),
        valid_to=datetime(2026, 12, 31, tzinfo=UTC),
        exclusive=True,
        evidence_ids=["ev-a"],
    )
    right = TemporalRelationshipClaim(
        relationship_id="b",
        subject_id="org-b",
        object_id="asset-1",
        relationship_type=RelationshipType.OWNS,
        valid_from=datetime(2026, 1, 1, tzinfo=UTC),
        exclusive=True,
        evidence_ids=["ev-b"],
    )
    conflicts = detect_temporal_conflicts([left, right])
    assert len(conflicts) == 1
    assert conflicts[0].status is ClaimStatus.UNKNOWN
    assert conflicts[0].evidence_ids == ["ev-a", "ev-b"]

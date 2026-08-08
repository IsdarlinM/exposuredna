from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hypothesis import given, strategies as st
from sric.models import ClaimStatus

from exposuredna.eras import TemporalRelationshipClaim, detect_temporal_conflicts, relationship_at
from exposuredna.resolution import RelationshipType

UTC = timezone.utc
BASE = datetime(2020, 1, 1, tzinfo=UTC)


@given(
    st.integers(min_value=0, max_value=1500),
    st.integers(min_value=1, max_value=1500),
    st.integers(min_value=1, max_value=1500),
)
def test_relationship_never_projects_past_evidenced_interval(
    start_offset: int,
    duration: int,
    after_offset: int,
) -> None:
    valid_from = BASE + timedelta(days=start_offset)
    valid_to = valid_from + timedelta(days=duration)
    relationship = TemporalRelationshipClaim(
        relationship_id="generated",
        subject_id="org-a",
        object_id="asset-a",
        relationship_type=RelationshipType.OWNS,
        valid_from=valid_from,
        valid_to=valid_to,
        status=ClaimStatus.INFERRED,
    )
    view = relationship_at(relationship, valid_to + timedelta(days=after_offset))
    assert view.active is False
    assert view.status is ClaimStatus.UNKNOWN


@given(st.integers(min_value=1, max_value=1000))
def test_generated_overlapping_exclusive_claims_remain_unknown(overlap_days: int) -> None:
    left = TemporalRelationshipClaim(
        relationship_id="left",
        subject_id="org-a",
        object_id="asset-a",
        relationship_type=RelationshipType.OPERATES,
        valid_from=BASE,
        valid_to=BASE + timedelta(days=overlap_days + 30),
        exclusive=True,
    )
    right = TemporalRelationshipClaim(
        relationship_id="right",
        subject_id="org-b",
        object_id="asset-a",
        relationship_type=RelationshipType.OPERATES,
        valid_from=BASE + timedelta(days=30),
        valid_to=BASE + timedelta(days=overlap_days + 60),
        exclusive=True,
    )
    conflicts = detect_temporal_conflicts([left, right])
    assert len(conflicts) == 1
    assert conflicts[0].status is ClaimStatus.UNKNOWN

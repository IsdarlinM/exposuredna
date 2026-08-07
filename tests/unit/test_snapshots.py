from datetime import datetime, timedelta, timezone

import pytest

from exposuredna.resolution import RelationshipType
from exposuredna.snapshots import (
    OrganizationSnapshot,
    SnapshotChangeKind,
    SnapshotEntity,
    SnapshotRelationship,
    acquisition_lineage,
    diff_snapshots,
)
from sric.models import ClaimStatus


T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T1 = T0 + timedelta(days=30)


def entity(
    entity_id: str,
    value: str,
    *,
    attributes: dict[str, object] | None = None,
) -> SnapshotEntity:
    return SnapshotEntity(
        entity_id=entity_id,
        entity_type="domain",
        canonical_value=value,
        status=ClaimStatus.OBSERVED,
        evidence_ids=[f"E-{entity_id}"],
        attributes=attributes or {},
    )


def relationship(
    relationship_id: str,
    source: str,
    target: str,
    relationship_type: RelationshipType,
    *,
    valid_from: datetime = T0,
) -> SnapshotRelationship:
    return SnapshotRelationship(
        relationship_id=relationship_id,
        source_entity_id=source,
        target_entity_id=target,
        relationship_type=relationship_type,
        status=ClaimStatus.INFERRED,
        valid_from=valid_from,
        evidence_ids=[f"E-{relationship_id}"],
    )


def snapshot(
    snapshot_id: str,
    captured_at: datetime,
    *,
    entities: list[SnapshotEntity],
    relationships: list[SnapshotRelationship] | None = None,
) -> OrganizationSnapshot:
    return OrganizationSnapshot(
        snapshot_id=snapshot_id,
        organization_id="org-1",
        captured_at=captured_at,
        entities=entities,
        relationships=relationships or [],
        source_ids=["source-1"],
    )


def test_snapshot_hash_is_deterministic() -> None:
    value = snapshot("S-1", T0, entities=[entity("D-1", "example.test")])

    assert value.content_sha256() == value.content_sha256()
    assert len(value.content_sha256()) == 64


def test_snapshot_diff_reports_added_removed_and_modified() -> None:
    before = snapshot(
        "S-1",
        T0,
        entities=[
            entity("D-1", "one.test", attributes={"state": "active"}),
            entity("D-2", "two.test"),
        ],
    )
    after = snapshot(
        "S-2",
        T1,
        entities=[
            entity("D-1", "one.test", attributes={"state": "redirected"}),
            entity("D-3", "three.test"),
        ],
    )

    report = diff_snapshots(before, after)
    changes = {item.object_id: item.change for item in report.changes}

    assert changes == {
        "D-1": SnapshotChangeKind.MODIFIED,
        "D-2": SnapshotChangeKind.REMOVED,
        "D-3": SnapshotChangeKind.ADDED,
    }
    assert report.risk_score is None
    assert "temporal evidence" in report.changes[0].limitations[0]


def test_unchanged_objects_are_omitted_by_default() -> None:
    before = snapshot("S-1", T0, entities=[entity("D-1", "one.test")])
    after = snapshot("S-2", T1, entities=[entity("D-1", "one.test")])

    assert diff_snapshots(before, after).changes == []
    included = diff_snapshots(before, after, include_unchanged=True)
    assert included.changes[0].change is SnapshotChangeKind.UNCHANGED


def test_snapshot_relationships_must_reference_present_entities() -> None:
    with pytest.raises(ValueError, match="target is absent"):
        snapshot(
            "S-X",
            T0,
            entities=[entity("ORG", "org")],
            relationships=[
                relationship("R-1", "ORG", "MISSING", RelationshipType.OWNS)
            ],
        )


def test_snapshots_from_different_organizations_cannot_be_diffed() -> None:
    before = snapshot("S-1", T0, entities=[])
    after = OrganizationSnapshot(
        snapshot_id="S-2",
        organization_id="org-2",
        captured_at=T1,
    )

    with pytest.raises(ValueError, match="same organization"):
        diff_snapshots(before, after)


def test_reverse_time_diff_is_rejected() -> None:
    before = snapshot("S-1", T1, entities=[])
    after = snapshot("S-2", T0, entities=[])

    with pytest.raises(ValueError, match="must not predate"):
        diff_snapshots(before, after)


def test_acquisition_lineage_is_temporal_and_deduplicated() -> None:
    entities = [entity("ORG-A", "org-a"), entity("ORG-B", "org-b")]
    relation = relationship(
        "ACQ-1",
        "ORG-A",
        "ORG-B",
        RelationshipType.ACQUIRED,
        valid_from=T0,
    )
    first = snapshot("S-1", T0, entities=entities, relationships=[relation])
    richer_relation = relation.model_copy(
        update={"evidence_ids": ["E-ACQ-1", "E-ACQ-2"]}
    )
    second = snapshot(
        "S-2",
        T1,
        entities=entities,
        relationships=[richer_relation],
    )

    lineage = acquisition_lineage([second, first])

    assert len(lineage) == 1
    assert lineage[0].evidence_ids == ["E-ACQ-1", "E-ACQ-2"]


def test_observed_entity_requires_evidence() -> None:
    with pytest.raises(ValueError, match="require evidence_ids"):
        SnapshotEntity(
            entity_id="D-X",
            entity_type="domain",
            canonical_value="example.test",
            status=ClaimStatus.OBSERVED,
        )

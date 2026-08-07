from datetime import datetime, timezone

import pytest

from exposuredna.interchange import (
    EntityMergeOperation,
    EntityResolutionMutationPlan,
    EntitySplitOperation,
    apply_resolution_plan,
    export_snapshot_graphml,
    export_snapshot_jsonld,
    rollback_resolution_plan,
)
from exposuredna.resolution import RelationshipType
from exposuredna.snapshots import OrganizationSnapshot, SnapshotEntity, SnapshotRelationship
from sric.models import ClaimStatus

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def entity(entity_id: str, value: str, entity_type: str = "domain") -> SnapshotEntity:
    return SnapshotEntity(
        entity_id=entity_id,
        entity_type=entity_type,
        canonical_value=value,
        status=ClaimStatus.OBSERVED,
        evidence_ids=[f"E-{entity_id}"],
    )


def relationship(relationship_id: str, source: str, target: str) -> SnapshotRelationship:
    return SnapshotRelationship(
        relationship_id=relationship_id,
        source_entity_id=source,
        target_entity_id=target,
        relationship_type=RelationshipType.POSSIBLY_RELATED,
        status=ClaimStatus.INFERRED,
        valid_from=T0,
        evidence_ids=[f"E-{relationship_id}"],
    )


def snapshot() -> OrganizationSnapshot:
    return OrganizationSnapshot(
        snapshot_id="S-1",
        organization_id="org-1",
        captured_at=T0,
        entities=[
            entity("ORG", "org", "organization"),
            entity("D-1", "one.test"),
            entity("D-2", "two.test"),
        ],
        relationships=[
            relationship("R-1", "ORG", "D-1"),
            relationship("R-2", "ORG", "D-2"),
        ],
    )


def test_snapshot_exports_are_interoperable_and_evidence_bearing() -> None:
    value = snapshot()
    jsonld = export_snapshot_jsonld(value)
    graphml = export_snapshot_graphml(value)
    assert '"POSSIBLY_RELATED"' in jsonld
    assert "E-R-1" in jsonld
    assert "POSSIBLY_RELATED" in graphml
    assert "E-R-2" in graphml


def test_resolution_plan_requires_an_operation() -> None:
    with pytest.raises(ValueError, match="at least one merge or split"):
        EntityResolutionMutationPlan(plan_id="EMPTY")


def test_plan_rejects_entities_used_by_multiple_operations() -> None:
    with pytest.raises(ValueError, match="only one plan operation"):
        EntityResolutionMutationPlan(
            plan_id="AMBIGUOUS",
            merges=[
                EntityMergeOperation(
                    target_entity_id="D-1",
                    source_entity_ids=["D-2"],
                    reason="first",
                ),
                EntityMergeOperation(
                    target_entity_id="D-1",
                    source_entity_ids=["D-3"],
                    reason="second",
                ),
            ],
        )


def test_merge_plan_requires_human_approval() -> None:
    plan = EntityResolutionMutationPlan(
        plan_id="P-1",
        merges=[
            EntityMergeOperation(
                target_entity_id="D-1",
                source_entity_ids=["D-2"],
                reason="Duplicate confirmed by reviewer",
            )
        ],
    )
    with pytest.raises(PermissionError, match="human approval"):
        apply_resolution_plan(snapshot(), plan)


def test_merge_dry_run_previews_rewired_graph_without_validating_ownership() -> None:
    plan = EntityResolutionMutationPlan(
        plan_id="P-1",
        merges=[
            EntityMergeOperation(
                target_entity_id="D-1",
                source_entity_ids=["D-2"],
                reason="Duplicate candidate",
                evidence_ids=["E-REVIEW"],
            )
        ],
        human_approved=True,
        dry_run=True,
    )
    result = apply_resolution_plan(snapshot(), plan)
    assert result.applied is False
    assert {item.entity_id for item in result.after_snapshot.entities} == {"ORG", "D-1"}
    assert all(item.target_entity_id == "D-1" for item in result.after_snapshot.relationships)
    assert result.ownership_validated is False
    assert "must not be persisted" in result.limitations[1]


def test_malformed_existing_merge_metadata_is_ignored_safely() -> None:
    value = snapshot()
    target = next(item for item in value.entities if item.entity_id == "D-1")
    target.attributes["merged_from"] = [{"unhashable": True}, "D-0", 42]
    plan = EntityResolutionMutationPlan(
        plan_id="P-METADATA",
        merges=[
            EntityMergeOperation(
                target_entity_id="D-1",
                source_entity_ids=["D-2"],
                reason="Duplicate candidate",
            )
        ],
        human_approved=True,
    )
    result = apply_resolution_plan(value, plan)
    merged = next(item for item in result.after_snapshot.entities if item.entity_id == "D-1")
    assert merged.attributes["merged_from"] == ["D-0", "D-2"]


def test_merge_that_creates_self_loop_is_rejected() -> None:
    value = snapshot()
    value.relationships.append(relationship("R-SELF", "D-1", "D-2"))
    plan = EntityResolutionMutationPlan(
        plan_id="P-SELF",
        merges=[
            EntityMergeOperation(
                target_entity_id="D-1",
                source_entity_ids=["D-2"],
                reason="Duplicate candidate",
            )
        ],
        human_approved=True,
    )
    with pytest.raises(ValueError, match="self-referential"):
        apply_resolution_plan(value, plan)


def test_split_requires_complete_relationship_assignment() -> None:
    value = snapshot()
    plan = EntityResolutionMutationPlan(
        plan_id="P-SPLIT",
        splits=[
            EntitySplitOperation(
                source_entity_id="ORG",
                new_entities=[
                    entity("ORG-A", "org-a", "organization"),
                    entity("ORG-B", "org-b", "organization"),
                ],
                relationship_assignments={"R-1": "ORG-A"},
                reason="Distinct organizations",
            )
        ],
        human_approved=True,
        dry_run=True,
    )
    with pytest.raises(ValueError, match="assignments incomplete"):
        apply_resolution_plan(value, plan)


def test_split_and_rollback_restore_complete_snapshot() -> None:
    value = snapshot()
    plan = EntityResolutionMutationPlan(
        plan_id="P-SPLIT",
        splits=[
            EntitySplitOperation(
                source_entity_id="ORG",
                new_entities=[
                    entity("ORG-A", "org-a", "organization"),
                    entity("ORG-B", "org-b", "organization"),
                ],
                relationship_assignments={"R-1": "ORG-A", "R-2": "ORG-B"},
                reason="Evidence distinguishes two organizations",
                evidence_ids=["E-SPLIT"],
            )
        ],
        human_approved=True,
        dry_run=False,
    )
    result = apply_resolution_plan(value, plan)
    restored = rollback_resolution_plan(result, rollback_token=result.rollback_token)
    assert result.applied is True
    assert {item.entity_id for item in result.after_snapshot.entities} == {
        "ORG-A",
        "ORG-B",
        "D-1",
        "D-2",
    }
    assert restored.content_sha256() == value.content_sha256()


def test_invalid_rollback_token_is_rejected() -> None:
    plan = EntityResolutionMutationPlan(
        plan_id="P-1",
        merges=[
            EntityMergeOperation(
                target_entity_id="D-1",
                source_entity_ids=["D-2"],
                reason="Duplicate",
            )
        ],
        human_approved=True,
    )
    result = apply_resolution_plan(snapshot(), plan)
    with pytest.raises(PermissionError, match="invalid rollback"):
        rollback_resolution_plan(result, rollback_token="bad")

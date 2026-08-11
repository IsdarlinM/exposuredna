from __future__ import annotations

import hashlib
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.exports import ExportEdge, ExportNode, export_graphml, export_jsonld

from .snapshots import OrganizationSnapshot, SnapshotEntity


class EntityMergeOperation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_entity_id: str
    source_entity_ids: list[str]
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def merge_semantics(self) -> "EntityMergeOperation":
        sources = set(self.source_entity_ids)
        if not sources:
            raise ValueError("merge requires at least one source entity")
        if self.target_entity_id in sources:
            raise ValueError("merge target cannot also be a source entity")
        if len(sources) != len(self.source_entity_ids):
            raise ValueError("merge source entity IDs must be unique")
        return self


class EntitySplitOperation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_entity_id: str
    new_entities: list[SnapshotEntity]
    relationship_assignments: dict[str, str]
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def split_semantics(self) -> "EntitySplitOperation":
        if len(self.new_entities) < 2:
            raise ValueError("split requires at least two replacement entities")
        ids = [item.entity_id for item in self.new_entities]
        if len(ids) != len(set(ids)):
            raise ValueError("split replacement entity IDs must be unique")
        if self.source_entity_id in ids:
            raise ValueError("split replacement IDs must differ from the source")
        if set(self.relationship_assignments.values()) - set(ids):
            raise ValueError("relationship assignments must target replacement entities")
        return self


class EntityResolutionMutationPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    merges: list[EntityMergeOperation] = Field(default_factory=list)
    splits: list[EntitySplitOperation] = Field(default_factory=list)
    human_approved: bool = False
    dry_run: bool = True

    @model_validator(mode="after")
    def validate_operation_set(self) -> "EntityResolutionMutationPlan":
        if not self.merges and not self.splits:
            raise ValueError("resolution plan requires at least one merge or split")
        touched: list[str] = []
        for merge in self.merges:
            touched.append(merge.target_entity_id)
            touched.extend(merge.source_entity_ids)
        for split in self.splits:
            touched.append(split.source_entity_id)
            touched.extend(item.entity_id for item in split.new_entities)
        duplicates = sorted(
            {entity_id for entity_id in touched if touched.count(entity_id) > 1}
        )
        if duplicates:
            raise ValueError(
                "entities may participate in only one plan operation: "
                + ", ".join(duplicates)
            )
        return self


class EntityResolutionMutationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    applied: bool
    before_snapshot: OrganizationSnapshot
    after_snapshot: OrganizationSnapshot
    rollback_token: str
    changed_entity_ids: list[str]
    changed_relationship_ids: list[str]
    ownership_validated: bool = False
    limitations: list[str] = Field(default_factory=list)


def export_snapshot_jsonld(snapshot: OrganizationSnapshot) -> str:
    nodes = [
        ExportNode(
            node_id=item.entity_id,
            node_type=item.entity_type,
            label=item.canonical_value,
            status=item.status,
            evidence_ids=item.evidence_ids,
            attributes=item.attributes,
        )
        for item in snapshot.entities
    ]
    edges = [
        ExportEdge(
            edge_id=item.relationship_id,
            source_id=item.source_entity_id,
            target_id=item.target_entity_id,
            edge_type=item.relationship_type.value,
            status=item.status,
            evidence_ids=item.evidence_ids,
            counter_evidence_ids=item.counter_evidence_ids,
            attributes={
                **item.attributes,
                "valid_from": item.valid_from.isoformat() if item.valid_from else None,
                "valid_to": item.valid_to.isoformat() if item.valid_to else None,
            },
        )
        for item in snapshot.relationships
    ]
    return export_jsonld(nodes, edges)


def export_snapshot_graphml(snapshot: OrganizationSnapshot) -> str:
    nodes = [
        ExportNode(
            node_id=item.entity_id,
            node_type=item.entity_type,
            label=item.canonical_value,
            status=item.status,
            evidence_ids=item.evidence_ids,
            attributes=item.attributes,
        )
        for item in snapshot.entities
    ]
    edges = [
        ExportEdge(
            edge_id=item.relationship_id,
            source_id=item.source_entity_id,
            target_id=item.target_entity_id,
            edge_type=item.relationship_type.value,
            status=item.status,
            evidence_ids=item.evidence_ids,
            counter_evidence_ids=item.counter_evidence_ids,
            attributes=item.attributes,
        )
        for item in snapshot.relationships
    ]
    return export_graphml(nodes, edges)


def _merge_entity(
    target: SnapshotEntity,
    sources: Sequence[SnapshotEntity],
    operation: EntityMergeOperation,
) -> SnapshotEntity:
    source_types = {item.entity_type for item in sources}
    if source_types - {target.entity_type}:
        raise ValueError("merge entities must share the same entity_type")
    attributes = dict(target.attributes)
    existing_raw = attributes.get("merged_from", [])
    existing_merged = (
        {item for item in existing_raw if isinstance(item, str)}
        if isinstance(existing_raw, list)
        else set()
    )
    merged_from = {item.entity_id for item in sources}
    attributes["merged_from"] = sorted(existing_merged | merged_from)
    attributes["merge_reason"] = operation.reason
    return target.model_copy(
        update={
            "evidence_ids": sorted(
                set(target.evidence_ids)
                | set(operation.evidence_ids)
                | {
                    evidence
                    for item in sources
                    for evidence in item.evidence_ids
                }
            ),
            "attributes": attributes,
        }
    )


def apply_resolution_plan(
    snapshot: OrganizationSnapshot,
    plan: EntityResolutionMutationPlan,
) -> EntityResolutionMutationResult:
    if not plan.human_approved:
        raise PermissionError("entity merge/split plans require human approval")

    before = snapshot.model_copy(deep=True)
    entities = {
        item.entity_id: item.model_copy(deep=True) for item in snapshot.entities
    }
    relationships = {
        item.relationship_id: item.model_copy(deep=True)
        for item in snapshot.relationships
    }
    changed_entities: set[str] = set()
    changed_relationships: set[str] = set()

    for merge_operation in plan.merges:
        target = entities.get(merge_operation.target_entity_id)
        if target is None:
            raise ValueError(f"unknown merge target: {merge_operation.target_entity_id}")
        missing = sorted(set(merge_operation.source_entity_ids) - set(entities))
        if missing:
            raise ValueError("unknown merge sources: " + ", ".join(missing))
        sources = [entities[source_id] for source_id in merge_operation.source_entity_ids]
        entities[target.entity_id] = _merge_entity(target, sources, merge_operation)
        for relationship_id, relationship in list(relationships.items()):
            relationship_update: dict[str, str] = {}
            if relationship.source_entity_id in merge_operation.source_entity_ids:
                relationship_update["source_entity_id"] = target.entity_id
            if relationship.target_entity_id in merge_operation.source_entity_ids:
                relationship_update["target_entity_id"] = target.entity_id
            if relationship_update:
                relationships[relationship_id] = relationship.model_copy(update=relationship_update)
                changed_relationships.add(relationship_id)
        for source_id in merge_operation.source_entity_ids:
            entities.pop(source_id)
            changed_entities.add(source_id)
        changed_entities.add(target.entity_id)

    for split_operation in plan.splits:
        source = entities.get(split_operation.source_entity_id)
        if source is None:
            raise ValueError(f"unknown split source: {split_operation.source_entity_id}")
        replacement_ids = {item.entity_id for item in split_operation.new_entities}
        if replacement_ids & set(entities):
            raise ValueError("split replacement IDs already exist")
        touching = {
            relationship_id
            for relationship_id, relationship in relationships.items()
            if split_operation.source_entity_id
            in {relationship.source_entity_id, relationship.target_entity_id}
        }
        if touching != set(split_operation.relationship_assignments):
            missing = sorted(touching - set(split_operation.relationship_assignments))
            extra = sorted(set(split_operation.relationship_assignments) - touching)
            raise ValueError(
                f"split relationship assignments incomplete; missing={missing}, extra={extra}"
            )
        for replacement in split_operation.new_entities:
            attributes = dict(replacement.attributes)
            attributes["split_from"] = source.entity_id
            attributes["split_reason"] = split_operation.reason
            entities[replacement.entity_id] = replacement.model_copy(
                update={
                    "evidence_ids": sorted(
                        set(replacement.evidence_ids)
                        | set(source.evidence_ids)
                        | set(split_operation.evidence_ids)
                    ),
                    "attributes": attributes,
                }
            )
            changed_entities.add(replacement.entity_id)
        for relationship_id in touching:
            relationship = relationships[relationship_id]
            replacement_id = split_operation.relationship_assignments[relationship_id]
            split_update: dict[str, str] = {}
            if relationship.source_entity_id == source.entity_id:
                split_update["source_entity_id"] = replacement_id
            if relationship.target_entity_id == source.entity_id:
                split_update["target_entity_id"] = replacement_id
            relationships[relationship_id] = relationship.model_copy(update=split_update)
            changed_relationships.add(relationship_id)
        entities.pop(source.entity_id)
        changed_entities.add(source.entity_id)

    self_loops = sorted(
        relationship.relationship_id
        for relationship in relationships.values()
        if relationship.source_entity_id == relationship.target_entity_id
    )
    if self_loops:
        raise ValueError(
            "resolution plan would create self-referential relationships: "
            + ", ".join(self_loops)
        )

    proposed = snapshot.model_copy(
        update={
            "snapshot_id": f"{snapshot.snapshot_id}:{plan.plan_id}",
            "entities": sorted(entities.values(), key=lambda item: item.entity_id),
            "relationships": sorted(
                relationships.values(), key=lambda item: item.relationship_id
            ),
            "notes": [
                *snapshot.notes,
                f"Entity resolution plan {plan.plan_id} proposed in-memory.",
            ],
        }
    )
    after = OrganizationSnapshot.model_validate(proposed.model_dump(mode="python"))
    rollback_token = hashlib.sha256(
        f"{plan.plan_id}\x00{before.content_sha256()}".encode("utf-8")
    ).hexdigest()
    return EntityResolutionMutationResult(
        plan_id=plan.plan_id,
        applied=not plan.dry_run,
        before_snapshot=before,
        after_snapshot=after,
        rollback_token=rollback_token,
        changed_entity_ids=sorted(changed_entities),
        changed_relationship_ids=sorted(changed_relationships),
        limitations=[
            "Entity merge/split changes graph representation only; it never validates ownership.",
            "Dry-run results contain the proposed snapshot but must not be persisted.",
            "The caller must persist approved non-dry-run results transactionally.",
            "Rollback requires the exact result and token and restores the complete prior snapshot.",
        ],
    )


def rollback_resolution_plan(
    result: EntityResolutionMutationResult,
    *,
    rollback_token: str,
) -> OrganizationSnapshot:
    expected = hashlib.sha256(
        f"{result.plan_id}\x00{result.before_snapshot.content_sha256()}".encode("utf-8")
    ).hexdigest()
    if rollback_token != expected or rollback_token != result.rollback_token:
        raise PermissionError("invalid rollback token")
    return result.before_snapshot.model_copy(deep=True)

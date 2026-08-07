from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from .api import create_app as create_base_app
from .interchange import (
    EntityResolutionMutationPlan,
    EntityResolutionMutationResult,
    apply_resolution_plan,
    export_snapshot_graphml,
    export_snapshot_jsonld,
    rollback_resolution_plan,
)
from .resolution import RelationshipType, ResolutionSignal, evaluate_resolution
from .snapshots import OrganizationSnapshot, acquisition_lineage, diff_snapshots


class ResolutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str
    subject_id: str
    object_id: str
    proposed_relationship: RelationshipType
    signals: list[ResolutionSignal]


class SnapshotDiffRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    before: OrganizationSnapshot
    after: OrganizationSnapshot
    include_unchanged: bool = False


class LineageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshots: list[OrganizationSnapshot]


class SnapshotExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot: OrganizationSnapshot
    format: Literal["jsonld", "graphml"]


class ResolutionPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot: OrganizationSnapshot
    plan: EntityResolutionMutationPlan


class ResolutionRollbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    result: EntityResolutionMutationResult
    rollback_token: str


router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/resolution/evaluate")
async def resolution_evaluate(request: ResolutionRequest) -> dict[str, object]:
    candidate = evaluate_resolution(
        candidate_id=request.candidate_id,
        subject_id=request.subject_id,
        object_id=request.object_id,
        proposed_relationship=request.proposed_relationship,
        signals=request.signals,
    )
    return {
        "candidate": candidate.model_dump(mode="json"),
        "ownership_validated": False,
        "validated_findings_created": 0,
    }


@router.post("/snapshots/diff")
async def snapshot_diff(request: SnapshotDiffRequest) -> dict[str, object]:
    try:
        report = diff_snapshots(
            request.before,
            request.after,
            include_unchanged=request.include_unchanged,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "diff": report.model_dump(mode="json"),
        "risk_score": None,
        "ownership_validated": False,
    }


@router.post("/lineage/acquisitions")
async def lineage(request: LineageRequest) -> dict[str, object]:
    relationships = acquisition_lineage(request.snapshots)
    return {
        "relationships": [item.model_dump(mode="json") for item in relationships],
        "current_ownership_inferred": False,
    }


@router.post("/snapshots/export")
async def snapshot_export(request: SnapshotExportRequest) -> dict[str, object]:
    content = (
        export_snapshot_jsonld(request.snapshot)
        if request.format == "jsonld"
        else export_snapshot_graphml(request.snapshot)
    )
    return {
        "format": request.format,
        "content": content,
        "ownership_validated": False,
        "persisted": False,
    }


@router.post("/resolution/plan")
async def resolution_plan(request: ResolutionPlanRequest) -> dict[str, object]:
    try:
        result = apply_resolution_plan(request.snapshot, request.plan)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "result": result.model_dump(mode="json"),
        "persisted": False,
        "ownership_validated": False,
        "validated_findings_created": 0,
    }


@router.post("/resolution/rollback")
async def resolution_rollback(request: ResolutionRollbackRequest) -> dict[str, object]:
    try:
        restored = rollback_resolution_plan(
            request.result,
            rollback_token=request.rollback_token,
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    return {
        "snapshot": restored.model_dump(mode="json"),
        "persisted": False,
        "ownership_validated": False,
    }


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)
    app.include_router(router)
    return app

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict

from .api import create_app as create_base_app
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
    report = diff_snapshots(
        request.before,
        request.after,
        include_unchanged=request.include_unchanged,
    )
    return {
        "diff": report.model_dump(mode="json"),
        "risk_score": None,
        "ownership_validated": False,
    }


@router.post("/lineage/acquisitions")
async def lineage(request: LineageRequest) -> dict[str, object]:
    relationships = acquisition_lineage(request.snapshots)
    return {
        "relationships": [
            item.model_dump(mode="json") for item in relationships
        ],
        "current_ownership_inferred": False,
    }


def create_app() -> FastAPI:
    app = create_base_app()
    app.include_router(router)
    return app

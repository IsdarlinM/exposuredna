from __future__ import annotations

import json
from pathlib import Path

import typer

from .cli import app
from .resolution import (
    RelationshipType,
    ResolutionSignal,
    evaluate_resolution,
)
from .snapshots import OrganizationSnapshot, acquisition_lineage, diff_snapshots


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc


@app.command("resolve-evaluate")
def resolve_evaluate(
    path: Path,
    candidate_id: str = typer.Option(..., "--candidate-id"),
    subject_id: str = typer.Option(..., "--subject-id"),
    object_id: str = typer.Option(..., "--object-id"),
    relationship: RelationshipType = typer.Option(
        ...,
        "--relationship",
        case_sensitive=False,
    ),
) -> None:
    """Evaluate resolution signals without asserting ownership."""

    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("resolution signals JSON must be a list")
    signals = [ResolutionSignal.model_validate(item) for item in raw]
    candidate = evaluate_resolution(
        candidate_id=candidate_id,
        subject_id=subject_id,
        object_id=object_id,
        proposed_relationship=relationship,
        signals=signals,
    )
    typer.echo(candidate.model_dump_json(indent=2))
    if candidate.status.value == "UNKNOWN":
        raise typer.Exit(2)


@app.command("snapshot-diff")
def snapshot_diff(
    before: Path,
    after: Path,
    include_unchanged: bool = typer.Option(False, "--include-unchanged"),
) -> None:
    """Compare organization snapshots without producing a risk score."""

    old = OrganizationSnapshot.model_validate(_read_json(before))
    new = OrganizationSnapshot.model_validate(_read_json(after))
    report = diff_snapshots(old, new, include_unchanged=include_unchanged)
    typer.echo(report.model_dump_json(indent=2))


@app.command("acquisition-lineage")
def acquisition_lineage_command(path: Path) -> None:
    """Extract temporal acquisition/ownership history from snapshot JSON."""

    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("snapshots JSON must be a list")
    snapshots = [OrganizationSnapshot.model_validate(item) for item in raw]
    relationships = acquisition_lineage(snapshots)
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in relationships],
            indent=2,
            default=str,
        )
    )

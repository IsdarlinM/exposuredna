from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer
from pydantic import ValidationError

from .cli import app
from .eras import TemporalRelationshipClaim, detect_temporal_conflicts, relationship_at


def _read(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc


@app.command("relationship-at")
def relationship_at_command(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    at: str = typer.Option(..., "--at", help="ISO-8601 query time."),
) -> None:
    """Evaluate a temporal relationship at one point in time."""

    try:
        raw = _read(path)
        relationship = TemporalRelationshipClaim.model_validate(raw)
        when = datetime.fromisoformat(at.replace("Z", "+00:00"))
        view = relationship_at(relationship, when)
    except (ValidationError, ValueError, TypeError) as exc:
        typer.echo(f"temporal relationship query failed: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(
        json.dumps(
            {
                "view": view.model_dump(mode="json"),
                "ownership_validated": False,
                "historical_relationship_projected_forward": False,
            },
            indent=2,
        )
    )


@app.command("relationship-conflicts")
def relationship_conflicts(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
) -> None:
    """Detect overlapping explicitly-exclusive ownership/operation claims."""

    try:
        raw = _read(path)
        if not isinstance(raw, list):
            raise ValueError("input must be a JSON list")
        relationships = [TemporalRelationshipClaim.model_validate(item) for item in raw]
        conflicts = detect_temporal_conflicts(relationships)
    except (ValidationError, ValueError, TypeError) as exc:
        typer.echo(f"temporal conflict analysis failed: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(
        json.dumps(
            {
                "conflicts": [item.model_dump(mode="json") for item in conflicts],
                "ownership_validated": False,
                "validated_findings_created": 0,
            },
            indent=2,
        )
    )

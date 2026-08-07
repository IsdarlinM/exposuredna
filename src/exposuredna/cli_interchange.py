from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from .cli import app
from .interchange import (
    EntityResolutionMutationPlan,
    EntityResolutionMutationResult,
    apply_resolution_plan,
    export_snapshot_graphml,
    export_snapshot_jsonld,
    rollback_resolution_plan,
)
from .snapshots import OrganizationSnapshot


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc


def _write_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise typer.BadParameter(f"cannot write {path}: {exc}") from exc


def _validation_error(label: str, exc: Exception) -> typer.Exit:
    typer.echo(f"invalid {label}: {exc}", err=True)
    return typer.Exit(2)


@app.command("snapshot-export")
def snapshot_export(
    snapshot: Path,
    output: Path,
    format: str = typer.Option("jsonld", "--format"),
) -> None:
    """Export a snapshot as evidence-bearing JSON-LD or GraphML."""
    normalized = format.lower()
    if normalized not in {"jsonld", "graphml"}:
        raise typer.BadParameter("--format must be jsonld or graphml")
    try:
        value = OrganizationSnapshot.model_validate(_read_json(snapshot))
        content = (
            export_snapshot_jsonld(value)
            if normalized == "jsonld"
            else export_snapshot_graphml(value)
        )
    except (ValidationError, ValueError) as exc:
        raise _validation_error("snapshot", exc) from exc
    _write_text(output, content)
    typer.echo(str(output))


@app.command("resolution-plan")
def resolution_plan(
    snapshot: Path,
    plan: Path,
    output: Path,
    approve: bool = typer.Option(False, "--approve"),
    apply: bool = typer.Option(False, "--apply"),
) -> None:
    """Preview or materialize an approved merge/split result as a new JSON file."""
    if apply and not approve:
        raise typer.BadParameter("--apply requires --approve")
    try:
        value = OrganizationSnapshot.model_validate(_read_json(snapshot))
        mutation = EntityResolutionMutationPlan.model_validate(_read_json(plan))
        mutation = mutation.model_copy(
            update={"human_approved": approve, "dry_run": not apply}
        )
        result = apply_resolution_plan(value, mutation)
    except PermissionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(3) from exc
    except (ValidationError, ValueError) as exc:
        raise _validation_error("resolution plan", exc) from exc
    _write_text(output, result.model_dump_json(indent=2) + "\n")
    typer.echo(str(output))


@app.command("resolution-rollback")
def resolution_rollback(
    result: Path,
    rollback_token: str = typer.Option(..., "--rollback-token"),
    output: Path = typer.Option(..., "--output"),
) -> None:
    """Restore the complete pre-plan snapshot into a new JSON file."""
    try:
        value = EntityResolutionMutationResult.model_validate(_read_json(result))
        restored = rollback_resolution_plan(value, rollback_token=rollback_token)
    except PermissionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(3) from exc
    except (ValidationError, ValueError) as exc:
        raise _validation_error("resolution result", exc) from exc
    _write_text(output, restored.model_dump_json(indent=2) + "\n")
    typer.echo(str(output))

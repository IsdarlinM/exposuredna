from __future__ import annotations

import json
from pathlib import Path

import typer

from .cli import app
from .interchange import (
    EntityResolutionMutationPlan,
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@app.command("snapshot-export")
def snapshot_export(
    snapshot: Path,
    output: Path,
    format: str = typer.Option("jsonld", "--format"),
) -> None:
    """Export a snapshot as evidence-bearing JSON-LD or GraphML."""

    value = OrganizationSnapshot.model_validate(_read_json(snapshot))
    normalized = format.lower()
    if normalized == "jsonld":
        content = export_snapshot_jsonld(value)
    elif normalized == "graphml":
        content = export_snapshot_graphml(value)
    else:
        raise typer.BadParameter("--format must be jsonld or graphml")
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

    value = OrganizationSnapshot.model_validate(_read_json(snapshot))
    mutation = EntityResolutionMutationPlan.model_validate(_read_json(plan))
    mutation = mutation.model_copy(
        update={
            "human_approved": approve,
            "dry_run": not apply,
        }
    )
    if apply and not approve:
        raise typer.BadParameter("--apply requires --approve")
    try:
        result = apply_resolution_plan(value, mutation)
    except (PermissionError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    _write_text(output, result.model_dump_json(indent=2) + "\n")
    typer.echo(str(output))


@app.command("resolution-rollback")
def resolution_rollback(
    result: Path,
    rollback_token: str = typer.Option(..., "--rollback-token"),
    output: Path = typer.Option(..., "--output"),
) -> None:
    """Restore the complete pre-plan snapshot into a new JSON file."""

    from .interchange import EntityResolutionMutationResult

    value = EntityResolutionMutationResult.model_validate(_read_json(result))
    try:
        restored = rollback_resolution_plan(value, rollback_token=rollback_token)
    except PermissionError as exc:
        raise typer.BadParameter(str(exc)) from exc
    _write_text(output, restored.model_dump_json(indent=2) + "\n")
    typer.echo(str(output))

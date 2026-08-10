from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from sric.plugins import PluginRegistry
from sric.workspace import Workspace

from . import __version__
from .core import ExposureEngine
from .sric_bootstrap import status as sric_runtime_status

app = typer.Typer(
    name="exposuredna",
    help="Organization Security DNA — explainable security knowledge graph.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
    rich_markup_mode=None,
)


def rd() -> Path:
    return Path.home() / ".exposuredna" / "workspaces"


def wp(name: str, root: Path) -> Path:
    return root / name


@app.command()
def version() -> None:
    """Print the installed Exposure DNA version."""
    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check runtime compatibility and privacy-safe defaults."""
    plugin_path = Path.home() / ".sric" / "plugins"
    plugins = PluginRegistry(plugin_path).list()
    runtime = sric_runtime_status()
    checks = {
        "python": {"ok": sys.version_info >= (3, 11), "version": sys.version.split()[0]},
        "sric": {"ok": runtime.compatible, "version": runtime.version, "required": ">=0.5.11,<0.6", "missing_modules": list(runtime.missing_modules), "reasons": list(runtime.reasons)},
        "ai": {"ok": True, "mode": "disabled", "cloud_uploads": False},
        "plugins": {"ok": True, "count": len(plugins), "path": str(plugin_path)},
        "privacy": {"ok": True, "telemetry": False},
    }
    ok = all(bool(item["ok"]) for item in checks.values())
    typer.echo(json.dumps({"ok": ok, "checks": checks}, indent=2))
    if not ok:
        raise typer.Exit(1)


@app.command()
def init(name: str, organization: str, root: Path = typer.Option(rd(), "--root")) -> None:
    """Create a local workspace and set its organization identity."""
    root.mkdir(parents=True, exist_ok=True)
    workspace = Workspace.create(root, name)
    ExposureEngine(workspace.root).set_organization(organization)
    typer.echo(str(workspace.root))


@app.command("workspace")
def workspace_command(
    action: str = typer.Argument("list", help="create|list|show|archive"),
    name: Optional[str] = typer.Argument(None),
    root: Path = typer.Option(rd(), "--root"),
    confirm: bool = typer.Option(False, "--confirm", help="Required for archive."),
) -> None:
    """Create, list, inspect or archive local workspaces."""
    root.mkdir(parents=True, exist_ok=True)
    action = action.lower()
    if action == "list":
        typer.echo(json.dumps({"workspaces": sorted(path.name for path in root.iterdir() if path.is_dir() and (path / "workspace.json").is_file())}, indent=2))
        return
    if not name:
        typer.echo(f"workspace {action} requires NAME", err=True)
        raise typer.Exit(2)
    target = wp(name, root)
    if action == "create":
        workspace = Workspace.create(root, name)
        ExposureEngine(workspace.root)
        typer.echo(str(workspace.root))
        return
    if action == "show":
        workspace = Workspace.open(target)
        metadata = json.loads((workspace.root / "workspace.json").read_text(encoding="utf-8"))
        typer.echo(json.dumps({"path": str(workspace.root), "metadata": metadata}, indent=2))
        return
    if action == "archive":
        if not confirm:
            typer.echo("workspace archive requires --confirm; no data was changed", err=True)
            raise typer.Exit(5)
        Workspace.open(target)
        archive_root = root / "archived"
        archive_root.mkdir(exist_ok=True)
        destination = archive_root / name
        if destination.exists():
            typer.echo("archive destination already exists; no data was changed", err=True)
            raise typer.Exit(2)
        target.rename(destination)
        typer.echo(str(destination))
        return
    typer.echo(f"Unknown workspace action: {action}", err=True)
    raise typer.Exit(2)


@app.command("config")
def config_command(
    action: str = typer.Argument("show", help="show|explain"),
    key: Optional[str] = typer.Argument(None),
    workspace: Optional[str] = typer.Option(None, "--workspace"),
    root: Path = typer.Option(rd(), "--root"),
) -> None:
    """Show privacy defaults and their effective source."""
    values = {"telemetry": False, "cloud_ai": False, "external_uploads": False}
    sources = {name: "secure default" for name in values}
    if workspace:
        metadata_path = wp(workspace, root) / "workspace.json"
        if not metadata_path.is_file():
            typer.echo("workspace.json not found", err=True)
            raise typer.Exit(2)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        for name in values:
            if name in metadata:
                values[name] = metadata[name]
                sources[name] = f"workspace config: {metadata_path}"
    if action == "show":
        typer.echo(json.dumps({"values": values, "sources": sources}, indent=2))
        return
    if action == "explain":
        if not key or key not in values:
            typer.echo("config explain requires one of: " + ", ".join(sorted(values)), err=True)
            raise typer.Exit(2)
        typer.echo(json.dumps({"key": key, "value": values[key], "source": sources[key]}, indent=2))
        return
    typer.echo(f"Unknown config action: {action}", err=True)
    raise typer.Exit(2)


from . import cli_analysis as _cli_analysis  # noqa: E402,F401
from . import cli_resolution as _cli_resolution  # noqa: E402,F401
from . import cli_runtime as _cli_runtime  # noqa: E402,F401


@app.command("help", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def help_command(ctx: typer.Context, command: Optional[str] = typer.Argument(None)) -> None:
    """Show root or top-level command help."""
    if not command:
        typer.echo(ctx.parent.get_help() if ctx.parent else ctx.get_help())
        return
    root = ctx.parent.command if ctx.parent else app
    if hasattr(root, "commands") and command in root.commands:
        typer.echo(root.commands[command].get_help(ctx))
        return
    typer.echo(f"Unknown command: {command}", err=True)
    raise typer.Exit(2)


def run() -> None:
    """Console entrypoint supporting `exposuredna COMMAND help`."""
    if len(sys.argv) >= 3 and sys.argv[-1] == "help" and sys.argv[1] != "help":
        sys.argv[-1] = "--help"
    app()

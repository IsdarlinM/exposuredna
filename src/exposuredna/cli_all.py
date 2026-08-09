from __future__ import annotations

import typer
from sric.cli_style import CLIBrand, configure_cli_context, no_color_option, run_branded_cli

from . import __version__
from . import cli_eras as _cli_eras  # noqa: F401
from . import cli_interchange as _cli_interchange  # noqa: F401
from . import cli_runtime as _runtime
from .cli import app
from . import cli_capabilities as _cli_capabilities  # noqa: F401
from . import cli_update as _cli_update  # noqa: F401,E402


def _create_complete_app(*args: object, **kwargs: object) -> object:
    from .api_all import create_app

    return create_app(*args, **kwargs)


_runtime.create_app = _create_complete_app

__all__ = ["BRAND", "app", "normalize_help_argv", "run"]

BRAND = CLIBrand(product="Exposure DNA", description="Correlate organization security relationships across time with evidence.", version=__version__)
app.rich_markup_mode = "rich"


@app.callback()
def branded_main(ctx: typer.Context, no_color: bool = no_color_option()) -> None:
    """Exposure DNA CLI presentation controls."""
    configure_cli_context(ctx, no_color=no_color)


def normalize_help_argv(argv: list[str]) -> list[str]:
    """Normalize trailing `help` for root and nested Exposure DNA commands."""
    normalized = list(argv)
    if len(normalized) >= 3 and normalized[-1] == "help" and normalized[1] != "help":
        normalized[-1] = "--help"
    return normalized


def run() -> None:
    """Console entrypoint including the branded CLI and local Web/API."""
    run_branded_cli(app, BRAND, argv_normalizer=normalize_help_argv)

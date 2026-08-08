from __future__ import annotations

import sys

from . import cli_eras as _cli_eras  # noqa: F401
from . import cli_interchange as _cli_interchange  # noqa: F401
from . import cli_runtime as _runtime
from .api_vnext import create_app as create_vnext_app
from .cli import app

_runtime.create_app = create_vnext_app

__all__ = ["app", "normalize_help_argv", "run"]


def normalize_help_argv(argv: list[str]) -> list[str]:
    """Normalize trailing `help` for root and nested Exposure DNA commands."""
    normalized = list(argv)
    if len(normalized) >= 3 and normalized[-1] == "help" and normalized[1] != "help":
        normalized[-1] = "--help"
    return normalized


def run() -> None:
    """Console entrypoint including every public Exposure DNA command and vNext Web/API."""
    sys.argv[:] = normalize_help_argv(sys.argv)
    app()

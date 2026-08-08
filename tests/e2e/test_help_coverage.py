from typer.main import get_command
from typer.testing import CliRunner
from exposuredna.cli_all import app


def test_every_registered_top_level_command_has_dash_help() -> None:
    runner = CliRunner()
    group = get_command(app)
    assert hasattr(group, "commands")
    for name in group.commands:  # type: ignore[attr-defined]
        assert runner.invoke(app, [name, "--help"]).exit_code == 0, name
        assert runner.invoke(app, [name, "-h"]).exit_code == 0, name

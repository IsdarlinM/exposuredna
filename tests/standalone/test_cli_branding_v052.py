from typer.main import get_command

from exposuredna.cli_all import BRAND, app
from sric.cli_style import build_banner


def test_exposure_dna_brand_identity() -> None:
    banner = build_banner(BRAND)
    assert "Exposure DNA" in banner
    assert "organization security relationships" in banner
    assert "IsdarlinM :: v0.5.2" in banner


def test_no_color_option_is_registered() -> None:
    command = get_command(app)
    assert any("--no-color" in getattr(param, "opts", ()) for param in command.params)

from typer.testing import CliRunner
from exposuredna.cli import app

def test_collect_passive()->None:
    r=CliRunner().invoke(app,["collect"]); assert r.exit_code==0; assert "no unbounded external collection" in r.stdout

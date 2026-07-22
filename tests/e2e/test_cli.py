from typer.testing import CliRunner
from exposuredna.cli import app
r=CliRunner()
def test_help()->None:
    for args in [["--help"],["-h"],["help"],["correlate","--help"]]: assert r.invoke(app,args).exit_code==0

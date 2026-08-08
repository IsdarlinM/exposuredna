import json
from pathlib import Path

from typer.testing import CliRunner

from exposuredna.cli_all import app

runner = CliRunner()


def test_relationship_at_cli_returns_unknown_outside_interval(tmp_path: Path) -> None:
    path = tmp_path / "relationship.json"
    path.write_text(
        json.dumps(
            {
                "relationship_id": "rel-1",
                "subject_id": "org-a",
                "object_id": "asset-a",
                "relationship_type": "OWNS",
                "valid_from": "2021-01-01T00:00:00Z",
                "valid_to": "2023-12-31T00:00:00Z",
                "status": "INFERRED",
            }
        ),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["relationship-at", str(path), "--at", "2026-08-08T00:00:00Z"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["view"]["active"] is False
    assert payload["view"]["status"] == "UNKNOWN"

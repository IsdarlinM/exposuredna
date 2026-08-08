from pathlib import Path

from fastapi.testclient import TestClient

from exposuredna.api_vnext import create_app


def test_historical_relationship_api_does_not_project_forward(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    response = client.post(
        "/api/v1/analysis/relationships/at",
        json={
            "relationship": {
                "relationship_id": "rel-1",
                "subject_id": "org-a",
                "object_id": "asset-a",
                "relationship_type": "OWNS",
                "valid_from": "2021-01-01T00:00:00Z",
                "valid_to": "2023-12-31T00:00:00Z",
                "status": "INFERRED",
                "evidence_ids": ["ev-1"],
            },
            "at": "2026-08-08T00:00:00Z",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["view"]["active"] is False
    assert payload["view"]["status"] == "UNKNOWN"
    assert payload["ownership_validated"] is False
    assert payload["historical_relationship_projected_forward"] is False

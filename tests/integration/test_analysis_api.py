from fastapi.testclient import TestClient

from exposuredna.api_vnext import create_app


def test_resolution_api_never_validates_ownership() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/resolution/evaluate",
        json={
            "candidate_id": "C-1",
            "subject_id": "org-a",
            "object_id": "asset-a",
            "proposed_relationship": "OWNS",
            "signals": [
                {
                    "signal_id": "shared-cloud",
                    "signal_type": "asn",
                    "contribution": -0.8,
                    "reason": "Shared cloud ASN",
                    "source_id": "source-1",
                    "evidence_ids": ["E-1"],
                    "direct_observation": True,
                    "specificity": 0.2,
                    "exclusivity": 0.1,
                    "negative_constraint": "CDN_OR_CLOUD",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate"]["status"] == "UNKNOWN"
    assert payload["ownership_validated"] is False
    assert payload["validated_findings_created"] == 0


def test_snapshot_api_has_no_risk_score() -> None:
    client = TestClient(create_app())
    before = {
        "snapshot_id": "S-1",
        "organization_id": "org-1",
        "captured_at": "2026-01-01T00:00:00Z",
        "entities": [],
        "relationships": [],
    }
    after = {
        "snapshot_id": "S-2",
        "organization_id": "org-1",
        "captured_at": "2026-02-01T00:00:00Z",
        "entities": [
            {
                "entity_id": "D-1",
                "entity_type": "domain",
                "canonical_value": "example.test",
                "status": "OBSERVED",
                "evidence_ids": ["E-D1"],
            }
        ],
        "relationships": [],
    }
    response = client.post(
        "/api/v1/analysis/snapshots/diff",
        json={"before": before, "after": after},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_score"] is None
    assert payload["ownership_validated"] is False
    assert payload["diff"]["summary"]["ADDED"] == 1


def test_lineage_api_does_not_infer_current_ownership() -> None:
    client = TestClient(create_app())
    snapshot = {
        "snapshot_id": "S-1",
        "organization_id": "org-1",
        "captured_at": "2026-01-01T00:00:00Z",
        "entities": [
            {
                "entity_id": "ORG-A",
                "entity_type": "organization",
                "canonical_value": "org-a",
                "status": "OBSERVED",
                "evidence_ids": ["E-A"],
            },
            {
                "entity_id": "ORG-B",
                "entity_type": "organization",
                "canonical_value": "org-b",
                "status": "OBSERVED",
                "evidence_ids": ["E-B"],
            },
        ],
        "relationships": [
            {
                "relationship_id": "R-1",
                "source_entity_id": "ORG-A",
                "target_entity_id": "ORG-B",
                "relationship_type": "ACQUIRED",
                "status": "INFERRED",
                "valid_from": "2020-01-01T00:00:00Z",
                "evidence_ids": ["E-R1"],
            }
        ],
    }
    response = client.post(
        "/api/v1/analysis/lineage/acquisitions",
        json={"snapshots": [snapshot]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["relationships"]) == 1
    assert payload["current_ownership_inferred"] is False

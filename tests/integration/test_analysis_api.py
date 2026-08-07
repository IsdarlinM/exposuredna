from fastapi.testclient import TestClient

from exposuredna.api_vnext import create_app


def snapshot_payload(snapshot_id: str = "S-1", organization_id: str = "org-1") -> dict[str, object]:
    return {
        "snapshot_id": snapshot_id,
        "organization_id": organization_id,
        "captured_at": "2026-01-01T00:00:00Z",
        "entities": [
            {
                "entity_id": "ORG",
                "entity_type": "organization",
                "canonical_value": "org",
                "status": "OBSERVED",
                "evidence_ids": ["E-ORG"],
            },
            {
                "entity_id": "D-1",
                "entity_type": "domain",
                "canonical_value": "one.test",
                "status": "OBSERVED",
                "evidence_ids": ["E-D1"],
            },
            {
                "entity_id": "D-2",
                "entity_type": "domain",
                "canonical_value": "two.test",
                "status": "OBSERVED",
                "evidence_ids": ["E-D2"],
            },
        ],
        "relationships": [
            {
                "relationship_id": "R-1",
                "source_entity_id": "ORG",
                "target_entity_id": "D-1",
                "relationship_type": "POSSIBLY_RELATED",
                "status": "INFERRED",
                "evidence_ids": ["E-R1"],
            },
            {
                "relationship_id": "R-2",
                "source_entity_id": "ORG",
                "target_entity_id": "D-2",
                "relationship_type": "POSSIBLY_RELATED",
                "status": "INFERRED",
                "evidence_ids": ["E-R2"],
            },
        ],
    }


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
        "snapshot_id": "S-0",
        "organization_id": "org-1",
        "captured_at": "2025-12-01T00:00:00Z",
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


def test_snapshot_diff_cross_organization_is_controlled_422() -> None:
    client = TestClient(create_app())
    before = snapshot_payload("S-A", "org-a")
    after = snapshot_payload("S-B", "org-b")
    response = client.post(
        "/api/v1/analysis/snapshots/diff",
        json={"before": before, "after": after},
    )
    assert response.status_code == 422
    assert "same organization" in response.text


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


def test_snapshot_export_api_preserves_inferred_status_without_persistence() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/snapshots/export",
        json={"snapshot": snapshot_payload(), "format": "jsonld"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert '"POSSIBLY_RELATED"' in payload["content"]
    assert '"INFERRED"' in payload["content"]
    assert payload["ownership_validated"] is False
    assert payload["persisted"] is False


def test_resolution_plan_requires_approval_and_never_persists() -> None:
    client = TestClient(create_app())
    plan = {
        "plan_id": "P-1",
        "merges": [
            {
                "target_entity_id": "D-1",
                "source_entity_ids": ["D-2"],
                "reason": "Potential duplicate",
            }
        ],
        "human_approved": False,
        "dry_run": True,
    }
    denied = client.post(
        "/api/v1/analysis/resolution/plan",
        json={"snapshot": snapshot_payload(), "plan": plan},
    )
    assert denied.status_code == 403

    plan["human_approved"] = True
    response = client.post(
        "/api/v1/analysis/resolution/plan",
        json={"snapshot": snapshot_payload(), "plan": plan},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["applied"] is False
    assert payload["persisted"] is False
    assert payload["ownership_validated"] is False
    assert {item["entity_id"] for item in payload["result"]["after_snapshot"]["entities"]} == {
        "ORG",
        "D-1",
    }


def test_resolution_rollback_rejects_invalid_token_without_500() -> None:
    client = TestClient(create_app())
    plan = {
        "plan_id": "P-1",
        "merges": [
            {
                "target_entity_id": "D-1",
                "source_entity_ids": ["D-2"],
                "reason": "Potential duplicate",
            }
        ],
        "human_approved": True,
        "dry_run": True,
    }
    prepared = client.post(
        "/api/v1/analysis/resolution/plan",
        json={"snapshot": snapshot_payload(), "plan": plan},
    )
    assert prepared.status_code == 200
    result = prepared.json()["result"]
    response = client.post(
        "/api/v1/analysis/resolution/rollback",
        json={"result": result, "rollback_token": "bad"},
    )
    assert response.status_code == 403

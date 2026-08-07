import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from exposuredna.api_vnext import create_app


def client() -> TestClient:
    return TestClient(create_app(Path(tempfile.mkdtemp(prefix="exposuredna-api-"))))


def snapshot_payload(snapshot_id: str = "S-1", organization_id: str = "org-1") -> dict[str, object]:
    return {
        "snapshot_id": snapshot_id,
        "organization_id": organization_id,
        "captured_at": "2026-01-01T00:00:00Z",
        "entities": [
            {"entity_id": "ORG", "entity_type": "organization", "canonical_value": "org", "status": "OBSERVED", "evidence_ids": ["E-ORG"]},
            {"entity_id": "D-1", "entity_type": "domain", "canonical_value": "one.test", "status": "OBSERVED", "evidence_ids": ["E-D1"]},
            {"entity_id": "D-2", "entity_type": "domain", "canonical_value": "two.test", "status": "OBSERVED", "evidence_ids": ["E-D2"]},
        ],
        "relationships": [
            {"relationship_id": "R-1", "source_entity_id": "ORG", "target_entity_id": "D-1", "relationship_type": "POSSIBLY_RELATED", "status": "INFERRED", "evidence_ids": ["E-R1"]},
            {"relationship_id": "R-2", "source_entity_id": "ORG", "target_entity_id": "D-2", "relationship_type": "POSSIBLY_RELATED", "status": "INFERRED", "evidence_ids": ["E-R2"]},
        ],
    }


def test_vnext_web_root_and_security_headers() -> None:
    response = client().get("/")
    assert response.status_code == 200
    assert "Exposure DNA" in response.text
    assert "default-src 'self'" in response.headers["content-security-policy"]


def test_resolution_api_never_validates_ownership() -> None:
    response = client().post(
        "/api/v1/analysis/resolution/evaluate",
        json={
            "candidate_id": "C-1",
            "subject_id": "org-a",
            "object_id": "asset-a",
            "proposed_relationship": "OWNS",
            "signals": [{
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
            }],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate"]["status"] == "UNKNOWN"
    assert payload["ownership_validated"] is False
    assert payload["validated_findings_created"] == 0


def test_snapshot_diff_has_no_risk_score_and_cross_org_is_422() -> None:
    api = client()
    before = {"snapshot_id": "S-0", "organization_id": "org-1", "captured_at": "2025-12-01T00:00:00Z", "entities": [], "relationships": []}
    after = {"snapshot_id": "S-2", "organization_id": "org-1", "captured_at": "2026-02-01T00:00:00Z", "entities": [{"entity_id": "D-1", "entity_type": "domain", "canonical_value": "example.test", "status": "OBSERVED", "evidence_ids": ["E-D1"]}], "relationships": []}
    response = api.post("/api/v1/analysis/snapshots/diff", json={"before": before, "after": after})
    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_score"] is None
    assert payload["ownership_validated"] is False
    assert payload["diff"]["summary"]["ADDED"] == 1

    bad = api.post(
        "/api/v1/analysis/snapshots/diff",
        json={"before": snapshot_payload("S-A", "org-a"), "after": snapshot_payload("S-B", "org-b")},
    )
    assert bad.status_code == 422


def test_snapshot_export_preserves_inferred_status_without_persistence() -> None:
    response = client().post(
        "/api/v1/analysis/snapshots/export",
        json={"snapshot": snapshot_payload(), "format": "jsonld"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert '"POSSIBLY_RELATED"' in payload["content"]
    assert '"INFERRED"' in payload["content"]
    assert payload["ownership_validated"] is False
    assert payload["persisted"] is False


def test_resolution_plan_requires_approval_previews_changes_and_never_persists() -> None:
    api = client()
    plan: dict[str, object] = {
        "plan_id": "P-1",
        "merges": [{"target_entity_id": "D-1", "source_entity_ids": ["D-2"], "reason": "Potential duplicate"}],
        "human_approved": False,
        "dry_run": True,
    }
    denied = api.post("/api/v1/analysis/resolution/plan", json={"snapshot": snapshot_payload(), "plan": plan})
    assert denied.status_code == 403

    plan["human_approved"] = True
    response = api.post("/api/v1/analysis/resolution/plan", json={"snapshot": snapshot_payload(), "plan": plan})
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["applied"] is False
    assert payload["persisted"] is False
    assert payload["ownership_validated"] is False
    assert {item["entity_id"] for item in payload["result"]["after_snapshot"]["entities"]} == {"ORG", "D-1"}


def test_resolution_rollback_rejects_invalid_token_without_500() -> None:
    api = client()
    plan = {
        "plan_id": "P-1",
        "merges": [{"target_entity_id": "D-1", "source_entity_ids": ["D-2"], "reason": "Potential duplicate"}],
        "human_approved": True,
        "dry_run": True,
    }
    prepared = api.post("/api/v1/analysis/resolution/plan", json={"snapshot": snapshot_payload(), "plan": plan})
    assert prepared.status_code == 200
    response = api.post(
        "/api/v1/analysis/resolution/rollback",
        json={"result": prepared.json()["result"], "rollback_token": "bad"},
    )
    assert response.status_code == 403

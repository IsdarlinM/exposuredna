import pytest

from exposuredna.resolution import (
    HumanResolutionDecision,
    NegativeConstraint,
    RelationshipType,
    ResolutionReview,
    ResolutionSignal,
    apply_human_review,
    evaluate_resolution,
)
from sric.models import ClaimStatus


def signal(
    signal_id: str,
    *,
    contribution: float = 0.7,
    source: str | None = None,
    group: str | None = None,
    exclusivity: float = 0.9,
    specificity: float = 0.9,
    constraint: NegativeConstraint | None = None,
) -> ResolutionSignal:
    return ResolutionSignal(
        signal_id=signal_id,
        signal_type="test-signal",
        contribution=contribution,
        reason="test evidence",
        source_id=source or signal_id,
        source_group=group,
        evidence_ids=[f"E-{signal_id}"],
        direct_observation=True,
        source_quality=1.0,
        specificity=specificity,
        exclusivity=exclusivity,
        negative_constraint=constraint,
    )


def test_similarity_without_specific_signal_remains_unknown() -> None:
    candidate = evaluate_resolution(
        candidate_id="C-1",
        subject_id="org-a",
        object_id="asset-a",
        proposed_relationship=RelationshipType.OWNS,
        signals=[signal("generic", exclusivity=0.2, specificity=0.3)],
    )

    assert candidate.status is ClaimStatus.UNKNOWN
    assert "specific and exclusive relationship signal" in candidate.missing_evidence
    assert candidate.ownership_claimed is False


def test_shared_cloud_signal_blocks_ownership() -> None:
    candidate = evaluate_resolution(
        candidate_id="C-2",
        subject_id="org-a",
        object_id="ip-a",
        proposed_relationship=RelationshipType.OWNS,
        signals=[
            signal("positive"),
            signal(
                "cloud",
                contribution=-0.8,
                constraint=NegativeConstraint.CDN_OR_CLOUD,
            ),
        ],
    )

    assert candidate.status is ClaimStatus.UNKNOWN
    assert NegativeConstraint.CDN_OR_CLOUD in candidate.negative_constraints
    assert candidate.ownership_claimed is False


def test_historical_ownership_does_not_prove_current_ownership() -> None:
    candidate = evaluate_resolution(
        candidate_id="C-3",
        subject_id="org-a",
        object_id="domain-a",
        proposed_relationship=RelationshipType.OWNS,
        signals=[
            signal("historic-positive"),
            signal(
                "historic-only",
                contribution=-0.6,
                constraint=NegativeConstraint.HISTORICAL_OWNERSHIP_ONLY,
            ),
        ],
    )

    assert candidate.status is ClaimStatus.UNKNOWN
    assert any("Historical ownership" in item for item in candidate.alternative_explanations)


def test_specific_non_ownership_relationship_can_remain_inferred() -> None:
    candidate = evaluate_resolution(
        candidate_id="C-4",
        subject_id="application-a",
        object_id="oauth-provider-a",
        proposed_relationship=RelationshipType.USES,
        signals=[signal("issuer-match")],
    )

    assert candidate.status is ClaimStatus.INFERRED
    assert candidate.confidence <= 0.74
    assert candidate.ownership_claimed is False


def test_duplicate_sources_do_not_count_as_independent() -> None:
    candidate = evaluate_resolution(
        candidate_id="C-5",
        subject_id="org-a",
        object_id="asset-a",
        proposed_relationship=RelationshipType.POSSIBLY_RELATED,
        signals=[
            signal("one", source="feed-a", group="same-upstream"),
            signal("two", source="feed-b", group="same-upstream"),
        ],
    )

    assert candidate.duplicate_source_groups == ["same-upstream"]
    assert any("same upstream" in item for item in candidate.alternative_explanations)


def test_negative_constraint_cannot_be_positive() -> None:
    with pytest.raises(ValueError, match="cannot have positive contribution"):
        signal("invalid", contribution=0.5, constraint=NegativeConstraint.SHARED_HOSTING)


def test_human_review_cannot_validate_ownership() -> None:
    candidate = evaluate_resolution(
        candidate_id="C-6",
        subject_id="org-a",
        object_id="asset-a",
        proposed_relationship=RelationshipType.OWNS,
        signals=[signal("authoritative")],
    )
    review = apply_human_review(
        candidate,
        decision=HumanResolutionDecision.ACCEPT_AS_INFERRED,
        reviewer="analyst",
        reason="Evidence supports retaining the candidate as an inference.",
    )

    assert review.resulting_status is ClaimStatus.INFERRED
    with pytest.raises(ValueError, match="cannot create VALIDATED ownership"):
        ResolutionReview(
            candidate_id="C-6",
            decision=HumanResolutionDecision.ACCEPT_AS_INFERRED,
            reviewer="analyst",
            reason="invalid",
            resulting_status=ClaimStatus.VALIDATED,
        )


def test_domain_transfer_counter_signal_blocks_current_ownership() -> None:
    candidate = evaluate_resolution(
        candidate_id="C-7",
        subject_id="former-org",
        object_id="domain-a",
        proposed_relationship=RelationshipType.OWNS,
        signals=[
            signal("old-whois"),
            signal(
                "transfer",
                contribution=-1.0,
                constraint=NegativeConstraint.DOMAIN_TRANSFER,
            ),
        ],
    )

    assert candidate.status is ClaimStatus.UNKNOWN
    assert NegativeConstraint.DOMAIN_TRANSFER in candidate.negative_constraints

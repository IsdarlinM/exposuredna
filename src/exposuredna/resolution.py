from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.calibration import ConfidenceSignal, score_confidence, skeptic_review
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RelationshipType(StrEnum):
    OWNS = "OWNS"
    OPERATES = "OPERATES"
    HOSTS = "HOSTS"
    USES = "USES"
    DEVELOPED_BY = "DEVELOPED_BY"
    PUBLISHED_BY = "PUBLISHED_BY"
    ACQUIRED = "ACQUIRED"
    FORMERLY_OWNED = "FORMERLY_OWNED"
    SHARED_WITH = "SHARED_WITH"
    POSSIBLY_RELATED = "POSSIBLY_RELATED"


class NegativeConstraint(StrEnum):
    SHARED_HOSTING = "SHARED_HOSTING"
    SHARED_ASN = "SHARED_ASN"
    CDN_OR_CLOUD = "CDN_OR_CLOUD"
    WILDCARD_CERTIFICATE = "WILDCARD_CERTIFICATE"
    COMMON_ANALYTICS_ID = "COMMON_ANALYTICS_ID"
    COMMON_OAUTH_PROVIDER = "COMMON_OAUTH_PROVIDER"
    REPOSITORY_FORK = "REPOSITORY_FORK"
    COPIED_CODE = "COPIED_CODE"
    WHITE_LABEL_APPLICATION = "WHITE_LABEL_APPLICATION"
    OUTSOURCED_DEVELOPMENT = "OUTSOURCED_DEVELOPMENT"
    PACKAGE_NAMESPACE_COLLISION = "PACKAGE_NAMESPACE_COLLISION"
    HISTORICAL_OWNERSHIP_ONLY = "HISTORICAL_OWNERSHIP_ONLY"
    DOMAIN_TRANSFER = "DOMAIN_TRANSFER"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"


class ResolutionSignal(BaseModel):
    """Explainable positive or negative entity-resolution evidence."""

    model_config = ConfigDict(extra="forbid")

    signal_id: str
    signal_type: str
    contribution: float = Field(ge=-1.0, le=1.0)
    reason: str
    source_id: str
    source_group: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    observed_at: datetime = Field(default_factory=utcnow)
    direct_observation: bool = False
    source_quality: float = Field(default=0.5, ge=0.0, le=1.0)
    specificity: float = Field(default=0.5, ge=0.0, le=1.0)
    exclusivity: float = Field(default=0.5, ge=0.0, le=1.0)
    temporal_half_life_days: int = Field(default=365, ge=1, le=36500)
    negative_constraint: NegativeConstraint | None = None
    counter_evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_semantics(self) -> "ResolutionSignal":
        if self.direct_observation and not self.evidence_ids:
            raise ValueError("direct observations require evidence_ids")
        if self.negative_constraint is not None and self.contribution > 0:
            raise ValueError("negative constraints cannot have positive contribution")
        return self

    def confidence_signal(self) -> ConfidenceSignal:
        return ConfidenceSignal(
            signal=self.signal_type,
            contribution=self.contribution * self.exclusivity,
            reason=self.reason,
            source_id=self.source_id,
            source_group=self.source_group,
            evidence_ids=self.evidence_ids,
            observed_at=self.observed_at,
            direct_observation=self.direct_observation,
            source_quality=self.source_quality,
            specificity=self.specificity,
            temporal_half_life_days=self.temporal_half_life_days,
        )


class ResolutionCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    subject_id: str
    object_id: str
    proposed_relationship: RelationshipType
    status: ClaimStatus
    confidence: float = Field(ge=0.0, le=1.0)
    signal_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    negative_constraints: list[NegativeConstraint] = Field(default_factory=list)
    duplicate_source_groups: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    skeptic_verdict: str
    ownership_claimed: bool = False
    human_review_required: bool = True


class HumanResolutionDecision(StrEnum):
    ACCEPT_AS_INFERRED = "ACCEPT_AS_INFERRED"
    REJECT = "REJECT"
    DEFER = "DEFER"
    MERGE_ENTITIES = "MERGE_ENTITIES"
    SPLIT_ENTITIES = "SPLIT_ENTITIES"


class ResolutionReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    decision: HumanResolutionDecision
    reviewer: str
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)
    reviewed_at: datetime = Field(default_factory=utcnow)
    resulting_status: ClaimStatus

    @model_validator(mode="after")
    def review_cannot_validate_ownership(self) -> "ResolutionReview":
        if self.resulting_status is ClaimStatus.VALIDATED:
            raise ValueError("entity-resolution review cannot create VALIDATED ownership")
        return self


_OWNERSHIP_BLOCKERS = {
    NegativeConstraint.SHARED_HOSTING,
    NegativeConstraint.SHARED_ASN,
    NegativeConstraint.CDN_OR_CLOUD,
    NegativeConstraint.WILDCARD_CERTIFICATE,
    NegativeConstraint.COMMON_ANALYTICS_ID,
    NegativeConstraint.COMMON_OAUTH_PROVIDER,
    NegativeConstraint.REPOSITORY_FORK,
    NegativeConstraint.COPIED_CODE,
    NegativeConstraint.WHITE_LABEL_APPLICATION,
    NegativeConstraint.OUTSOURCED_DEVELOPMENT,
    NegativeConstraint.PACKAGE_NAMESPACE_COLLISION,
    NegativeConstraint.HISTORICAL_OWNERSHIP_ONLY,
    NegativeConstraint.DOMAIN_TRANSFER,
    NegativeConstraint.TEMPORAL_CONFLICT,
}


def evaluate_resolution(
    *,
    candidate_id: str,
    subject_id: str,
    object_id: str,
    proposed_relationship: RelationshipType,
    signals: Sequence[ResolutionSignal],
) -> ResolutionCandidate:
    """Evaluate entity resolution without asserting ownership from similarity."""

    negative_constraints = sorted(
        {signal.negative_constraint for signal in signals if signal.negative_constraint},
        key=lambda item: item.value,
    )
    evidence_ids = sorted({value for signal in signals for value in signal.evidence_ids})
    counter_ids = sorted(
        {value for signal in signals for value in signal.counter_evidence_ids}
    )
    positive = [signal for signal in signals if signal.contribution > 0]
    exclusive_positive = [
        signal
        for signal in positive
        if signal.exclusivity >= 0.75 and signal.specificity >= 0.75
    ]

    groups: dict[str, int] = {}
    for signal in signals:
        group = signal.source_group or signal.source_id
        groups[group] = groups.get(group, 0) + 1
    duplicates = sorted(group for group, count in groups.items() if count > 1)

    missing: list[str] = []
    alternatives: list[str] = []
    if not positive:
        missing.append("positive relationship evidence")
    if not exclusive_positive:
        missing.append("specific and exclusive relationship signal")
    if duplicates:
        alternatives.append(
            "Multiple signals may derive from the same upstream source rather than independent confirmation."
        )
    for constraint in negative_constraints:
        alternatives.append(
            {
                NegativeConstraint.SHARED_HOSTING: "The infrastructure may be shared by unrelated organizations.",
                NegativeConstraint.SHARED_ASN: "The ASN may belong to a hosting or cloud provider.",
                NegativeConstraint.CDN_OR_CLOUD: "The network signal may identify a CDN/cloud platform rather than an owner.",
                NegativeConstraint.WILDCARD_CERTIFICATE: "The certificate may cover unrelated tenants or catch-all names.",
                NegativeConstraint.COMMON_ANALYTICS_ID: "The analytics identifier may be reused by an agency or vendor.",
                NegativeConstraint.COMMON_OAUTH_PROVIDER: "A common OAuth issuer/provider does not imply organizational ownership.",
                NegativeConstraint.REPOSITORY_FORK: "Repository similarity may result from a fork.",
                NegativeConstraint.COPIED_CODE: "Code similarity may result from copying or shared open-source dependencies.",
                NegativeConstraint.WHITE_LABEL_APPLICATION: "The application may be a white-label deployment.",
                NegativeConstraint.OUTSOURCED_DEVELOPMENT: "A third-party developer may publish or operate the asset.",
                NegativeConstraint.PACKAGE_NAMESPACE_COLLISION: "The package namespace may be non-exclusive or colliding.",
                NegativeConstraint.HISTORICAL_OWNERSHIP_ONLY: "Historical ownership does not establish current ownership.",
                NegativeConstraint.DOMAIN_TRANSFER: "The domain or asset may have changed owners.",
                NegativeConstraint.TEMPORAL_CONFLICT: "The timestamps are incompatible with the proposed relationship.",
            }[constraint]
        )

    breakdown = score_confidence(
        [signal.confidence_signal() for signal in signals],
        base_confidence=0.03,
        maximum=0.74,
    )
    review = skeptic_review(
        breakdown,
        alternative_explanations=alternatives,
        counter_evidence_ids=counter_ids,
        missing_required_evidence=missing,
    )

    blocked_ownership = (
        proposed_relationship is RelationshipType.OWNS
        and bool(set(negative_constraints) & _OWNERSHIP_BLOCKERS)
    )
    if missing or blocked_ownership or not signals:
        status = ClaimStatus.UNKNOWN
        confidence = min(review.adjusted_confidence, 0.49)
    else:
        status = ClaimStatus.INFERRED
        confidence = min(review.adjusted_confidence, 0.74)

    # Similarity and correlation never create an ownership assertion. Even a
    # reviewed candidate remains an evidence-bearing inference.
    ownership_claimed = False
    if proposed_relationship is RelationshipType.OWNS and status is ClaimStatus.INFERRED:
        alternatives.append(
            "The candidate relationship is an ownership inference and requires stronger authoritative evidence."
        )

    return ResolutionCandidate(
        candidate_id=candidate_id,
        subject_id=subject_id,
        object_id=object_id,
        proposed_relationship=proposed_relationship,
        status=status,
        confidence=round(confidence, 6),
        signal_ids=sorted(signal.signal_id for signal in signals),
        evidence_ids=evidence_ids,
        counter_evidence_ids=counter_ids,
        negative_constraints=negative_constraints,
        duplicate_source_groups=duplicates,
        missing_evidence=sorted(set(missing)),
        alternative_explanations=sorted(set(alternatives)),
        skeptic_verdict=review.verdict.value,
        ownership_claimed=ownership_claimed,
    )


def apply_human_review(
    candidate: ResolutionCandidate,
    *,
    decision: HumanResolutionDecision,
    reviewer: str,
    reason: str,
    evidence_ids: Sequence[str] = (),
) -> ResolutionReview:
    if decision in {HumanResolutionDecision.REJECT, HumanResolutionDecision.SPLIT_ENTITIES}:
        status = ClaimStatus.REJECTED
    elif decision is HumanResolutionDecision.DEFER:
        status = ClaimStatus.UNKNOWN
    else:
        status = ClaimStatus.INFERRED
    return ResolutionReview(
        candidate_id=candidate.candidate_id,
        decision=decision,
        reviewer=reviewer,
        reason=reason,
        evidence_ids=sorted(set(evidence_ids)),
        resulting_status=status,
    )

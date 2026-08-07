# Entity resolution v2

Entity resolution proposes relationships; it does not prove ownership.

Each signal records its source, upstream source group, evidence, contribution, specificity, exclusivity, source quality, temporal relevance and counter-evidence. Mirrors and derived providers sharing one upstream origin are capped as one source group.

Negative constraints include shared hosting/ASN, CDN or cloud infrastructure, wildcard certificates, common analytics/OAuth providers, repository forks, copied code, white-label applications, outsourced development, namespace collisions, historical ownership, domain transfers and temporal conflicts.

Weak, ambiguous or ownership-blocked candidates remain `UNKNOWN`. A supported relationship may remain `INFERRED`, with all evidence and alternative explanations visible. Neither correlation nor human review may create `VALIDATED` ownership. Authoritative proof must enter through a separate evidence-backed validation workflow.

Human review supports accept-as-inferred, reject, defer, merge and split decisions. Every decision records the reviewer, reason, timestamp and evidence references.

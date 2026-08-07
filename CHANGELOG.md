# Changelog

## 0.3.0 - 2026-08-06
- Migrated the package requirement from SRIC 0.3 to SRIC 0.4.1.
- Added entity-resolution v2 with explainable positive and negative signal contributions.
- Added source-group deduplication, signal specificity, exclusivity, temporal decay and Skeptic review.
- Added explicit controls for shared hosting/ASN, CDN/cloud, wildcard certificates, common analytics/OAuth providers, forks, copied code, white-label applications, outsourced development, namespace collisions, historical ownership, domain transfers and temporal conflicts.
- Ownership similarity remains `UNKNOWN` or `INFERRED`; it never becomes `VALIDATED` through correlation or human review alone.
- Added audited human review outcomes that retain inference semantics and support reject/defer/merge/split decisions.
- Added tests for false ownership, duplicated upstream sources, historical ownership, domain transfers and review-state restrictions.
- Replaced hosted GitHub Actions/Dependabot automation with a local reproducible release gate.

## 0.2.0 - 2026-07-22
- Added explainable entity resolution with source-diversity and counter-evidence.
- Added evidence-completeness coverage by DNA dimension; this is never a risk score.
- Added organization/acquisition lineage, organization comparison without ownership claims, human-controlled resolution decisions, and cross-project correlation.
- Added passive adapters for CT, DNS, repositories, packages, OAuth, analytics, ASN, OpenAPI and mobile exports.
- Integrated SRIC 0.3 temporal graph, jobs/SSE, evidence lineage, notebook/search and content-addressed evidence storage.

## 0.1.0 - 2026-07-21
- Initial evidence-native Organization Security Knowledge Graph MVP.

# Changelog

## 0.5.5 - 2026-08-08
- Made the official Exposure DNA updater zero-config: `exposuredna update`, `exposuredna update --check`, and `exposuredna update --force` no longer require user-supplied manifest/key configuration.
- Delegated official update trust and immutable GitHub signed-commit validation to SRIC Core 0.5.5 while preserving same-version force reinstall and downgrade rejection.
- Kept `--manifest` plus `--public-key` as an explicit advanced custom/private-channel override.
- Updated the SRIC Core runtime floor, lock, and exact first-party pin to the signed SRIC 0.5.5 release commit.
- Added standalone regression coverage proving `exposuredna update --force` selects the official channel with no manifest/key.

## 0.5.4 - 2026-08-08
- Added the SRIC Web Command Console at `/console`, exposing the complete installed `exposuredna.cli_all` command tree without an operating-system shell.
- Added exact Web-catalog-to-CLI-tree regression coverage so future public CLI commands cannot silently disappear from the Web console.
- Preserved evidence, temporal and human-review semantics; Web invocation cannot convert correlation into validated ownership.
- Added fixed-runner `shell=False` execution, explicit mutation approval, secret redaction, cancellable jobs and real-time SSE output through SRIC Core 0.5.4.
- Updated package/runtime dependency metadata and the exact SRIC first-party pin to the 0.5.4 Web parity snapshot.

## 0.5.3 - 2026-08-08
- Added `exposuredna update --force` for explicit same-version reinstall of a trusted signed release using pip `--force-reinstall`.
- Preserved Ed25519 manifest verification, SHA-256 wheel verification, state backup and rollback behavior.
- `--force` may install the same or a newer signed release, never an older release; SemVer prerelease precedence is enforced by SRIC Core.
- `--check` and `--force` are mutually exclusive.
- Updated the SRIC Core runtime floor, lock and exact first-party source pin to 0.5.3.
- Added standalone regression coverage for the public `--force` CLI contract.

## 0.5.2 - 2026-08-08
- Added a subdued green interactive CLI banner ordered as `Exposure DNA :: v0.5.2`, `Developer: IsdarlinM`, then the product description.
- Added colorized Typer/Rich command help plus global `--no-color` and `NO_COLOR` support.
- Kept banner output on interactive stderr so JSON, graph exports and automation stdout remain clean.
- Added CLI branding regression tests and documentation.
- Updated the SRIC Core runtime floor, lock and first-party source pin to 0.5.2.

## 0.5.1 - 2026-08-08
- Fixed clean installation when `sric-core` is not published on PyPI.
- Added a first-party dependency manifest pinned to the exact SRIC Core 0.5.1 GitHub commit.
- Added a Python 3.11 runtime lock and made Windows/Linux installers bootstrap first-party dependencies before product installation.
- Preserved `SRIC_CORE_SOURCE` as an explicit development override.
- Updated the SRIC dependency floor to 0.5.1 and added standalone installer contract regression coverage.

## 0.5.0 - 2026-08-08
- Added Organization Era and temporal relationship modeling so historical ownership/operation evidence is bounded by explicit validity intervals.
- Added `relationship_at()` views that return `UNKNOWN` outside an evidenced time interval instead of propagating historical relationships into the present.
- Added conservative conflict detection for overlapping explicitly-exclusive ownership/operation claims; conflicts remain `UNKNOWN` and retain supporting/counter-evidence.
- Preserved the rule that temporal entity resolution cannot create `VALIDATED` ownership.
- Updated SRIC compatibility to the Sentinel Forge 0.5 release train.
- Added standalone capability discovery with no mandatory sibling-product dependencies.
- Reworked Linux/Windows installation to resolve SRIC 0.5 automatically and removed silent adjacent-repository discovery.
- Added standalone CLI/API/Web contracts, recursive parser/help tests, clean-install smokes and data-preserving Linux uninstall behavior.
- Added regression tests for historical relationship expiry and overlapping exclusive ownership claims.

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

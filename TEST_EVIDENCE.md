# Test Evidence — Exposure DNA v0.3.0

## Current validation status

**PENDING LOCAL RELEASE GATE.**

Exposure DNA v0.3.0 migrates the package to SRIC 0.4.1 and adds entity-resolution negative constraints, source-group deduplication, human review restrictions, organization snapshots, temporal diff, acquisition lineage and new CLI surfaces. Regression tests were added, but the complete repository suite has **not** been executed in the connector-only editing environment.

Do not tag, merge as a release, publish artifacts or describe v0.3.0 as validated until the exact commit produces `PASS` from:

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

Expected evidence:

```text
build/release-evidence/release-gate.json
```

The SRIC ecosystem gate must additionally confirm compatibility with SRIC 0.4.1.

## Previous baseline

Exposure DNA v0.2.0 did not include a root `TEST_EVIDENCE.md` equivalent to the other Sentinel Forge repositories. Therefore no previous test count is promoted here as a validated release baseline.

The existence of unit, integration, security, fuzz and E2E directories in v0.2.0 does not prove those suites ran. The v0.3.0 local release report is the first required release-level evidence for this repository.

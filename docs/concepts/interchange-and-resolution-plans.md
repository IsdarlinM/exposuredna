# Interchange and reversible entity-resolution plans

Exposure DNA 0.3.0 exports organization snapshots as deterministic evidence-bearing JSON-LD or GraphML. Status, evidence, counter-evidence and temporal relationship metadata are preserved. Export never upgrades an inferred relationship or validates ownership.

## Merge and split plans

Entity merge/split operations require explicit human approval. A plan can:

- merge evidence-compatible entities and rewire relationships;
- split one entity into at least two replacements;
- require a complete relationship-assignment map for splits;
- carry evidence and reviewer rationale;
- return a proposed snapshot without persisting it;
- create a rollback token restoring the complete prior snapshot.

`--apply` creates an approved result artifact only. The CLI/API do not mutate a workspace directly. Persistence must be transactional and controlled by the caller.

CLI:

```bash
exposuredna snapshot-export snapshot.json export.jsonld --format jsonld
exposuredna resolution-plan snapshot.json plan.json preview.json --approve
exposuredna resolution-plan snapshot.json plan.json result.json --approve --apply
exposuredna resolution-rollback result.json --rollback-token TOKEN --output restored.json
```

Loopback API:

```text
POST /api/v1/analysis/snapshots/export
POST /api/v1/analysis/resolution/plan
POST /api/v1/analysis/resolution/rollback
```

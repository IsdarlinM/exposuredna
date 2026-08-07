# Organization snapshots and temporal lineage

`OrganizationSnapshot` records an organization's observed/inferred entities and relationships at a specific collection time. It validates unique IDs, relationship endpoints and evidence requirements, then produces a deterministic SHA-256 content hash.

`diff_snapshots` reports added, removed, modified and optionally unchanged entities/relationships. It deliberately has no risk score. A removal can represent collection gaps rather than real retirement, and every change remains temporal evidence rather than proof of exposure, ownership or vulnerability.

`acquisition_lineage` extracts temporally ordered `ACQUIRED`, `FORMERLY_OWNED` and historical `OWNS` relationships, deduplicating repeated observations while retaining the richest evidence set. Historical relationships do not establish current ownership.

CLI examples:

```bash
exposuredna resolve-evaluate signals.json \
  --candidate-id C-1 --subject-id org-a --object-id asset-a \
  --relationship possibly_related

exposuredna snapshot-diff before.json after.json
exposuredna acquisition-lineage snapshots.json
```

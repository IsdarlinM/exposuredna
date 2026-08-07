# Analysis API

Run the extended local API on loopback:

```bash
python -m uvicorn exposuredna.api_vnext:create_app --factory --host 127.0.0.1 --port 8767
```

Additional endpoints:

```text
POST /api/v1/analysis/resolution/evaluate
POST /api/v1/analysis/snapshots/diff
POST /api/v1/analysis/lineage/acquisitions
```

Resolution endpoints never validate ownership. Snapshot diff deliberately has no risk score, and acquisition lineage never converts historical relationships into current ownership.

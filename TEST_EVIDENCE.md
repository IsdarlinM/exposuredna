# Test Evidence — Exposure DNA v0.3.0

## QA pass — 2026-08-07

Freshly executed in the current local runtime:

- Sentinel Forge cross-product high-risk regression matrix including Exposure DNA entity-resolution/rollback logic: **7/7 matrix tests passed**;
- Python `compileall` over the reconstructed corrected modules: **PASS**;
- branch comparison against `main`: branch is ahead and **0 commits behind** at the time of this audit.

Current-source review and regression coverage include:

- SRIC 0.4.1 compatibility;
- positive/negative entity-resolution evidence without automatic ownership validation;
- organization snapshot integrity and temporal diff without risk score;
- empty/ambiguous merge/split plan rejection;
- hostile existing merge metadata handling;
- self-loop prevention;
- dry-run returning the proposed graph preview without persistence;
- complete split relationship assignment and rollback-token validation;
- JSON-LD/GraphML export preserving evidence/status;
- snapshot export, guarded resolution plan and rollback endpoints in the workspace-bound vNext API;
- controlled 403/422 errors instead of server exceptions;
- complete CLI entrypoint registration for export/plan/rollback;
- `--apply` requiring `--approve` and controlled CLI file/model errors;
- recursive help-path coverage;
- `exposuredna web` serving the same vNext API and CSP-protected UI;
- public Python exports for snapshot/interchange/reversible resolution primitives.

## Current release-gate status

**FULL CURRENT REPOSITORY GATE NOT EXECUTABLE IN THIS RUNTIME.**

The private repository cannot be materialized as a complete local checkout from the connector, and Ruff, mypy, `build` and `pip-audit` are unavailable from the runtime/index. No GitHub Actions, Codespaces or paid/hosted GitHub execution was used.

Do not describe v0.3.0 as a fully validated release until the exact commit produces `PASS` from a complete local sibling checkout:

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

## Previous baseline

Exposure DNA v0.2.0 did not have an equivalent root release-evidence record. Existing historical unit/integration/security/fuzz/E2E files are not promoted as proof that the old full suite ran.

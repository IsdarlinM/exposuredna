# CLI Reference — exposuredna v0.2.0

All public commands support `COMMAND --help` and `COMMAND -h`; `exposuredna COMMAND help` is normalized to the same help path.

- `version` — print version.
- `doctor` — validate Python, SRIC, AI-disabled defaults and plugins.
- `init`, `workspace`, `config` — initialize/manage isolated workspaces and explain configuration.
- `add`, `relationship`, `import` — ingest explicit entities/relationships/JSON evidence.
- `collect` — passive adapter ingestion only (`ct`, `dns`, `repo`, `package`, `oauth`, `analytics`, `asn`, `openapi`, `mobile`).
- `entities`, `graph`, `timeline` — inspect the Organization Security Knowledge Graph.
- `correlate`, `explain`, `coverage` — explainable entity-resolution and evidence-completeness views.
- `lineage`, `compare-org`, `resolve`, `cross-correlate` — organization lineage, comparison without ownership claims, human resolution and sibling-product correlation.
- `export`, `report`, `demo` — export/report/offline synthetic demo.
- `web` — local Web UI; non-loopback binding refused by default.
- `evidence` — SRIC content-addressed evidence storage.
- `ai`, `plugins`, `scope` — inspect secure runtime configuration and scope without hidden active requests.
- `query`, `notebook`, `evidence-lineage`, `jobs` — shared SRIC graph/research/evidence/job primitives.
- `update` — signed wheel update flow only; never blind `git pull`.
- `help` — root/top-level help dispatcher.

Use `exposuredna <command> --help` for authoritative arguments/options.

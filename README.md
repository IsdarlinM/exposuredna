# Exposure DNA

```text
Exposure DNA
imr :: v0.2.0
```

Organization Security Knowledge Graph for correlating infrastructure, identity, software, APIs, history, trust and developer ecosystem evidence without asserting ownership from similarity alone.

> **AI proposes. Evidence proves. Humans control.**

## What works in v0.2.0

- organization workspaces and typed DNA dimensions;
- temporal entities and explicit relationships with evidence/counter-evidence;
- explainable entity-resolution queue using shared signals such as OAuth issuer, SDK lineage, analytics/certificate/ASN/repository metadata;
- conflicting evidence lowers confidence and all inferred relationships remain `INFERRED`;
- graph, timeline, DNA dimension summaries, explain and export;
- passive JSON ingestion; no autonomous Internet-wide crawling;
- local FastAPI + responsive DNA/knowledge-graph summary Web UI;
- offline synthetic demo, scope checks, plugin inspection, AI-disabled mode and signed-update primitive through SRIC;
- source-diversity-aware entity resolution and evidence-completeness coverage by DNA dimension (never a risk score);
- explicit organization/acquisition lineage, organization comparison without ownership claims and human-controlled resolution decisions;
- cross-project correlation preserving source/status/evidence plus passive adapters for CT, DNS, repos, packages, OAuth, analytics, ASN, OpenAPI and mobile exports;
- SRIC 0.3 jobs/SSE, evidence lineage, notebook/search and shared temporal graph primitives.

## Five-minute start

```bash
exposuredna doctor
exposuredna demo --workspace demo
exposuredna correlate demo
exposuredna graph demo
exposuredna web demo
```

Offline lab:

```bash
exposuredna init lab
exposuredna import lab examples/lab/organization.json
exposuredna correlate lab
```

## Ownership rule

Similarity never establishes ownership. Resolution candidates expose supporting signals, conflicting evidence, source diversity/temporal context and confidence; they remain `INFERRED` until reviewed with stronger evidence.

## Safety and privacy

Passive/local workflows are the default. Telemetry, cloud AI and external uploads are off unless explicitly configured.

## Documentation

See `docs/` and `ROADMAP.md` for architecture, security, CLI, formats, AI/plugins, integrations and deferred collectors.

## License

Apache-2.0.

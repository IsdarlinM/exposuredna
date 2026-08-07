# Exposure DNA

```text
Exposure DNA
imr :: v0.3.0
```

Organization Security Knowledge Graph for correlating infrastructure, identity, software, APIs, history, trust and developer-ecosystem evidence without asserting ownership from similarity alone.

> **AI proposes. Evidence proves. Humans control.**

## Implemented

- organization workspaces and typed DNA dimensions;
- temporal entities and explicit relationships with evidence/counter-evidence;
- explainable entity-resolution queue for OAuth issuer, SDK lineage, analytics, certificate, ASN, repository and package metadata;
- graph, timeline, DNA dimension summaries, explain and export;
- passive JSON ingestion with no autonomous Internet-wide crawling;
- local FastAPI API and responsive knowledge-graph Web UI;
- source-diversity-aware resolution and evidence-completeness coverage by DNA dimension, never a risk score;
- organization/acquisition lineage, organization comparison without ownership claims and human-controlled resolution decisions;
- passive CT, DNS, repository, package, OAuth, analytics, ASN, OpenAPI and mobile-export adapters;
- SRIC 0.4.1 graph, jobs/SSE, evidence lineage, notebook/search, evidence store and confidence calibration.

## Entity resolution v2

Exposure DNA now models positive and negative contributions explicitly. Negative controls include shared hosting and ASN, CDN/cloud infrastructure, wildcard certificates, common analytics/OAuth providers, repository forks, copied code, white-label applications, outsourced development, package namespace collisions, historical ownership, domain transfers and temporal conflicts.

Signals sharing one upstream source are deduplicated. Specificity, exclusivity, source quality and temporal relevance are visible in the confidence breakdown. Similarity never establishes ownership:

- weak or ambiguous candidates remain `UNKNOWN`;
- sufficiently supported relationships may remain `INFERRED`;
- correlation and human review cannot create `VALIDATED` ownership;
- counter-evidence and alternative explanations remain attached to the candidate.

## Quickstart

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

## Local release gate

Exposure DNA does not require hosted CI:

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

Machine-readable evidence and artifact hashes are written under `build/release-evidence/`. A release requires a complete `PASS` report for the exact source commit.

Passive/local workflows are the default. Telemetry, cloud AI and external uploads are off unless explicitly configured. Apache-2.0.

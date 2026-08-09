# Exposure DNA

```text
Exposure DNA :: v0.5.6
Developer: IsdarlinM

Correlate organization security relationships across time with evidence.
```

Organization Security Knowledge Graph for correlating infrastructure, identity, software, APIs, history, trust and developer-ecosystem evidence without asserting ownership from similarity alone.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

Exposure DNA is independently installable and independently useful. It uses SRIC Core 0.5.x internally, but ReproSec, AuthTwin, FossilScope and TrustBoundary Mapper are optional. Their absence never prevents organization modeling, entity resolution, CLI, API, Web UI or reporting.

```bash
exposuredna doctor
exposuredna capabilities
```

## Implemented

- organization workspaces and typed DNA dimensions;
- temporal entities, Organization Eras and explicit relationships with evidence/counter-evidence;
- explainable entity-resolution queue for OAuth issuer, SDK lineage, analytics, certificate, ASN, repository and package metadata;
- temporal relationship queries and conservative conflict detection;
- graph, timeline, DNA dimension summaries, explain and export;
- passive JSON ingestion with no autonomous Internet-wide crawling;
- local FastAPI API and responsive knowledge-graph Web UI;
- source-diversity-aware resolution and evidence-completeness coverage by DNA dimension, never a risk score;
- organization/acquisition lineage and human-controlled resolution decisions;
- passive CT, DNS, repository, package, OAuth, analytics, ASN, OpenAPI and mobile-export adapters;
- SRIC 0.5.x graph, jobs/SSE, evidence lineage, notebook/search, evidence store and confidence primitives;
- zero-config official update flow with safe same-version `update --force` reinstall support;
- full Web Feature Workbench with every public Exposure DNA CLI command and argument represented as structured responsive controls;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Entity resolution semantics

Positive and negative evidence are modeled explicitly. Weak or ambiguous candidates remain `UNKNOWN`; sufficiently supported relationships may remain `INFERRED`; correlation and human review cannot manufacture `VALIDATED` ownership. Historical ownership is bounded by its evidence interval and does not establish current ownership.

## Standalone install

Linux:

```bash
./scripts/install-linux.sh
exposuredna doctor
exposuredna capabilities
```

Windows:

```cmd
scripts\install-windows.cmd
exposuredna doctor
exposuredna capabilities
```

The installer resolves SRIC automatically. `SRIC_CORE_SOURCE` is only an explicit development/release-validation override.

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `Exposure DNA :: v0.5.6`, `Developer: IsdarlinM`, then the organization-security correlation purpose statement. Use `exposuredna --no-color COMMAND`, `exposuredna COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

## Quickstart

```bash
exposuredna doctor
exposuredna capabilities
exposuredna init lab example-org
exposuredna demo --workspace demo
exposuredna correlate demo
exposuredna graph demo
exposuredna web demo
```

## Web and API

The native knowledge-graph dashboard remains the quick view and now exposes **All Features** (`/workbench`) and **Advanced Console** (`/console`) directly. The Workbench is generated from `exposuredna.cli_all`, so every public command and every ordered CLI parameter has a structured responsive Web representation.

The Workbench uses the fixed SRIC runner with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. Evidence, temporal and human-review semantics remain authoritative: correlation cannot create validated ownership and Web convenience cannot bypass that rule.

## Updates

```bash
exposuredna update --check
exposuredna update
exposuredna update --force
```

The official path is zero-config. `--force` may reinstall the current official version or move forward, never downgrade. Custom `--manifest` plus `--public-key` remains an advanced signed-channel override.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.6 interface suite walks every public Exposure DNA command with `--help`, verifies every option and required argument, compares the complete ordered CLI parameter tree with the Workbench catalog, verifies native Dashboard / All Features / Advanced Console navigation, and smoke-tests graph, DNA, resolution queue, lineage, external correlations, jobs and notebook APIs. Destructive operations are gate-tested rather than executed solely for coverage.

Machine-readable evidence is written below `build/release-evidence/`; a release requires PASS for the exact commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.exposuredna/` are preserved.

Passive/local workflows are the default. Telemetry, cloud AI and external uploads are OFF unless explicitly configured. Apache-2.0.

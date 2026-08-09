# Exposure DNA

```text
Exposure DNA :: v0.5.5
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
- Web Command Console with exact public CLI command-tree parity and real-time jobs;
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

Interactive terminals display a compact subdued-green banner ordered as `Exposure DNA :: v0.5.5`, `Developer: IsdarlinM`, then the organization-security correlation purpose statement. Use `exposuredna --no-color COMMAND`, `exposuredna COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation. The banner is emitted to interactive stderr so JSON and redirected stdout remain clean. See `docs/cli-presentation.md`.

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

Exposure DNA provides a responsive knowledge-graph Web UI and local API. `/console` adds the Web Command Console, whose catalog is generated from `exposuredna.cli_all`; a standalone test requires the Web and CLI command-path sets to be exactly equal.

The console is **not an operating-system web shell**. It invokes only the fixed SRIC runner with `shell=False`, disabled stdin and a structured argv array. Mutating commands require explicit approval; evidence, temporal and human-review semantics remain authoritative. See `docs/web/cli-parity.md`.

## Updates

The official update path is zero-config:

```bash
exposuredna update --check
exposuredna update
exposuredna update --force
```

Normal users do **not** provide a manifest or public key. SRIC resolves only the fixed official `IsdarlinM/exposuredna` channel, requires the selected immutable release commit to be reported by GitHub as signature-verified, validates the exact source snapshot and package metadata, backs up state, installs without a shell, and verifies the installed distribution version.

`--force` reinstalls the official release even when that exact version is already installed. It may install a newer official release but never downgrades; `--check` and `--force` cannot be combined. Normal upgrades require rollback metadata; same-version forced reinstalls use the verified target snapshot as the recovery package.

`--manifest` and `--public-key` remain available together only as an advanced custom/private-channel override. Custom channels retain Ed25519 manifest and SHA-256 wheel verification. No blind `git pull` fallback is used. See `docs/release/update.md`.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

Machine-readable evidence is written below `build/release-evidence/`; a release requires PASS for the exact commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.exposuredna/` are preserved.

Passive/local workflows are the default. Telemetry, cloud AI and external uploads are OFF unless explicitly configured. Apache-2.0.

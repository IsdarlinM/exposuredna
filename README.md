# Exposure DNA

```text
Exposure DNA :: v0.5.7
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
- zero-config official update flow with same-version `update --force`, rollback and first-party runtime repair;
- exact SRIC version/module diagnostics in `doctor` and `/api/v1/runtime-compatibility`;
- full Web Feature Workbench with every public Exposure DNA CLI command and argument represented as structured responsive controls;
- lazy shared-Web loading and actionable degraded Workbench 503 behavior so a missing shared UI module cannot crash the entire CLI;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Entity resolution semantics

Positive and negative evidence are modeled explicitly. Weak or ambiguous candidates remain `UNKNOWN`; sufficiently supported relationships may remain `INFERRED`; correlation and human review cannot manufacture `VALIDATED` ownership. Historical ownership is bounded by its evidence interval and does not establish current ownership.

## Standalone install and repair

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

The installer resolves SRIC automatically. `SRIC_CORE_SOURCE` is only an explicit development/release-validation override. Installers are repair-capable: they force-reinstall the pinned signed first-party runtime and Exposure DNA, run `pip check`, import-probe `sric.web_console` and `sric.web_workbench`, verify the compatible core range, and execute doctor/capability/help smokes while preserving workspaces and evidence.

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `Exposure DNA :: v0.5.7`, `Developer: IsdarlinM`, then the organization-security correlation purpose statement. Use `exposuredna --no-color COMMAND`, `exposuredna COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

The help contract covers `exposuredna --help`, `exposuredna -h`, `exposuredna help`, `exposuredna COMMAND --help`, `exposuredna COMMAND -h` and `exposuredna COMMAND help`.

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

The native knowledge-graph dashboard remains the quick view and exposes **All Features** (`/workbench`) and **Advanced Console** (`/console`) directly. The Workbench is generated from `exposuredna.cli_all`, so every public command and every ordered CLI parameter has a structured responsive Web representation. `/api/v1/runtime-compatibility` exposes exact shared-runtime status.

Shared Web modules are loaded lazily. A stale/corrupt SRIC therefore cannot make every Exposure DNA command fail merely because a shared UI module is absent; the native application remains reachable and the unavailable Workbench returns an actionable `RUNTIME_INCOMPATIBLE` 503.

The Workbench uses the fixed SRIC runner with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. Evidence, temporal and human-review semantics remain authoritative: correlation cannot create validated ownership and Web convenience cannot bypass that rule.

## Updates

```bash
exposuredna update --check
exposuredna update
exposuredna update --force
```

Before an official product update, Exposure DNA verifies the shared SRIC runtime. Supported stale 0.5.x cores are bridged through immutable GitHub-signature-verified historical snapshots to the compatible floor; a compatible-version core with required modules missing is force-reinstalled through the official channel. Custom/private `--manifest` plus `--public-key` channels remain explicit and are not silently replaced by the official core channel.

The official path is zero-config. `--force` may reinstall the current official version or move forward, never downgrade, and no blind `git pull` fallback is used.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.7 runtime/interface suite reproduces stale/missing Workbench states, validates the signed transition chain and same-version repair, verifies degraded Web behavior, walks every public Exposure DNA command through all supported help forms and compares every ordered CLI parameter with the Workbench schema. Existing unit/integration/E2E/security suites continue to cover graph/DNA dimensions, resolution queue, negative evidence, human review, temporal relationships, organization eras, snapshots, lineage, passive adapters and ownership-safety semantics. Destructive operations are gate-tested rather than executed solely for coverage.

Machine-readable evidence is written below `build/release-evidence/`; a release requires PASS for the exact commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.exposuredna/` are preserved.

Passive/local workflows are the default. Telemetry, cloud AI and external uploads are OFF unless explicitly configured. Apache-2.0.

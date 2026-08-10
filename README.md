# Exposure DNA

```text
Exposure DNA :: v0.5.10
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
- JSON-safe shared Web command catalog generation from SRIC 0.5.11;
- lazy shared-Web loading and actionable degraded Workbench 503 behavior so a missing shared UI module cannot crash the entire CLI;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Entity resolution semantics

Positive and negative evidence are modeled explicitly. Weak or ambiguous candidates remain `UNKNOWN`; sufficiently supported relationships may remain `INFERRED`; correlation and human review cannot manufacture `VALIDATED` ownership. Historical ownership is bounded by its evidence interval and does not establish current ownership.

## Standalone install and repair

Linux / Termux:

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

The normal installer pins SRIC Core to an immutable GitHub commit and resolves that explicit first-party source **in the same pip transaction as Exposure DNA**. Because `sric-core` is intentionally not discovered from PyPI, the installer does not perform a later product-only reinstall that can trigger `ResolutionImpossible`. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override.

The repair path preserves workspaces and evidence. It validates host Python and any existing runtime interpreter; a stale, incomplete or broken environment rebuilds only `~/.exposuredna/venv`. It bootstraps `pip`, `setuptools` and `wheel`, resolves constrained Exposure DNA plus the explicit SRIC source, runs `pip check`, verifies `sric.web_console`, `sric.web_workbench` and `sric.web_catalog`, requires SRIC `>=0.5.11,<0.6`, and runs doctor/capability plus `--help`, `-h` and `help` smokes.

Installer-internal smokes use `SENTINEL_BANNER=never` and a temporary validation log. Successful installation no longer repeats the Exposure DNA banner; captured diagnostics are printed only if validation fails. Normal installation does not use `--force-reinstall`.

On Termux, a writable `$PREFIX/bin` already present in `PATH` is preferred so `exposuredna` becomes immediately reachable. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`; any Python 3 interpreter satisfying `>=3.11` is accepted.

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `Exposure DNA :: v0.5.10`, `Developer: IsdarlinM`, then the organization-security correlation purpose statement. Use `exposuredna --no-color COMMAND`, `exposuredna COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

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

SRIC 0.5.11 normalizes command metadata to deterministic JSON-safe primitives before FastAPI serialization, preventing unusual CLI defaults/metadata from producing an opaque catalog HTTP 500. Shared Web modules are loaded lazily; a stale/corrupt SRIC therefore cannot make every Exposure DNA command fail merely because a shared UI module is absent.

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

The 0.5.10 installer regression verifies atomic first-party resolution, signed SRIC 0.5.11 pin/lock, venv-only repair, Termux `$PREFIX/bin`, safe Windows PATH handling, quiet installer smokes and dependency/import/help checks. Web regressions require Console/Workbench catalogs to return HTTP 200 with non-empty command/feature sets and complete CLI/Web coverage. Existing runtime/interface and unit/integration/E2E/security suites continue to cover graph/DNA dimensions, resolution queue, negative evidence, human review, temporal relationships, organization eras, snapshots, lineage, passive adapters and ownership-safety semantics. Destructive operations are gate-tested rather than executed solely for coverage.

Machine-readable evidence is written below `build/release-evidence/`; a release requires PASS for the exact commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.exposuredna/` are preserved.

Passive/local workflows are the default. Telemetry, cloud AI and external uploads are OFF unless explicitly configured. Apache-2.0.

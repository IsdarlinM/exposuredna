# Exposure DNA

```text
Exposure DNA :: v0.5.13
Developer: IsdarlinM

Correlate organization security relationships across time with evidence.
```

Organization Security Knowledge Graph for correlating infrastructure, identity, software, APIs, history, trust and developer-ecosystem evidence without asserting ownership from similarity alone.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

Exposure DNA is independently installable and independently useful. It requires **SRIC Core >=0.5.13,<0.6** for shared evidence, policy, workspace, graph and Web/runtime primitives; ReproSec, AuthTwin, FossilScope and TrustBoundary Mapper remain optional integrations.

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
- SRIC graph, jobs/SSE, evidence lineage, notebook/search, evidence store and confidence primitives;
- zero-config product update flow with same-version `update --force`, rollback and first-party runtime repair;
- exact SRIC version/module diagnostics in `doctor` and `/api/v1/runtime-compatibility`;
- guided **Web Security Console** with every public Exposure DNA capability represented as operation cards and typed responsive controls;
- checkboxes/tri-state selectors for flags, combo/select controls for closed choices, numeric/path controls, repeated-value controls and protected sensitive fields;
- JSON-safe shared Web capability catalog generation with choice/bound/path metadata;
- structured redacted HTTP 503 handling when capability-catalog construction itself fails;
- bounded Web child termination/reaping and short-lived retired-job retention for active SSE/status readers;
- shared operational exception containment and persisted Job Engine secret redaction;
- shared-route CSP permitting same-origin Security Console CSS/JS while retaining restrictive object/base/frame policies;
- lazy shared-Web loading and actionable degraded Workbench 503 behavior;
- fixed-runner execution with exact CLI-tree parity and real-time jobs while keeping free-form command/argv entry out of the user interface;
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

The normal installer pins SRIC Core to immutable GitHub-verified commit `bd90fe668e4a2a23c00a39f7d63df1c092b63c12` and resolves that explicit first-party source in the same pip transaction as Exposure DNA. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override.

The repair path preserves workspaces, configuration and evidence. It validates host Python and any existing runtime interpreter; a stale, incomplete or broken environment rebuilds only `~/.exposuredna/venv`. It bootstraps `pip`, `setuptools` and `wheel`, resolves constrained Exposure DNA plus the explicit SRIC source, runs `pip check`, verifies `sric.web_console`, `sric.web_workbench`, `sric.web_catalog` and `sric.web_runtime`, requires SRIC `>=0.5.13,<0.6`, and runs doctor/capability plus `--help`, `-h` and `help` smokes.

Installer-internal smokes use `SENTINEL_BANNER=never` and a temporary validation log. Successful installation does not repeat the Exposure DNA banner; captured diagnostics are printed only if validation fails. Normal installation does not use `--force-reinstall`.

On Termux, a writable `$PREFIX/bin` already present in `PATH` is preferred so `exposuredna` becomes immediately reachable. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`; any Python 3 interpreter satisfying `>=3.11` is accepted.

## CLI presentation and help contract

Interactive terminals display `Exposure DNA :: v0.5.13`, `Developer: IsdarlinM`, then the organization-security correlation purpose statement. Use `exposuredna --no-color COMMAND`, `exposuredna COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

Supported help forms are:

```text
exposuredna --help
exposuredna -h
exposuredna help
exposuredna COMMAND --help
exposuredna COMMAND -h
exposuredna COMMAND help
```

Unexpected operational exceptions are redacted/contained by SRIC. `SENTINEL_DEBUG=1` is an explicit developer-only opt-in for raw local exception propagation.

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

The native knowledge-graph dashboard remains the quick view for DNA coverage, knowledge graph, resolution queue, organization lineage and live jobs. `/workbench` is the primary **Security Console** and is generated from `exposuredna.cli_all`, so every public capability and every ordered CLI parameter has a structured responsive Web representation. `/console` is retained only as a compatibility alias that opens `/workbench`; it is not an argv-oriented user interface. `/api/v1/runtime-compatibility` exposes exact shared-runtime status.

SRIC 0.5.13 normalizes command metadata to deterministic JSON-safe primitives and includes choice, numeric-bound and path metadata used to render appropriate HTML controls without duplicating product behavior. If catalog construction itself fails unexpectedly, the API returns a bounded/redacted HTTP 503 instead of an opaque HTTP 500. Shared Web modules are loaded lazily so a stale/corrupt shared UI module does not crash every Exposure DNA CLI command.

For the Security Console, Exposure DNA permits same-origin shared CSS/JS while retaining restrictive object/base/frame CSP policies.

Users do not type command paths, option names, flags or free-form argv. Structured control values are serialized only as an internal transport detail to the fixed SRIC runner. Execution uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs, approval gates and SSE output. Timed-out children use bounded terminate/kill/wait handling with background reaping when required; recently pruned terminal jobs remain briefly available to active status/SSE readers. Evidence, temporal and human-review semantics remain authoritative: correlation cannot create validated ownership and Web convenience cannot bypass that rule.

## Updates and shared-runtime repair

```bash
exposuredna update --check
exposuredna update
exposuredna update --force
```

Supported stale SRIC runtimes are advanced through fixed immutable GitHub-signature-verified snapshots one release at a time from 0.5.5 through the 0.5.13 floor, avoiding unsafe rollback-metadata jumps. A same-version corrupt 0.5.13 runtime is repaired from the fixed verified 0.5.13 snapshot. No blind `git pull` fallback is used.

The Exposure DNA 0.5.13 official channel points to a GitHub-verified release commit and carries rollback metadata for the immediately preceding verified 0.5.12 snapshot.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.13 runtime regression walks every public Exposure DNA CLI command, all supported root/subcommand help forms, exact ordered CLI/Web parameter parity, structured control types and absence of free-form argv UI. Existing unit/integration/E2E/security suites cover graph/DNA dimensions, resolution queue, negative evidence, human review, temporal relationships, organization eras, snapshots, lineage, passive adapters, native dashboard pages/API resources and ownership-safety semantics.

`TEST_EVIDENCE.md` is authoritative for what actually executed. GitHub-hosted runners are currently blocked by an account billing lock, so zero-step workflows are not counted as PASS and do not prove Exposure DNA's complete exact-commit release gate. The current execution environment also lacks GitHub network/DNS access, so no substitute clone-based local full-suite PASS is claimed.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.exposuredna/` are preserved.

Passive/local workflows are the default. Telemetry, cloud AI and external uploads are OFF unless explicitly configured. Apache-2.0.

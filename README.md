# Exposure DNA

```text
Exposure DNA :: v0.5.12
Developer: IsdarlinM

Correlate organization security relationships across time with evidence.
```

Organization Security Knowledge Graph for correlating infrastructure, identity, software, APIs, history, trust and developer-ecosystem evidence without asserting ownership from similarity alone.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

Exposure DNA is independently installable and independently useful. It requires **SRIC Core >=0.5.12,<0.6** for shared evidence, policy, workspace, graph and Web/runtime primitives; ReproSec, AuthTwin, FossilScope and TrustBoundary Mapper remain optional integrations.

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
- full Web Feature Workbench with every public Exposure DNA CLI command and argument represented as structured responsive controls;
- JSON-safe shared Web command catalog generation;
- structured redacted HTTP 503 handling when command-catalog construction itself fails;
- bounded Web child termination/reaping and short-lived retired-job retention for active SSE/status readers;
- shared operational exception containment and persisted Job Engine secret redaction;
- shared-route CSP permitting same-origin Console/Workbench CSS/JS while retaining restrictive object/base/frame policies;
- lazy shared-Web loading and actionable degraded Workbench 503 behavior;
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

The normal installer pins SRIC Core to immutable signed main commit `4dd0ad417e55fc76fb67d582ec50234bffff2876` and resolves that explicit first-party source in the same pip transaction as Exposure DNA. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override.

The repair path preserves workspaces, configuration and evidence. It validates host Python and any existing runtime interpreter; a stale, incomplete or broken environment rebuilds only `~/.exposuredna/venv`. It bootstraps `pip`, `setuptools` and `wheel`, resolves constrained Exposure DNA plus the explicit SRIC source, runs `pip check`, verifies `sric.web_console`, `sric.web_workbench`, `sric.web_catalog` and `sric.web_runtime`, requires SRIC `>=0.5.12,<0.6`, and runs doctor/capability plus `--help`, `-h` and `help` smokes.

Installer-internal smokes use `SENTINEL_BANNER=never` and a temporary validation log. Successful installation does not repeat the Exposure DNA banner; captured diagnostics are printed only if validation fails. Normal installation does not use `--force-reinstall`.

On Termux, a writable `$PREFIX/bin` already present in `PATH` is preferred so `exposuredna` becomes immediately reachable. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`; any Python 3 interpreter satisfying `>=3.11` is accepted.

## CLI presentation and help contract

Interactive terminals display `Exposure DNA :: v0.5.12`, `Developer: IsdarlinM`, then the organization-security correlation purpose statement. Use `exposuredna --no-color COMMAND`, `exposuredna COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

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

The native knowledge-graph dashboard remains the quick view and exposes **All Features** (`/workbench`) and **Advanced Console** (`/console`) directly. The Workbench is generated from `exposuredna.cli_all`, so every public command and every ordered CLI parameter has a structured responsive Web representation. `/api/v1/runtime-compatibility` exposes exact shared-runtime status.

SRIC 0.5.12 normalizes command metadata to deterministic JSON-safe primitives before FastAPI serialization. If catalog construction itself fails unexpectedly, the API returns a bounded/redacted HTTP 503 instead of an opaque HTTP 500. Shared Web modules are loaded lazily so a stale/corrupt shared UI module does not crash every Exposure DNA CLI command.

For `/console` and `/workbench`, Exposure DNA permits same-origin shared CSS/JS while retaining restrictive object/base/frame CSP policies.

The Workbench is not an operating-system shell. Execution uses the fixed SRIC runner with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. Timed-out children use bounded terminate/kill/wait handling with background reaping when required; recently pruned terminal jobs remain briefly available to active status/SSE readers. Evidence, temporal and human-review semantics remain authoritative: correlation cannot create validated ownership and Web convenience cannot bypass that rule.

## Updates and shared-runtime repair

```bash
exposuredna update --check
exposuredna update
exposuredna update --force
```

Supported stale SRIC runtimes are advanced through fixed immutable GitHub-signature-verified snapshots one release at a time from 0.5.5 through the 0.5.12 floor, avoiding unsafe rollback-metadata jumps. A same-version corrupt 0.5.12 runtime is repaired from the fixed signed 0.5.12 snapshot. No blind `git pull` fallback is used.

The SRIC official update channel may remain on the previous fully gated release while 0.5.12 exact-commit gates are blocked; Exposure DNA's first-party pin/repair chain uses fixed verified commits independently of that moving channel.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.12 runtime regression walks every public Exposure DNA CLI command, all supported root/subcommand help forms and exact ordered CLI/Web parameter parity. Existing unit/integration/E2E/security suites cover graph/DNA dimensions, resolution queue, negative evidence, human review, temporal relationships, organization eras, snapshots, lineage, passive adapters, Console/Workbench pages/assets/catalogs/coverage, native API resources and ownership-safety semantics.

`TEST_EVIDENCE.md` is authoritative for what actually executed. The shared SRIC 0.5.12 focused runtime harness passed its four targeted regressions after first exposing and fixing a background-reaper return-code race. GitHub-hosted runners are currently blocked by an account billing lock, so zero-step workflows are not counted as PASS and do not prove Exposure DNA's complete exact-commit release gate.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime is removed while workspaces, configuration and evidence under `~/.exposuredna/` are preserved.

Passive/local workflows are the default. Telemetry, cloud AI and external uploads are OFF unless explicitly configured. Apache-2.0.

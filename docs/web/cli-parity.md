# Web/CLI feature parity

Exposure DNA 0.5.6 mounts the shared SRIC Web Feature Workbench at `/workbench` and retains `/console` as an advanced argv-oriented surface.

The native organization knowledge-graph dashboard exposes **All Features** and **Advanced Console** navigation. The Workbench derives its schema from `exposuredna.cli_all`, so every public command and ordered CLI parameter has a structured responsive Web control. `/api/v1/workbench/coverage` reports exact parity.

Execution uses the fixed `sric.web_console_runner` with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. Evidence, temporal and human-review semantics remain authoritative; Web correlation cannot manufacture validated ownership.

The release tests invoke help for every public command, verify all options/required arguments, compare the complete ordered CLI parameter tree with the Workbench schema, verify native navigation and smoke-test graph/DNA/resolution/lineage APIs. Destructive actions are gate-tested rather than executed merely for coverage.

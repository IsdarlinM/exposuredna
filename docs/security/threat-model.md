# Threat model

Assets: organization evidence, provenance, relationship claims, workspaces and reports.

Primary threats include poisoned imports, false ownership inference, source-correlation inflation, path traversal, malicious files, prompt injection, secret leakage, cross-workspace leakage and unauthorized active validation.

Mitigations include bounded regular-file imports, schema validation, explicit evidence/counter-evidence, source-diversity accounting, temporal validity, local-first defaults, loopback-only Web UI, SRIC Scope/Policy gates and human-controlled validation.

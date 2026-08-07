# Local release gate

Exposure DNA does not depend on GitHub Actions or another hosted CI service.

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

The gate runs compilation, Ruff, strict mypy, all pytest suites, project security/evaluation scripts when present, `pip-audit`, SBOM generation when available, package build, isolated wheel installation and CLI `--help`/`-h` checks. Machine-readable evidence and SHA-256 artifact hashes are written under `build/release-evidence/`.

`--quick` is a development-only pass. The project must not publish a release until the full gate reports `PASS` for the exact source commit.

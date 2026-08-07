# Installation

Linux:

```bash
./scripts/install-linux.sh
```

Windows:

```cmd
scripts\install-windows.cmd
```

Python 3.11+ and SRIC Core 0.4.1 are required. Source installers prefer a sibling `sric-core` checkout or `SRIC_CORE_SOURCE`; otherwise they use the configured package source. Installers create an isolated environment and configure a user-local command launcher.

Verify installation and compatibility:

```bash
exposuredna doctor
python scripts/release-gate.py --quick
```

The complete release gate, including dependency audit and isolated wheel installation, must be run before publishing a release.

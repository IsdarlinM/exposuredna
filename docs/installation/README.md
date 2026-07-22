# Installation

Linux: `./scripts/install-linux.sh`

Windows: `scripts\install-windows.cmd`

Python 3.11+ and SRIC Core 0.3.x are required. Source installers prefer a sibling `sric-core` checkout or `SRIC_CORE_SOURCE`; otherwise they use the configured package source. Installers create an isolated environment and configure a user-local command launcher. Verify with `exposuredna doctor`.

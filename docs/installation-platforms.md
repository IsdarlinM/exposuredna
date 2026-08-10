# Installation and uninstallation

| Platform | Install | Uninstall |
|---|---|---|
| Linux / Termux | `sh scripts/install-linux.sh` | `sh scripts/uninstall-linux.sh` |
| Windows | `scripts\install-windows.cmd` | `scripts\uninstall-windows.cmd` |

The Windows uninstaller removes the `exposuredna.cmd` shim and isolated Exposure DNA venv while preserving workspaces, configuration, resolution decisions and evidence. It leaves the shared `%USERPROFILE%\.local\bin` PATH entry untouched. Linux follows the same data-preservation contract.

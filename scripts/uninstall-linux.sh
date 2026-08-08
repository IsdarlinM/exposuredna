#!/usr/bin/env sh
set -eu
INSTALL_ROOT="${HOME}/.exposuredna"
BIN="${HOME}/.local/bin/exposuredna"
rm -f "$BIN"
rm -rf "$INSTALL_ROOT/venv"
echo "Removed Exposure DNA runtime. Workspaces, configuration and evidence under $INSTALL_ROOT were preserved."

#!/usr/bin/env sh
set -eu
INSTALL_ROOT="${HOME}/.exposuredna"
VENV="$INSTALL_ROOT/venv"
BIN_DIR="${HOME}/.local/bin"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
if [ "$(id -u)" = "0" ] && [ "${ALLOW_ROOT_INSTALL:-0}" != "1" ]; then echo "Refusing root install by default." >&2; exit 2; fi
PYTHON="${PYTHON:-python3}"
"$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)' || { echo "Python 3.11+ is required." >&2; exit 2; }
mkdir -p "$INSTALL_ROOT" "$BIN_DIR"
[ -x "$VENV/bin/python" ] || "$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
SRIC_SOURCE="${SRIC_CORE_SOURCE:-}"
[ -n "$SRIC_SOURCE" ] || { [ ! -f "$REPO_ROOT/../sric-core/pyproject.toml" ] || SRIC_SOURCE="$REPO_ROOT/../sric-core"; }
if [ -n "$SRIC_SOURCE" ]; then "$VENV/bin/python" -m pip install --upgrade "$SRIC_SOURCE"; else "$VENV/bin/python" -m pip install 'sric-core>=0.3,<0.4' || { echo "SRIC Core 0.3.x is required." >&2; exit 3; }; fi
"$VENV/bin/python" -m pip install --upgrade "$REPO_ROOT"
ln -sfn "$VENV/bin/exposuredna" "$BIN_DIR/exposuredna"
PROFILE="${HOME}/.profile"; PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'; touch "$PROFILE"; grep -F "$PATH_LINE" "$PROFILE" >/dev/null 2>&1 || printf '\n# Security Research Intelligence tools\n%s\n' "$PATH_LINE" >> "$PROFILE"
"$VENV/bin/exposuredna" doctor
printf 'Exposure DNA installed successfully. Open a new shell and run: exposuredna --help\n'

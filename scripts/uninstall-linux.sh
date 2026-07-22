#!/usr/bin/env sh
set -eu
rm -f "$HOME/.local/bin/exposuredna"
rm -rf "$HOME/.exposuredna"
echo "Removed Exposure DNA. User-created workspaces outside $HOME/.exposuredna were not touched."

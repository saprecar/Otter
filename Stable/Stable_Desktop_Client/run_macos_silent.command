#!/usr/bin/env bash
# [AI-BLOCK: macOS Zero-Terminal Silent Launcher for Otter]
# Detaches Otter Desktop UI from Terminal.app so it runs windowless.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
osascript -e "do shell script \"cd \\\"$SCRIPT_DIR\\\" && ./run_macos.sh --silent >/dev/null 2>&1 &\"" >/dev/null 2>&1 &

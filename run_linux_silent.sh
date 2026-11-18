#!/usr/bin/env bash
# [AI-BLOCK: Linux Zero-Terminal Silent Launcher for Otter]
# Launches Otter Desktop UI directly in background with zero terminal window.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

nohup "$SCRIPT_DIR/run_linux.sh" --silent >/dev/null 2>&1 &

#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="python3"
command -v python3 &>/dev/null || PYTHON_CMD="python"
cd "$SCRIPT_DIR/desktop"
$PYTHON_CMD "$SCRIPT_DIR/desktop/otter_app.py" "$@"

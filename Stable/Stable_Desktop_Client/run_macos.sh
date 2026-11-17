#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "==================================================="
echo "  Otter - Virtual Webcam & Remote Controller"
echo "  Developer: spacecar | https://github.com/saprecar/Otter"
echo "==================================================="
echo ""

PYTHON_CMD="python3"
if [ -f "../../.venv/bin/python" ]; then
    PYTHON_CMD="../../.venv/bin/python"
elif [ -f "./.venv/bin/python" ]; then
    PYTHON_CMD="./.venv/bin/python"
elif [ -f "./venv/bin/python" ]; then
    PYTHON_CMD="./venv/bin/python"
fi

exec "$PYTHON_CMD" otter_app.py

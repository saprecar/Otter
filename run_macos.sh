#!/usr/bin/env bash
# [AI-BLOCK: macOS One-Click Launcher for Otter Virtual Camera Controller]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==================================================="
echo "  Otter - Virtual Webcam & Remote Controller"
echo "  Developer: spacecar | https://github.com/saprecar/Otter"
echo "==================================================="
echo ""

# Detect Python 3
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python 3 on macOS via Homebrew:"
    echo "  brew install python-tk"
    echo "Or download the official macOS installer from:"
    echo "  https://www.python.org/downloads/macos/"
    read -p "Press Enter to exit..."
    exit 1
fi

# Locate Otter App
APP_PATH=""
if [ -f "$SCRIPT_DIR/Dev/desktop/otter_app.py" ]; then
    APP_PATH="$SCRIPT_DIR/Dev/desktop/otter_app.py"
    cd "$SCRIPT_DIR/Dev/desktop"
elif [ -f "$SCRIPT_DIR/desktop/otter_app.py" ]; then
    APP_PATH="$SCRIPT_DIR/desktop/otter_app.py"
    cd "$SCRIPT_DIR/desktop"
elif [ -f "$SCRIPT_DIR/otter_app.py" ]; then
    APP_PATH="$SCRIPT_DIR/otter_app.py"
    cd "$SCRIPT_DIR"
else
    echo "[ERROR] Could not locate otter_app.py."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Starting Otter Controller using: $PYTHON_CMD"
echo ""
$PYTHON_CMD "$APP_PATH" "$@"

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "[NOTICE] Otter controller exited with code $EXIT_CODE."
    read -p "Press Enter to exit..."
fi

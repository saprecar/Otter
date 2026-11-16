#!/usr/bin/env bash
# [AI-BLOCK: Linux One-Click Launcher for Otter Virtual Camera Controller]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==================================================="
echo "  Otter - Virtual Webcam & Remote Controller"
echo "  Developer: spacecar | https://github.com/saprecar/Otter"
echo "==================================================="
echo ""

# Detect Python 3 (Prioritize local folder virtual environment .venv or venv)
PYTHON_CMD=""
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
    echo "[INFO] Using project local virtual environment (.venv)."
elif [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
    echo "[INFO] Using project local virtual environment (venv)."
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python on Debian/Ubuntu/Mint:"
    echo "  sudo apt update && sudo apt install python3 python3-pip python3-tk"
    echo "Or on Fedora/RHEL:"
    echo "  sudo dnf install python3 python3-pip python3-tkinter"
    echo "Or on Arch Linux:"
    echo "  sudo pacman -S python python-pip tk"
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

#!/usr/bin/env bash
# [AI-BLOCK: macOS One-Click Self-Bootstrapping Launcher for Otter]

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==================================================="
echo "  Otter - Virtual Webcam & Remote Controller"
echo "  Developer: spacecar | https://github.com/saprecar/Otter"
echo "==================================================="
echo ""

# 1. Detect Python 3 on macOS
PYTHON_SYS=""
if command -v python3 &>/dev/null; then
    PYTHON_SYS="python3"
elif [ -f "/usr/local/bin/python3" ]; then
    PYTHON_SYS="/usr/local/bin/python3"
elif [ -f "/opt/homebrew/bin/python3" ]; then
    PYTHON_SYS="/opt/homebrew/bin/python3"
elif command -v python &>/dev/null; then
    PYTHON_SYS="python"
fi

if [ -z "$PYTHON_SYS" ]; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "To install Python on macOS via Homebrew:"
    echo "  brew install python python-tk"
    echo "Or download Python from: https://www.python.org/downloads/macos/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# 2. Check for Tkinter GUI support (optional fallback)
if ! "$PYTHON_SYS" -c "import tkinter" &>/dev/null; then
    echo "[INFO] Note: Tkinter GUI not available. Otter will run using the universal Web UI."
fi

# 3. Create & bootstrap isolated virtual environment (.venv)
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "[INFO] Creating isolated virtual environment in .venv..."
    "$PYTHON_SYS" -m venv "$VENV_DIR"
    echo "[INFO] Installing required dependencies (opencv-python, numpy, imageio-ffmpeg)..."
    "$VENV_DIR/bin/pip" install --upgrade pip --quiet
    if [ -f "$SCRIPT_DIR/Dev/desktop/requirements.txt" ]; then
        "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/Dev/desktop/requirements.txt"
    elif [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    else
        "$VENV_DIR/bin/pip" install "opencv-python>=4.8.0" "numpy>=1.24.0" "imageio-ffmpeg>=0.4.8"
    fi
    echo "[INFO] Dependencies installed successfully."
fi

# 4. Locate Otter App
APP_PATH=""
if [ -f "$SCRIPT_DIR/Stable/Stable_Desktop_Client/otter_app.py" ]; then
    APP_PATH="$SCRIPT_DIR/Stable/Stable_Desktop_Client/otter_app.py"
    cd "$SCRIPT_DIR/Stable/Stable_Desktop_Client"
elif [ -f "$SCRIPT_DIR/Dev/desktop/otter_app.py" ]; then
    APP_PATH="$SCRIPT_DIR/Dev/desktop/otter_app.py"
    cd "$SCRIPT_DIR/Dev/desktop"
elif [ -f "$SCRIPT_DIR/otter_app.py" ]; then
    APP_PATH="$SCRIPT_DIR/otter_app.py"
fi

# 5. Launch Otter Desktop Controller
echo "[INFO] Starting Otter Desktop Controller..."
echo ""
"$VENV_PYTHON" "$APP_PATH" "$@"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "[ERROR] Otter Desktop Controller exited with code $EXIT_CODE."
    read -p "Press Enter to exit..."
fi

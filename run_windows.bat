@echo off
setlocal enabledelayedexpansion
title Otter Virtual Camera Controller
cd /d "%~dp0"

echo ===================================================
echo   Otter - Virtual Webcam ^& Remote Controller
echo   Developer: spacecar ^| https://github.com/saprecar/Otter
echo ===================================================
echo.

:: 1. Check for bundled portable Python
set "PYTHON_CMD="
if exist "%~dp0Stable\Stable_Desktop_Client\python\python.exe" (
    set "PYTHON_CMD=%~dp0Stable\Stable_Desktop_Client\python\python.exe"
    goto :RUN_OTTER
) else if exist "%~dp0python\python.exe" (
    set "PYTHON_CMD=%~dp0python\python.exe"
    goto :RUN_OTTER
)

:: 2. Check for local virtual environment (.venv)
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
    goto :RUN_OTTER
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
    goto :RUN_OTTER
)

:: 3. Detect System Python
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "SYS_PYTHON=python"
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "SYS_PYTHON=py -3"
    ) else (
        echo [ERROR] Python is not detected on your system.
        echo Please install Python from https://www.python.org/downloads/
        echo Make sure to check the box "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
)

:: 4. Auto-create local .venv so user does not need to install anything globally
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [INFO] First-time setup: Creating isolated Python environment (.venv)...
    %SYS_PYTHON% -m venv "%~dp0.venv"
    if %ERRORLEVEL% neq 0 (
        echo [WARNING] venv creation failed. Running with system Python...
        set "PYTHON_CMD=%SYS_PYTHON%"
        goto :RUN_OTTER
    )
    echo [INFO] Installing required dependencies (opencv-python, numpy, imageio-ffmpeg)...
    "%~dp0.venv\Scripts\pip.exe" install --upgrade pip --quiet
    if exist "%~dp0Dev\desktop\requirements.txt" (
        "%~dp0.venv\Scripts\pip.exe" install -r "%~dp0Dev\desktop\requirements.txt"
    ) else if exist "%~dp0requirements.txt" (
        "%~dp0.venv\Scripts\pip.exe" install -r "%~dp0requirements.txt"
    ) else (
        "%~dp0.venv\Scripts\pip.exe" install "opencv-python>=4.8.0" "numpy>=1.24.0" "imageio-ffmpeg>=0.4.8"
    )
    echo [INFO] Setup complete.
)

set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"

:RUN_OTTER
set "APP_PATH="
if exist "%~dp0Stable\Stable_Desktop_Client\otter_app.py" (
    set "APP_PATH=%~dp0Stable\Stable_Desktop_Client\otter_app.py"
    cd /d "%~dp0Stable\Stable_Desktop_Client"
) else if exist "%~dp0Dev\desktop\otter_app.py" (
    set "APP_PATH=%~dp0Dev\desktop\otter_app.py"
    cd /d "%~dp0Dev\desktop"
) else if exist "%~dp0otter_app.py" (
    set "APP_PATH=%~dp0otter_app.py"
)

echo [INFO] Starting Otter Desktop Controller...
echo.
"%PYTHON_CMD%" "%APP_PATH%"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [NOTICE] Otter controller exited with error code %ERRORLEVEL%.
    pause
)

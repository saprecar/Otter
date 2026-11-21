@echo off
setlocal enabledelayedexpansion
title Otter Web UI Controller
cd /d "%~dp0"

echo ===================================================
echo   Otter - Web UI Controller ^& Virtual Camera
echo   Developer: spacecar ^| https://github.com/saprecar/Otter
echo ===================================================
echo.

:: 1. Detect Python executable
set "PYTHON_CMD="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
) else if exist "%~dp0Stable\Stable_Desktop_Client\python\python.exe" (
    set "PYTHON_CMD=%~dp0Stable\Stable_Desktop_Client\python\python.exe"
) else if exist "%~dp0python\python.exe" (
    set "PYTHON_CMD=%~dp0python\python.exe"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=python"
    ) else (
        echo [ERROR] Python is not installed or not in PATH.
        echo Please install Python 3.8+ and add it to PATH.
        pause
        exit /b 1
    )
)

:: 2. Locate Web Server script
set "APP_PATH="
if exist "%~dp0Dev\desktop\otter_web_server.py" (
    set "APP_PATH=%~dp0Dev\desktop\otter_web_server.py"
    cd /d "%~dp0Dev\desktop"
) else if exist "%~dp0Stable\Stable_Desktop_Client\otter_web_server.py" (
    set "APP_PATH=%~dp0Stable\Stable_Desktop_Client\otter_web_server.py"
    cd /d "%~dp0Stable\Stable_Desktop_Client"
) else if exist "%~dp0otter_web_server.py" (
    set "APP_PATH=%~dp0otter_web_server.py"
) else if exist "%~dp0Dev\desktop\otter_app.py" (
    set "APP_PATH=%~dp0Dev\desktop\otter_app.py"
    cd /d "%~dp0Dev\desktop"
)

echo [INFO] Starting Otter Universal Web Controller on %PYTHON_CMD%...
echo.
"%PYTHON_CMD%" "%APP_PATH%" %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo [NOTICE] Otter Web Controller exited with code %ERRORLEVEL%.
    pause
)

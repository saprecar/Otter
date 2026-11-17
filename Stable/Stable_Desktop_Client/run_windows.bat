@echo off
setlocal enabledelayedexpansion
title Otter Virtual Camera Controller
cd /d "%~dp0"

echo ===================================================
echo   Otter - Virtual Webcam ^& Remote Controller
echo   Developer: spacecar ^| https://github.com/saprecar/Otter
echo ===================================================
echo.

:: Detect Python executable (Prioritize local folder virtual environment .venv or venv)
set "PYTHON_CMD="
if exist "%~dp0..\..\.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0..\..\.venv\Scripts\python.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=python"
    ) else (
        where py >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            set "PYTHON_CMD=py -3"
        )
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python is not detected on your system.
    echo Please install Python 3.8 or higher from:
    echo   https://www.python.org/downloads/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Starting Otter Controller...
echo.
"%PYTHON_CMD%" "%~dp0otter_app.py"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [NOTICE] Otter controller exited.
    pause
)

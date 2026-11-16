@echo off
setlocal enabledelayedexpansion
title Otter Virtual Camera Controller

echo ===================================================
echo   Otter - Virtual Webcam ^& Remote Controller
echo   Developer: spacecar ^| https://github.com/saprecar/Otter
echo ===================================================
echo.

set "PYTHON_CMD="
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=py -3"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python is not detected on your system.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

cd /d "%~dp0desktop"
echo Starting Otter Controller using: %PYTHON_CMD%
echo.
%PYTHON_CMD% "%~dp0desktop\otter_app.py"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [NOTICE] Otter controller exited with an error.
    pause
)

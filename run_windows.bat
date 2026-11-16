@echo off
setlocal enabledelayedexpansion
title Otter Virtual Camera Controller

echo ===================================================
echo   Otter - Virtual Webcam ^& Remote Controller
echo   Developer: spacecar ^| https://github.com/saprecar/Otter
echo ===================================================
echo.

:: Detect Python executable (Prioritize local folder virtual environment .venv or venv)
set "PYTHON_CMD="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
    echo [INFO] Using project local virtual environment: .venv
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
    echo [INFO] Using project local virtual environment: venv
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=python"
    ) else (
        where py >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            set "PYTHON_CMD=py -3"
        ) else (
            if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
                set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
            ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
                set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
            ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
                set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
            )
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

:: Locate Otter app script
set "APP_PATH="
if exist "%~dp0Dev\desktop\otter_app.py" (
    set "APP_PATH=%~dp0Dev\desktop\otter_app.py"
    cd /d "%~dp0Dev\desktop"
) else if exist "%~dp0desktop\otter_app.py" (
    set "APP_PATH=%~dp0desktop\otter_app.py"
    cd /d "%~dp0desktop"
) else if exist "%~dp0otter_app.py" (
    set "APP_PATH=%~dp0otter_app.py"
    cd /d "%~dp0"
) else (
    echo [ERROR] Could not locate otter_app.py.
    pause
    exit /b 1
)

echo Starting Otter Controller using: "%PYTHON_CMD%"
echo.
"%PYTHON_CMD%" "%APP_PATH%"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [NOTICE] Otter controller exited with an error.
    pause
)

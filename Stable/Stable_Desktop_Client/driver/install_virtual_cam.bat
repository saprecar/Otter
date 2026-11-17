@echo off
setlocal
title Otter Virtual Camera Driver Installer

echo ===================================================
echo   Otter - Standalone Virtual Camera Driver Setup
echo   Registers DirectShow webcam device in Windows
echo ===================================================
echo.

cd /d "%~dp0"

:: Check for administrative rights
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [NOTICE] Requesting Administrator permissions...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

echo Registering 64-bit DirectShow Filter...
regsvr32 /s "%~dp0UnityCaptureFilter64.dll"
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] 64-bit DirectShow virtual camera registered successfully!
) else (
    echo [WARNING] Failed to register 64-bit filter. Error code: %ERRORLEVEL%
)

echo Registering 32-bit DirectShow Filter...
regsvr32 /s "%~dp0UnityCaptureFilter32.dll"
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] 32-bit DirectShow virtual camera registered successfully!
) else (
    echo [INFO] 32-bit registration skipped or not required.
)

echo.
echo ===================================================
echo   Driver Ready!
echo   Zoom, Teams, Google Meet, Discord, NVIDIA Broadcast,
echo   and OBS will now detect 'Unity Video Capture' as a native webcam!
echo ===================================================
echo.
pause

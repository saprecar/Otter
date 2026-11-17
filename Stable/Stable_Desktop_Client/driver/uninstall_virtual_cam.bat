@echo off
setlocal
title Otter Virtual Camera Driver Uninstaller

echo ===================================================
echo   Otter - Standalone Virtual Camera Driver Removal
echo ===================================================
echo.

cd /d "%~dp0"

net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    powershell -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

echo Unregistering DirectShow Filter...
regsvr32 /u /s "%~dp0UnityCaptureFilter64.dll"
regsvr32 /u /s "%~dp0UnityCaptureFilter32.dll"

echo [SUCCESS] Virtual camera filter unregistered from Windows.
echo.
pause

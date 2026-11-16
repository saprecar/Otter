#!/usr/bin/env bash
# [AI-BLOCK: macOS Virtual Camera Setup Guide and Helper]

echo "==================================================="
echo "  Otter - macOS Virtual Camera Setup (CoreMediaIO)"
echo "==================================================="
echo ""

echo "On macOS (macOS 12 Monterey, macOS 13 Ventura, macOS 14 Sonoma, macOS 15+):"
echo "Apple enforces strict System Extension & DriverKit requirements for virtual webcams."
echo ""
echo "To make Otter detect directly as a camera in FaceTime, Zoom, Teams, and Photo Booth:"
echo "1. Native Hardware Mode (Android 14+):"
echo "   Plug your Android phone into your Mac via USB-C."
echo "   Select 'Use USB for' -> 'Webcam'."
echo "   Your Mac natively detects your phone as a standard UVC USB webcam without any drivers!"
echo ""
echo "2. Wireless / OBS Virtual Camera Driver (macOS):"
echo "   If using Wi-Fi streaming, install the official OBS Virtual Camera extension for macOS:"
echo "   brew install --cask obs"
echo "   Open OBS -> click 'Start Virtual Camera' (Registers 'OBS Virtual Camera' into macOS CoreMediaIO)."
echo ""
read -p "Press Enter to exit..."

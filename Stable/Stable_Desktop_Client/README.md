# Otter - Stable Desktop Client

Cross-platform virtual webcam receiver and remote controller for Android phone cameras.

## Requirements
- Python 3.8 or higher
- Windows 10/11, Ubuntu/Debian Linux, or macOS 11+

## Quick Launch
- **Windows**: Double-click `run_windows.bat`
- **Linux**: Run `./run_linux.sh` (or `bash run_linux.sh`)
- **macOS**: Double-click `run_macos.command` (or run `./run_macos.sh`)

## Manual Launch (Terminal)
```bash
pip install -r requirements.txt
python otter_app.py
```

## How It Works
1. Connect your Android phone to PC via USB cable (with USB Debugging ON) or ensure both are on the same Wi-Fi network.
2. Tap **Start Stream** on the Otter Android app.
3. Click **Connect & Start** on this controller.
4. Open OBS Studio, Discord, Google Meet, or Zoom and select **Otter Virtual Camera** (or **Unity Video Capture** / **OBS Virtual Camera**).

## Features
- Hardware H.264 video decoding with ultra-low latency
- Bidirectional Zoom (+/- buttons and smooth slider)
- Pro Camera Sliders: ISO, Shutter Speed, White Balance, Color FX (with Auto toggle interlocks)
- Quick Modes presets: Meetings, Online Class, Streaming, Snapshot, Scan/OCR, Security, Fun Filter, and Pro Reset
- Ultra Photo full-sensor still capture
- Dynamic resolution (up to 4K) and FPS detection (up to 60 FPS)
- Cross-platform virtual camera drivers (DirectShow shared memory, OBS bridge, v4l2loopback)

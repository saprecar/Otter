# Otter Desktop Client Release Notes (v1.5.0.0)

**Release Version**: `v1.5.0.0` (Desktop Client)  
**Compatible Mobile Builds**: Android Native App `v1.4.0.0` (versionCode 8) | Mobile Web Streamer (Zero-Install iOS & Android)  
**Release Archive**: `Stable_Desktop_Client v1.5.0.0.zip` (585 KB)

---

## What's New in Version 1.5.0.0

### 1. Universal Cross-Platform Web UI Controller
- **Zero GUI Driver & Rendering Issues**: Replaced the desktop Tkinter interface with a modern, responsive browser-based controller dashboard that eliminates blank viewfinders and missing buttons on Linux (X11 / Wayland) and macOS (Aqua / CoreGraphics).
- **Auto Safe Port Selection**: Automatically probes and allocates free ports starting at `8080`, strictly excluding privileged (<1024) and OS/system-reserved service ports (RPC, SMB, mDNS, databases) to prevent port conflicts even when services are temporarily idle.
- **Brave Browser Primary Default**: Automatically launches Brave Browser as the default browser per project policy, falling back smoothly to system default browsers.
- **Interactive Windows Launcher**: Added `run_web_ui_windows.bat` for transparent console launching, dependency validation, and live error reporting without accidental window termination.

### 2. Zero-Install Mobile Web Streamer (Apple iOS, iPadOS & Android)
- **Direct Browser Camera Streaming**: Turns **iPhones, iPads, and Android devices** into live PC webcams without installing native applications or requiring Apple Developer accounts:
  - **Apple iOS / iPadOS**: Safari on iPhone and iPad (iOS 11+).
  - **Android Devices**: Chrome, Brave, Samsung Internet, and Firefox.
- **Scannable QR Code & Live Address**: Generates an instant, client-rendered QR code and copyable LAN address directly on the desktop dashboard for one-second pairing.
- **Chrome Android Secure Context Diagnostic**:
  - Chrome on Android enforces strict Secure Context policies that disable `getUserMedia` over plain HTTP LAN IPs.
  - Added an in-page diagnosis banner with step-by-step instructions for allowing local origins via `chrome://flags/#unsafely-treat-insecure-origin-as-secure` or using natively secure USB ADB reverse (`adb reverse tcp:8080 tcp:8080`).

### 3. Dual-Input Virtual Camera Receiver & OBS Browser Source
- **Seamless Stream Multiplexing**: `cambridge_receiver.py` now supports both the native Android hardware H.264 stream and the browser HTML5 stream through `push_external_frame()` and `start_virtualcam_only()`.
- **OBS Studio Zero-Driver Support**: In addition to OS virtual camera drivers (`Unity Video Capture`, `OBS Virtual Camera`, and `v4l2loopback`), OBS Studio can ingest live video directly via a **Browser Source** pointing to the dynamic loopback URL:
  ```text
  http://localhost:<PORT>/mjpeg
  ```

---

## Quick Start Guide

### Launching the Desktop Client
1. Extract `Stable_Desktop_Client v1.5.0.0.zip`.
2. Launch the client:
   - **Windows**: Double-click `run_web_ui_windows.bat` (or `run_windows.bat` for classic mode).
   - **Linux**: Execute `./run_linux.sh` (or `./run_linux_silent.sh`).
   - **macOS**: Double-click `run_macos.command` (or execute `./run_macos.sh`).
3. The dashboard opens automatically in your browser.

### Connecting to Video Apps
- **Zoom / Microsoft Teams / Google Meet / Discord**:
  - In your application's **Settings > Video > Camera**, select:
    - **Windows**: `Unity Video Capture` or `OBS Virtual Camera`
    - **Linux**: `Otter Camera` or `/dev/video10`
    - **macOS**: `OBS Virtual Camera`
- **OBS Studio**:
  - Option A: Add a **Video Capture Device** and choose the virtual camera name above.
  - Option B: Add a **Browser Source**, copy the live MJPEG URL from the Otter dashboard (e.g. `http://localhost:8080/mjpeg`), and set resolution to `1280x720` or `1920x1080`.

---

## Checksums & Verification
- **Archive**: `Stable_Desktop_Client v1.5.0.0.zip`
- **Python Compatibility**: Python 3.8 to 3.13+
- **Open-Source License**: MIT License | Developer: `spacecar` | [Official Repository](https://github.com/saprecar/Otter)

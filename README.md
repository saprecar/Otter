# Otter - Virtual Webcam & Remote Control Suite

**Otter** is a lightweight, low-latency, 100% open-source virtual webcam suite that turns your Android device into a high-definition webcam for your PC (Windows, macOS, and Linux). Designed for content creators, remote workers, streamers, and privacy-conscious users.

- **Developer**: spacecar
- **Official GitHub Repository**: [https://github.com/saprecar/Otter](https://github.com/saprecar/Otter)
- **License**: MIT License (Permissive & Free to Use)

---

## What Does Otter Do?

Otter captures high-definition video directly from your Android phone's Camera2 hardware pipeline, encodes it with low-latency hardware H.264 (`MediaCodec`), and streams it to your PC over a USB cable (zero-latency ADB tunnel) or Wi-Fi local network.

On your computer, the Otter Desktop receiver broadcasts the stream into an OS-level virtual camera that functions seamlessly with:
- **OBS Studio & Streamlabs**
- **Discord**
- **Google Meet, Zoom & Microsoft Teams**
- **Web Browsers (Brave, Chrome, Firefox, Edge)**

---

## Key Features

1. **Dual Connection Modes**:
   - **USB Cable (ADB Auto-Tunnel)**: Recommended for zero-latency, rock-solid stability, and simultaneous phone charging. No root required.
   - **Wi-Fi (LAN IP)**: Wireless freedom across 2.4GHz / 5GHz home networks.
2. **Pro Optics & Remote Control**:
   - Bidirectional real-time control between phone and PC.
   - Front/Back lens switching with active lens indicator.
   - Instant mirror flip/deflip.
   - Digital zoom in/out up to sensor limits.
   - Continuous Auto Focus (AF) and Manual Focus (MF) with distance stepping (Infinity to Macro).
   - Real-time Exposure Value (EV) compensation.
   - Multi-resolution switching on the fly (1080p, 720p, 480p, 360p).
3. **Smart Lighting System**:
   - **Hardware Flashlight / Torch**: Rear camera torch with low/high brightness levels (Android 13+ strength control, disabled automatically on unsupported lenses).
   - **Front Screen Glow**: Front camera soft ring light with color temperatures (Warm, Daylight, Sunset, White) and automatic full-screen brightness boost.
4. **Anti-Kill Background Lock**:
   - Foreground service with `PARTIAL_WAKE_LOCK` for streaming with screen locked or turned off.
   - Built-in guidance for aggressive OEM battery savers (Xiaomi/MIUI/HyperOS, Samsung One UI, ColorOS, OxygenOS, FuntouchOS).
5. **Cross-Platform PC Controller**:
   - Dark-mode GUI written with pure Python `tkinter` (zero external GUI library dependencies to launch).
   - One-click launchers for Windows (`run_windows.bat`), macOS (`run_macos.sh`, `run_macos.command`), and Linux (`run_linux.sh`).
   - Built-in dependency installer & uninstaller.

---

## Quick Start & Installation

### Step 1: Install Android App (`app-debug.apk`)
1. Download `app-debug.apk` from the [Releases](https://github.com/saprecar/Otter/releases) page.
2. On your Android phone, enable **Install unknown apps** for your file manager or browser.
3. Install the APK and launch Otter.
4. Grant the camera permission when prompted.

### Step 2: Run Otter Desktop on PC

#### Windows
Double-click `run_windows.bat`.

#### Linux
Open terminal and run:
```bash
chmod +x run_linux.sh
./run_linux.sh
```

#### macOS
Double-click `run_macos.command` or run:
```bash
chmod +x run_macos.sh
./run_macos.sh
```

*Note: The launcher automatically detects your Python environment and opens the Otter Controller.*

---

## How to Connect: USB vs Wi-Fi

### Method A: USB Cable (Recommended for 0-Latency)
1. **Enable Developer Options**: Go to phone **Settings** -> **About Phone** -> tap **Build Number** 7 times.
2. **Enable USB Debugging**: In **Settings** -> **Developer Options**, turn ON **USB Debugging**.
3. **Plug in USB Cable**: Connect your phone to your PC with a USB data cable.
4. **Authorize**: Check "Always allow from this computer" and tap **OK**.
5. **Start Stream**:
   - On Phone: Tap **Start**.
   - On PC: Keep **USB (ADB Auto-Tunnel)** selected and click **Connect & Start**.

### Method B: Wi-Fi (Wireless Mode)
1. Ensure both phone and PC are connected to the same Wi-Fi network.
2. Open Otter on your phone; note the IP address shown (e.g. `192.168.1.50`).
3. Tap **Start** on your phone.
4. On PC, select **Wi-Fi (LAN IP)**, enter the IP, and click **Connect & Start**.

---

## Permissions & Full Transparency

Otter requires minimal Android permissions, strictly for virtual webcam functionality:

| Permission | Purpose | Why It Is Needed |
| :--- | :--- | :--- |
| `android.permission.CAMERA` | Camera Access | Captures live video stream from front and rear sensors. |
| `android.permission.INTERNET` | Local Network Socket | Streams H.264 video and control commands over local TCP ports (8089/8090). No data leaves your local network. |
| `android.permission.ACCESS_WIFI_STATE` | Wi-Fi IP Query | Detects and displays your local IP address for easy Wi-Fi pairing. |
| `android.permission.FOREGROUND_SERVICE` | Background Streaming | Keeps video encoder running when phone screen is turned off or locked. |
| `android.permission.FOREGROUND_SERVICE_CAMERA` | Android 14+ Compliance | Required by Android 14+ for foreground camera streaming. |
| `android.permission.WAKE_LOCK` | CPU Sleep Prevention | Prevents the operating system CPU from sleeping during a live meeting or stream. |
| `android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` | Battery Saver Exemption | Allows user to whitelist Otter from aggressive OEM task killers. |

### Privacy & Data Safety
- **Zero Cloud Servers**: Video is transmitted strictly point-to-point (P2P) between your phone and your PC over local USB or local Wi-Fi.
- **Zero Analytics / Telemetry**: No tracking, no crash telemetry, and no outbound web requests.
- **Zero Account Required**: No logins, no signups, no subscriptions.

---

## Python Desktop Dependencies

Otter Desktop utilizes standard, open-source Python packages:
- `opencv-python` (BSD License): Video frame decoding and processing.
- `numpy` (BSD License): Fast numerical array manipulation.
- `pyvirtualcam` (MIT License): Cross-platform virtual camera loopback driver interface.

### Automatic / Manual Management
Install via controller UI tab **Dependencies & OEM Fix**, or via terminal:
```bash
pip install -r Dev/desktop/requirements.txt
```
To uninstall completely:
```bash
pip uninstall -y opencv-python numpy pyvirtualcam
```

---

## Risk Disclaimer & Liability Notice

This software is distributed under the MIT License on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
- Neither developer **spacecar** nor the Otter project is liable for any hardware damage, data loss, dependency conflicts, or system disruptions.
- Users are encouraged to inspect source code and configure settings according to their system capabilities.

---

## License & Attribution

```text
MIT License

Copyright (c) 2026 spacecar (https://github.com/saprecar/Otter)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

Attribution Requirement:
If code, algorithms, or assets from Otter are integrated or reused in other applications,
proper attribution must be provided citing the application name ('Otter'), the official
repository (https://github.com/saprecar/Otter), and the original developer ('spacecar').
```

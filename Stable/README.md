# Otter Stable Release (v1.4.0.0)

Production-ready release packages for the Otter Virtual Camera and Remote Controller System, separated into dedicated distributions for Google Play Store compliance, GitHub / Sideloading, and Desktop Clients.

---

## 1. Directory Structure

```text
Stable/
├── GUIDEBOOK.md                      # Complete operational guidebook and architecture reference
├── Stable_Desktop_Client/            # Standalone desktop controller (Windows, macOS, Linux)
│   ├── driver/                       # DirectShow virtual webcam drivers and bridges
│   ├── wallpapers/                   # Default virtual background studio backdrops
│   ├── otter_app.py                  # Main desktop GUI (Dual Virtual BG, Screen Wake, Pro controls)
│   ├── cambridge_control.py          # Camera2 remote control TCP client (port 8090)
│   ├── cambridge_receiver.py         # Real-time H.264 video decoder with 2.5s socket timeout
│   ├── manage_adb.py                 # Portable Google ADB minimal tools manager
│   ├── manage_dependencies.py        # Auto-dependency installer
│   ├── network_discovery.py          # LAN camera discovery
│   ├── requirements.txt              # Python dependencies
│   ├── run_windows_silent.vbs        # 1-click Silent Windows launcher (No terminal window)
│   ├── run_windows.bat               # 1-click Windows launcher (With debug console)
│   ├── run_linux_silent.sh           # 1-click Silent Linux launcher
│   ├── run_linux.sh                  # 1-click Linux terminal launcher
│   ├── run_macos_silent.command      # 1-click Silent macOS launcher
│   ├── run_macos.command             # 1-click macOS launcher
│   ├── run_macos.sh                  # Terminal macOS launcher
│   └── README.md                     # Desktop client guide
│
├── stable_playstore_version/         # Google Play Store Distribution Package
│   ├── app/                          # Android source tree (Target SDK 36, minSdk 24, versionCode 8, versionName 1.4.0.0)
│   ├── gradle/                       # Gradle wrapper
│   ├── playstore_icon_512x512.png    # 512x512 official Play Store app icon
│   ├── playstore_feature_graphic*    # 1024x500 Feature Graphic (PNG & JPEG)
│   ├── playstore_tablet_10inch_*     # Eight 1920x1080 10-inch tablet screenshots
│   ├── STORE_LISTING.md              # Multi-language store listings (en-US, hi-IN, es-ES)
│   ├── store_listing_translations.csv# Google Play auto-detection translation file
│   └── README.md                     # Google Play build and submission guide
│
└── stable_non_playstore_version/     # GitHub / Sideload Distribution Package
    ├── app/                          # Android source tree (Target SDK 36, minSdk 21 Android 5.0+, versionCode 8, versionName 1.4.0.0)
    ├── gradle/                       # Gradle wrapper
    ├── org.understory.cambridge.yml  # Official F-Droid metadata build recipe
    ├── FDROID_SUBMISSION_GUIDE.md    # F-Droid & IzzyOnDroid submission guide
    └── README.md                     # Sideload installation & custom signing guide
```

All legal policies, terms of service, user agreements, and Google Play Data Safety declarations are consolidated in the universal [`Policies And Agreement/`](../Policies%20And%20Agreement/) folder.

---

## 2. Quick Start

### A. Desktop Client Launchers
Launchers automatically create an isolated Python virtual environment (`.venv`) and install all dependencies on first launch:
- **Windows Silent (Clean GUI)**: Double-click `run_windows_silent.vbs` (Terminal is completely hidden).
- **Windows Console (Debug / Logs)**: Double-click `run_windows.bat` (Console window shows real-time stream logs; do not be alarmed by the black terminal).
- **Linux**: Execute `./run_linux_silent.sh` or `./run_linux.sh` (If Tkinter is missing on Ubuntu/Debian: `sudo apt install python3-tk`).
- **macOS**: Double-click `run_macos_silent.command` or `run_macos.command` (If Tkinter is missing: `brew install python-tk`).

### B. Python Setup & Manual Commands (If Auto-Install Fails)
1. Download installer from https://www.python.org/downloads/
2. **Crucial**: Check **"Add python.exe to PATH"** on the first installation screen.
3. Click "Install Now".
4. **Internet Requirement**: An active internet connection is strictly required **only during initial setup / pip install** to download libraries. Once installed, Otter runs 100% offline.

#### Copy-Paste Installation Commands:
- **Windows**:
  ```cmd
  pip install opencv-python numpy pyvirtualcam imageio-ffmpeg
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update && sudo apt install -y python3 python3-pip python3-tk python3-venv v4l2loopback-dkms
  pip3 install opencv-python numpy pyvirtualcam imageio-ffmpeg
  ```
- **Linux (Fedora)**:
  ```bash
  sudo dnf install -y python3 python3-pip python3-tkinter v4l2loopback
  pip3 install opencv-python numpy pyvirtualcam imageio-ffmpeg
  ```
- **macOS**:
  ```bash
  brew install python python-tk && pip3 install opencv-python numpy pyvirtualcam imageio-ffmpeg
  ```

### C. Connection Modes (No Root Required)
1. **USB Tethering (No ADB - Recommended)**: Enable USB Tethering on phone, select `USB Tethering` in desktop app (auto-detects gateway), and click `Connect & Start`.
2. **USB (ADB Tunnel)**: Enable USB Debugging in Developer Options for classic zero-latency port forwarding (`127.0.0.1`).
3. **Wi-Fi (LAN IP)**: Wireless P2P streaming over your local network.
4. **Auto (USB -> Wi-Fi)**: Automatically probes for USB first and falls back to Wi-Fi.

### D. Play Protect & Android Version Support
- **Non-Play Store Sideload**: Supports Android 5.0 (API 21) to Android 16+. When sideloading APK, Play Protect may prompt to scan — users can safely scan or select "Install without scanning" / "Install anyway".
- **Play Store Version**: Supports Android 7.0 (API 24) to Android 16+.

### E. Troubleshooting Blocks
- **VPN**: Pause VPN or allow local network traffic / split-tunneling.
- **Firewall / Defender**: Allow Python/Otter on Private networks (TCP ports 8089 and 8090).
- **UI Lag**: Brief 1-2 second pause during initial connection or lens switch is normal while encoder keyframes synchronize.

### F. Gaming Consoles & Handheld Devices Setup
- **Handheld PC Gaming Devices (Desktop OS)**: Directly supported in Desktop Mode using `run_linux.sh` or `run_windows.bat`.
- **Dedicated Gaming Consoles (Proprietary Systems)**: Consoles require hardware USB Video Class (UVC) signals. Route your Otter video from PC into your console using a standard generic USB video capture card (PC HDMI Output -> Capture Card HDMI Input -> Capture Card USB plugged into Console).

---

## 3. Legal and Policy Disclaimers (Indian Law)
- **Local Peer-to-Peer Operation**: Otter does not operate cloud servers. All video and RPC controls remain on the user's local network (USB ADB or local Wi-Fi). Zero developer data retention.
- **Data Deletion & Liability**: The developer retains zero user data, so server deletion is not applicable. The developer holds zero liability for local network packet loss, interception, or software bugs.
- **Mandatory Attribution**: All reuse or forks must credit original developer **spacecar**, name the project **Otter**, and link to **https://github.com/saprecar/Otter**.
- **Governing Law**: Republic of India (Information Technology Act, 2000 & Indian Contract Act, 1872).
- **Exclusive Jurisdiction**: Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005).
- **Contact**: **getspacecar@gmail.com** (Mandatory subject line: `[Otter-Legal]` or `[Otter-Inquiry]`).
